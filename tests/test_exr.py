#-*- coding: utf-8 -*-
import os
import sys

import pytest

"""
The tests are ment to work with Python 2 and Python 3.
Please remember that Python 2 works with byte strings as default
and with the change of Python 3 unicode strings are used.

Python 2 default string
foo = b'bar'

Python 3 default string:
foo = u'bar'
"""

# Append the required module
sys.path.append(
    os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'src'))

import parse_metadata

EXR_IMAGES_DIR_PATH = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), 'openexr-images')


REC709_TEST_IMAGE_PATH = os.path.join(EXR_IMAGES_DIR_PATH,
                                      'Chromaticities', 'Rec709.exr')

def test_oserror_thrown_if_file_does_not_exist():
    with pytest.raises(OSError):
        parse_metadata.read_exr_header('pippo.exr')

@pytest.mark.parametrize("input_path,expected_lineorder", [
    pytest.param(REC709_TEST_IMAGE_PATH, 'INCREASING_Y')
])
def test_exr_meta_lineOrder(input_path, expected_lineorder):
    metadata = parse_metadata.read_exr_header(input_path)
    assert metadata['lineOrder'] == expected_lineorder

@pytest.mark.parametrize("input_path,expected_compression", [
    pytest.param(REC709_TEST_IMAGE_PATH, 'PIZ_COMPRESSION'),
    pytest.param(os.path.join(EXR_IMAGES_DIR_PATH, 'Chromaticities', 'XYZ.exr'), 'PIZ_COMPRESSION'),
    pytest.param(os.path.join(EXR_IMAGES_DIR_PATH, 'Chromaticities', 'XYZ_YC.exr'), 'PIZ_COMPRESSION'),
    pytest.param(os.path.join(EXR_IMAGES_DIR_PATH, 'TestImages', 'GammaChart.exr'), 'PXR24_COMPRESSION'),
    pytest.param(os.path.join(EXR_IMAGES_DIR_PATH, 'TestImages', 'BrightRings.exr'), 'ZIP_COMPRESSION'),
    pytest.param(os.path.join(EXR_IMAGES_DIR_PATH, 'TestImages', 'SquaresSwirls.exr'), 'PXR24_COMPRESSION'),
])
def test_exr_meta_compression(input_path,expected_compression):
    metadata = parse_metadata.read_exr_header(input_path)
    assert metadata['compression'] == expected_compression

def test_exr_meta_pixelAspectRatio():
    metadata = parse_metadata.read_exr_header(REC709_TEST_IMAGE_PATH)
    assert metadata['pixelAspectRatio'] == 1

def test_exr_meta_owner():
    metadata = parse_metadata.read_exr_header(REC709_TEST_IMAGE_PATH)
    assert metadata['owner'] == 'Copyright 2006 Industrial Light & Magic'

@pytest.mark.parametrize("input_path,expected_metadata", [
    # Rec709.exr
    pytest.param(REC709_TEST_IMAGE_PATH, {
        'compression': 'PIZ_COMPRESSION',
        'pixelAspectRatio': 1.0,
        'displayWindow': {
            'xMin': 0,
            'yMin': 0,
            'yMax': 405,
            'xMax': 609
        },
        'channels': {
            'R': {
                'reserved': [0, 0, 0],
                'pLinear': 0,
                'pixel_type': 1,
                'xSampling': 1,
                'ySampling': 1
            },
            'B': {
                'reserved': [0, 0, 0],
                'pLinear': 0,
                'pixel_type': 1,
                'xSampling': 1,
                'ySampling': 1
            },
            'G': {
                'reserved': [0, 0, 0],
                'pLinear': 0,
                'pixel_type': 1,
                'xSampling': 1,
                'ySampling': 1
            }
        },
        'dataWindow': {
            'xMin': 0,
            'yMin': 0,
            'yMax': 405,
            'xMax': 609
        },
        'screenWindowCenter': [0.0, 0.0],
        'owner': 'Copyright 2006 Industrial Light & Magic',
        'screenWindowWidth': 1.0,
        'lineOrder': 'INCREASING_Y'
    })
])
def test_exr_meta_all(input_path, expected_metadata):
    result = parse_metadata.read_exr_header(input_path)
    assert result == expected_metadata
