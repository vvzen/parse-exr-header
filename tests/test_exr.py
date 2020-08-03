#-*- coding: utf-8 -*-
import pytest
import sys
import os

"""
The tests work with Python 2 and Python 3.
Please remember that Python 2 works with byte strings as default
and with the change of Python 3 unicode strings are used.

Python 2 default string
foo = b'bar'

Python 3 default string:
foo = u'bar'
"""

# Append the required module
# Not the best way but it works in Python 2.7
sys.path.append(
    os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'src'))

import parse_metadata

EXR_IMAGES_DIR_PATH = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), 'openexr-images')


class TestEXRParsing:

    rec709_test_image_path = os.path.join(EXR_IMAGES_DIR_PATH, 'Chromaticities',
                                          'Rec709.exr')

    def test_oserror_thrown_if_file_does_not_exist(self):

        exr_path = 'pippo.exr'

        with pytest.raises(OSError):
            parse_metadata.read_exr_header(exr_path)

    def test_exr_meta_lineOrder(self):

        metadata = parse_metadata.read_exr_header(self.rec709_test_image_path)
        assert metadata['lineOrder'] == 'INCREASING_Y'

    def test_exr_meta_compression(self):

        metadata = parse_metadata.read_exr_header(self.rec709_test_image_path)
        assert metadata['compression'] == 'PIZ_COMPRESSION'

    def test_exr_meta_pixelAspectRatio(self):

        metadata = parse_metadata.read_exr_header(self.rec709_test_image_path)
        assert metadata['pixelAspectRatio'] == 1

    def test_exr_meta_owner(self):

        metadata = parse_metadata.read_exr_header(self.rec709_test_image_path)
        assert metadata['owner'] == 'Copyright 2006 Industrial Light & Magic'

    def test_exr_meta_all(self):
        expected = {
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
                    'pLinear': (0, ),
                    'pixel_type': (1, ),
                    'xSampling': (1, ),
                    'ySampling': (1, )
                },
                'B': {
                    'reserved': [0, 0, 0],
                    'pLinear': (0, ),
                    'pixel_type': (1, ),
                    'xSampling': (1, ),
                    'ySampling': (1, )
                },
                'G': {
                    'reserved': [0, 0, 0],
                    'pLinear': (0, ),
                    'pixel_type': (1, ),
                    'xSampling': (1, ),
                    'ySampling': (1, )
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
        }

        result = parse_metadata.read_exr_header(self.rec709_test_image_path)
        assert result == expected
