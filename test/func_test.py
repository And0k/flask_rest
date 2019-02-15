#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
  Purpose:  functional tests
  Author:   Andrey Korzh <ao.korzh@gmail.com>
  Created:  25.01.2019
"""
import pytest
from flask import url_for
from PIL import Image
from io import BytesIO
from pathlib import Path

url_images = ["https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_272x92dp.png",
              "http://flask.pocoo.org/docs/1.0/_images/logo-full.png"]  # if copy to json use _"_ not _'_
len_hex_uuid4 = 32
tmp_dir_name = f'{"~test_id_to_delete~":~<{len_hex_uuid4}}'

#@pytest.mark.skip(reason="not now")
def test_post_task(client, tmp_processed_dir_path, list_result_dirs):
    """
    http post: send urls for processing
    check: images from urls are processed and saved in new folder named with generated GUID which is returned
    :param client: fixture, injected by the `pytest-flask` plugin
    :param tmp_processed_dir_path: fixture, using it ensures we have new temporary dir
    :return:
    """

    # query
    n_urls = len(url_images)
    response = client.post("/", json = {'url_list': url_images, 'threshold': 150})

    # Was 1 dir created?
    assert len(list_result_dirs()) == 1

    # Was it filled with files number equal number of queried urls?
    assert len([1 for _ in list_result_dirs()[0].iterdir()]) == n_urls

    # Validate the response
    assert response.status_code == 201
    assert response.json == {
        'guid': list_result_dirs()[0].name,
        'processed_cnt': n_urls
    }


@pytest.fixture
def guids(list_result_dirs):
    """
    work folders from file system (autonamed folders has guid names)
    :param list_result_dirs: fixture
    :return:
    """
    ids = [d.name for d in list_result_dirs()]
    assert len(ids)>0  # test folder prepared?
    return ids


@pytest.mark.parametrize('url', ['', '/', '/index', '/index/'])
def test_get_json_ids_list(client, url, processed_dir_path_with_guids, guids):
    """
    http get main page (correspond to any of 4 parametrized urls)
    receive same list of work folders in json
    :param client: fixture, injected by the `pytest-flask` plugin
    :param processed_dir_path_with_guids: fixture, using it ensures we have prepared dir (where exist folders are guids)
    :return:
    """
    print(f'get folders from "{str(processed_dir_path_with_guids)}" for url "{url}"')
    response = client.get(url)
    # receive json with work ids?
    assert response.status_code == 200
    assert response.json == {'guids': guids}


id = '5e0ca894f29d4395ba234e1fe865ecea'  # folder we check, must be in _data/in_ folder
i_file = 1   #index of file we check


def test_get_json_files_list(client, app, list_result_dirs, processed_dir_path_with_guids, testdata_dir, guids):
    """
    http get _address of urls list_ of (processed) files for one of ids
    receive list with contents of corresponding folder given by urls relative to address for Config['PROCESSED_DIR_PATH']
    :param processed_dir_path_with_guids: fixture, using it ensures we have prepared dir (where exist folders are guids)
    :param guids: work folders red from file system
    :global param: id
    """

    url = f"/{id}"
    print(f'get folders from "{str(processed_dir_path_with_guids)}" for url "{url}"')
    response = client.get(url)
    assert response.status_code == 200
    # receive json with urls of result files?
    assert response.json == {
        'files': [url_for('static', filename=str(file.relative_to(app.config['PROCESSED_DIR_PATH']))) for file in \
                  Path(testdata_dir('guids_in') / id).iterdir()
                  ]
    }


def test_get_file(client, app, processed_dir_path_with_guids):
    """
    http get address of 1 (processed) file for one of ids
    receive 1 file of Config['PROCESSED_IMAGE_FORMAT'] format
    :param processed_dir_path_with_guids: fixture, using it ensures we have prepared dir (where exist folders are guids)
    :global param: id, i_file
    """
    response = client.get(f"/{id}/{i_file}.{app.config['PROCESSED_IMAGE_FORMAT']}/")
    assert response.status_code == 200
    img = Image.open(BytesIO(response.data))
    assert img.format == app.config['PROCESSED_IMAGE_FORMAT'].upper()


@pytest.fixture(params=range(4), ids= ['""', '/', '/guid', '/guid/file']) #
def query_urls(request, app):
    check_urls = ['',
                  '/',
                  f'/{id}',
                  f"/{id}/{i_file}.{app.config['PROCESSED_IMAGE_FORMAT']}"]
    response_contains = [
        id,
        id,
        f"/{id}/{i_file}.{app.config['PROCESSED_IMAGE_FORMAT']}",
        'PNG']
    return ((check_urls[request.param], response_contains[request.param]),)


def test_get_html(client, app, query_urls, processed_dir_path_with_guids):
    """
    Check content negotiation. Http get queries with {'Accept': 'text/html'}
    receive from {'Accept': 'text/html'} queries has html result
    :param processed_dir_path_with_guids: fixture, using it ensures we have prepared dir (where exist folders are guids)
    :return:
    """
    url, response_contains = query_urls[0]
    headers = 'text/html'  # 'headers', ['text/html']
    response = client.get(url, headers={'Accept': headers})
    assert response_contains.encode() in response.data
    if url.strip('/').endswith(app.config['PROCESSED_IMAGE_FORMAT']):
        assert response.mimetype.startswith('image')
    else:
        assert response.mimetype == headers


def test_delete(client, tmp_processed_dir_path, list_result_dirs):
    """

    :param client:
    :param tmp_processed_dir_path: fixture, using it ensures we have new temporary dir
    :return:
    """
    # make some dir inside temorary dir and write file
    new_dir = tmp_processed_dir_path / tmp_dir_name
    new_dir.mkdir()
    (new_dir / 'somefile').touch()
    # Was 1 dir created?
    assert len(list_result_dirs()) == 1

    # query to delete dir
    response = client.delete(f"/{new_dir.name}")

    # Was dir deleted?
    assert len(list_result_dirs()) == 0

    # Validate the response
    assert response.status_code == 204
    # assert response.json == {
    #     'guid': list_result_dirs()[0].name,
    #     'processed_cnt': 2
    # }
    pass

def test_update_task(client, tmp_processed_dir_path, list_result_dirs):
    """
    http post: send urls for processing
    check: images from urls are processed and saved in new folder named with generated GUID which is returned
    :param client: fixture, injected by the `pytest-flask` plugin
    :param tmp_processed_dir_path: fixture, using it ensures we have new temporary dir
    :return:
    """

    # make some dir inside temorary dir and write file
    new_dir = (tmp_processed_dir_path / tmp_dir_name)
    new_dir.mkdir()
    (new_dir / 'somefile').touch()
    # Was 1 dir created?
    assert len(list_result_dirs()) == 1

    # query to update dir
    n_urls = len(url_images)
    response = client.put(f"/{new_dir.name}", json = {'url_list': url_images, 'threshold': 150})

    # same dir exists?
    assert list_result_dirs()[0] == new_dir

    # Was it filled with files number equal number of queried urls?
    assert len([1 for _ in list_result_dirs()[0].iterdir()]) == n_urls

    # Validate the response
    assert response.status_code == 201
    assert response.json == {
        'guid': list_result_dirs()[0].name,
        'processed_cnt': n_urls
    }


@pytest.mark.skip(reason="run only if need print your API as a Postman")
def postman_helper(app):
    from flask import json
    urlvars = False     # Build query strings in URLs
    swagger = True      # Export Swagger specifications
    data = app.as_postman(urlvars=urlvars, swagger=swagger)
    print(json.dumps(data))