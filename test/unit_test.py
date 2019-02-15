#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
  Purpose:  unit tests
  Author:   Andrey Korzh <ao.korzh@gmail.com>
  Created:  25.01.2019
"""
import pytest
from PIL import Image
from distutils.dir_util import copy_tree
from service_images.models import ApiError, process_image, request_file


url_image = 'https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_272x92dp.png'

#@pytest.mark.skip(reason="tested long")


def test_process_image(tmp_processed_dir_path, testdata_dir):
    """
    Convert images of different formats from directory "images_in" with two thresholds and save
    result in directory "images_out" (also for the visual inspection)
    """

    # test: filling dir with results
    i = 0
    for i, image in enumerate(testdata_dir('images_in').iterdir(), start=1):
        for thr in [50.5, 200]:
                process_image(image, out_name=tmp_processed_dir_path.joinpath(f'{i}_{int(thr)}.png'), threshold=thr)

    assert i > 1  # we have processed some files

    # copy images from tmp_processed_dir_path to testdata_dir('images_out') for visual inspect
    files_list = copy_tree(str(tmp_processed_dir_path), str(testdata_dir('images_out')))

    # or count files
    # def list_result_files():
    #     return [f for f in tmp_processed_dir_path.iterdir() if not f.is_dir()]
    # files_list = list_result_files()
    assert len(files_list) == i*2  # we have two result files for each input file
    # tmp_processed_dir_path.replace(testdata_dir('images_out'))  #


def test_request_file():
    """downloading image"""
    url = url_image
    file_obj = request_file(url)
    img = Image.open(file_obj)
    assert img.format==url[-3:].upper()


@pytest.mark.parametrize('url', [
    'https://httpbin.org/status/404',   # will generate an HTTPError
    'https://no-such-server.org']       # will generate an URLError
                        )
def test_request_file_HTTPError(url):
    """exceptions on bad urls"""
    with pytest.raises(ApiError):
        file = request_file(url)


