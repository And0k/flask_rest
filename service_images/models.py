import uuid, logging
from pathlib import Path
from io import BytesIO
import requests
from PIL import Image
from .common import ApiError
from flask import current_app as app
logger = logging.getLogger('flask.app')


def remove_transparency(im, bg_colour=(255, 255, 255)):
    """
    Remove transparency/alpha from PIL.Image
    https://stackoverflow.com/a/35859141
    :param im: PIL.Image
    :param bg_colour: tuple (R, G, B), background color will be used instead transparency
    :return:
    """
    # Only process if image has transparency (http://stackoverflow.com/a/1963146)
    if im.mode in ('RGBA', 'LA') or (im.mode == 'P' and 'transparency' in im.info):

        # Need to convert to RGBA if LA format due to a bug in PIL (http://stackoverflow.com/a/1963146)
        alpha = im.convert('RGBA').split()[-1]

        # Create a new background image of our matt color.
        # Must be RGBA because paste requires both images have the same format
        # (http://stackoverflow.com/a/8720632  and  http://stackoverflow.com/a/9459208)
        bg = Image.new("RGBA", im.size, bg_colour + (255,))
        bg.paste(im, mask=alpha)
        return bg
    else:
        return im


def process_image(file, out_name=None, threshold=200):
    """
    Converts image to black and white with given threshold
    :param out_name: pathlib.Path, name of result image file
    :param file: [str, :class:pathlib.Path] - filename to read image or
                 file object (see PIL.open())
    :param threshold: int or float, in range 0..255. If higher then result will blacker
    :return: None
    """
    if not file:
        return
    try:
        img_in = Image.open(file)
        img_in = remove_transparency(img_in)
        # convert to 8-bit pixels, black and white, with given threshold
        img_out = img_in.convert('L').point(lambda x: 255 if x > threshold else 0, mode='1')
        img_out.save(out_name)
    except Exception as err:
        raise Exception('Processing image error.') from err


def request_file(url):
    """
    http get url with timeouts, mimic header of Mozilla browser
    :param url:
    :return: file object
    """
    connect_timeout = 5
    read_timeout = 50
    headers = {
        'User-Agent': 'Mozilla/5.0'}  # may add more info: (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36
    try:
        response = requests.get(url, headers=headers, timeout=(connect_timeout, read_timeout))
        response.raise_for_status()
    except Exception as err:  # (requests.HTTPError, requests.Timeout, ConnectionError)
        raise ApiError(str(err), details='Get image error')
    return BytesIO(response.content)


class WorkDAO(object):
    """
    Required app.config fields:
    PROCESSED_DIR_PATH
    PROCESSED_IMAGE_FORMAT
    """
    def __init__(self):
        if app.config['PROCESSED_DIR_PATH'].is_dir():
            pass  # self.ids = {d.name for d in self.list_ids()}
        else:
            app.config['PROCESSED_DIR_PATH'].mkdir(parents=True)

            # self.ids = set()  # set of str, folder names, maintained here in sync with existed folders in app.config['PROCESSED_DIR_PATH']

    def get(self, id):
        """
        Find folder with result of previous work.
        :param id: str
        :return: list of pathlib.Path, contents of folder
        Allows to not maintain folder list in memory/database
        """
        return self.find_work_dir(id).iterdir()

    def get_item(self, id, item):
        """
        :param id: str
        :param item: str
        :return: :class:`pathlib.Path` to file in dir
        """
        file = self.find_work_dir(id) / item
        return file

    def create(self, url_list, threshold, id=None):
        """
        Process all images links, saves to result dir and returns its name
        :param url_list: task data
        :param threshold: task parameter
        :param id: None to generate unique work id or str to create folder with this name
        :return:
        """
        if not id:
            # generate unique work id
            id = uuid.uuid4().hex  # will use hex representation of generated
        work_dir = app.config['PROCESSED_DIR_PATH'] / id
        try:
            work_dir.mkdir(exist_ok=True)
            processed_cnt = 0
            for i, url in enumerate(url_list):
                try:
                    file_obj = request_file(url)
                    process_image(file_obj, out_name=work_dir / f"{i}.{app.config['PROCESSED_IMAGE_FORMAT']}", threshold=threshold)
                    processed_cnt += 1
                except Exception as err:
                    logger.warning(f'{err} #{i} {url} failed')
            return {'guid': id, 'processed_cnt': processed_cnt}  # 'Images processed'
        except Exception as err:
            if Path.is_dir(work_dir):  # remove not completed work result
                Path.rmdir(work_dir)
            ApiError(str(err), f'Data not processed', 404)

    def update(self, id, url_list, threshold):
        self.delete(id)
        return self.create(url_list, threshold, id)

    def delete(self, id):
        """
        remove dir of id
        :param id: str
        :return:
        """

        dir = app.config['PROCESSED_DIR_PATH'] / id
        # remove all files from dir (required to can remove dir itself)
        for file in dir.iterdir():
            file.unlink()
        dir.rmdir()
        return dir.name

    def find_work_dir(self, id):
        """
        path to dir of id
        :param id: str, work id
        :return: pathlib.Path to dir
        """
        try:
            return app.config['PROCESSED_DIR_PATH'] / id
        except Exception as err:
            ApiError(str(err), f'Have no saved data with id {id}', 404)

    def list_ids(self):
        return [d.name for d in app.config['PROCESSED_DIR_PATH'].iterdir() if d.is_dir()]

