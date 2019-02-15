import pytest
from .config import Config
from ..service_images import create_app


#@pytest.fixture(scope='module')
# def create_app():
#     return a  # loads test config


@pytest.fixture(scope='module')
def app():
    """
    fixture whose name is "app"
    Adds config parameters for test
    :return: flask server instance
    """

    a = create_app(Config)
    #from ..service_images import apis
    return a


@pytest.fixture(scope='module')
def testdata_dir(app):
    """
    Info about data dirs for test
    :param parent_path: :class:`pathlib.Path`, parent dir of test data
    :return: function turned to dict value if used in test
    """
    # if not guid in {dir.name for dir in list_result_dirs()}:  # prepared?
    #     guid = list_result_dirs()[0].name
    #     print('Selected 1st dir as guid')

    test_data_dir_dict = {
        'images_in': app.config['TEST_PATH'] / 'data' / 'in' / 'images_in',
        'guids_in': app.config['TEST_PATH'] / 'data' / 'in',
        'images_out': app.config['TEST_PATH'] / 'data' / 'images_out'

    }

    def dict_value(key):
        return test_data_dir_dict[key]

    return dict_value


@pytest.fixture
def processed_dir_path_with_guids(testdata_dir, app):
    """
    Temporary point app.config['PROCESSED_DIR_PATH'] to test_data_dir_dict['guids_in']
    :param app:
    :return: app.config['PROCESSED_DIR_PATH']
    """

    save_path = app.config['PROCESSED_DIR_PATH']
    app.config['PROCESSED_DIR_PATH'] = testdata_dir('guids_in')
    yield testdata_dir('guids_in')
    app.config['PROCESSED_DIR_PATH'] = save_path


@pytest.fixture
def tmp_processed_dir_path(tmp_path, app):
    """
    Temporary make new temporary dir for app processing results and point app.config['PROCESSED_DIR_PATH'] to it
    :param tmp_path:
    :param app:
    :return:
    """
    save_path = app.config['PROCESSED_DIR_PATH']
    app.config['PROCESSED_DIR_PATH'] = tmp_path
    yield tmp_path
    app.config['PROCESSED_DIR_PATH'] = save_path


@pytest.fixture  #(scope='module')
def list_result_dirs(app):
    def list_result_dirs_func():
        return [d for d in app.config['PROCESSED_DIR_PATH'].iterdir() if d.is_dir()]
    return list_result_dirs_func
    # return [d for d in app.config['PROCESSED_DIR_PATH'].iterdir() if d.is_dir()]
    # def list_result_dirs_func(dir=(Path(dir) if dir else tmp_path)):
    #     return [d for d in dir.iterdir() if d.is_dir()]
    # return list_result_dirs_func




# @pytest.fixture
# def rem_dir_contents(dir):
#     # prepare (i.e. empty) result dir from subdirs
#     for d in list_result_dirs(dir):
#         # remove all files from dir and then dir itself
#         for file in d.iterdir():
#             file.unlink()
#         d.rmdir()
#     assert len(list_result_dirs(dir)) == 0  # prepared?


def pytest_report_header(config):
    return "mailto: ao.korzh@gmail.com"