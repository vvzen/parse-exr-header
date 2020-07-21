#-*- coding: utf-8 -*-
import os
import sys
import subprocess
import struct

import logging

logger = logging.getLogger('vvzen.parse_metadata')


class EXR_ATTRIBUTES:
    COMPRESSION_VALUES = (u'NO_COMPRESSION', u'RLE_COMPRESSION',
                          u'ZIPS_COMPRESSION', u'ZIP_COMPRESSION',
                          u'PIZ_COMPRESSION', u'PXR24_COMPRESSION',
                          u'B44_COMPRESSION', u'B44A_COMPRESSION')

    LINE_ORDER = (u'INCREASING_Y', u'DECREASING_Y', u'RANDOM_Y')

    ENVMAP_TYPES = (u'ENVMAP_LATLONG', u'ENVMAP_CUBE')


def read_until_null(filebuffer, maxbytes=1024):
    """Reads a file until a null character

    Args:
        filebuffer (obj): a file that was opened with open()
        maxbytes (int): number of bytes that will be read if no null byte is found
        Avoids infinite loops.

    Returns:
        str: string concatenation of the bytes read
        int: how many bytes were read
    """

    current_string = b''
    current_byte = filebuffer.read(1)
    bytes_read = 1

    while current_byte != b'\x00':

        current_string += current_byte
        # print('current byte: {}'.format(current_byte))

        bytes_read += 1
        current_byte = struct.unpack('c', filebuffer.read(1))[0]

        if bytes_read > maxbytes:
            print('exiting due to infinite loop')
            break

    # for python3 make sure to encode bytes to unicode string
    if sys.version_info.major == 2:
        current_string = unicode(current_string, encoding='utf8')
    else:
        current_string = str(current_string, encoding='utf8')


    return current_string, bytes_read


def read_exr_header(exrpath, maxreadsize=2000):
    """Parses the header of an exr file using the official specification :
    https://www.openexr.com/documentation/openexrfilelayout.pdf

    Args:
        exrpath (str): absolute path to the exr file
        maxreadsize (int, optional): Avoids infinite loops in case a final null byte is never encountered or the exr is formatted in a bad way. Defaults to 2000.

    Raises:
        OSError: if the exr does not exist
        TypeError: if the an unknown exr attribute is encountered

    Returns:
        dict: with the metadata
    """

    if not os.path.exists(exrpath):
        raise OSError('given EXR path does not exist ({})'.format(exrpath))

    exr_file = open(exrpath, 'rb')

    metadata = {}

    try:

        magic_number = struct.unpack('i', exr_file.read(4))
        logger.info('magic_number: {}'.format(magic_number[0]))

        openxr_version_number = struct.unpack('c', exr_file.read(1))
        logger.info('OpenEXR Version Number: {}'.format(
            ord(openxr_version_number[0])))

        version_field_attrs = struct.unpack('ccc', exr_file.read(3))
        logger.info('version_field_attrs : {} {} {}'.format(
            ord(version_field_attrs[0]), ord(version_field_attrs[1]),
            ord(version_field_attrs[2])))

        i = 0

        while i < maxreadsize:

            # We'll always have attribute name, attribute type separated by a null byte
            # Then attribute size and attribute value follow
            attribute_name, attribute_name_length = read_until_null(exr_file)
            attribute_type, _ = read_until_null(exr_file)
            attribute_size = int(struct.unpack('i', exr_file.read(4))[0])

            # If we're reading only byte it means it's the null byte
            # and we've reached the end of the header
            if attribute_name_length == 1:
                logger.info('reached the end of the header!')
                break

            if not attribute_name in metadata:
                metadata[attribute_name] = {}

            # print('attribute name: {}, length: {}, type: {}, size: {}'.format(
            #     attribute_name, attribute_name_length, attribute_type,
            #     attribute_size))

            # How many bytes of the attribute value we've read
            byte_count = 0

            # Parse the attribute value

            if attribute_type == u'box2i':
                box_values = struct.unpack('i' * 4, exr_file.read(4 * 4))

                metadata[attribute_name] = {
                    u'xMin': box_values[0],
                    u'yMin': box_values[1],
                    u'xMax': box_values[2],
                    u'yMax': box_values[3]
                }

            elif attribute_type == u'box2f':
                box_values = struct.unpack('f' * 4, exr_file.read(4 * 4))

                metadata[attribute_name] = {
                    u'xMin': box_values[0],
                    u'yMin': box_values[1],
                    u'xMax': box_values[2],
                    u'yMax': box_values[3]
                }

            elif attribute_type == u'chlist':

                channel_data = {}

                while byte_count < attribute_size:

                    channel_name, channel_name_length = read_until_null(
                        exr_file)

                    byte_count += channel_name_length
                    # print('read {} bytes of {}'.format(byte_count,
                    #                                    attribute_size))

                    # If we've read only one byte it means it was a null char
                    # We've found the end of the channels attribute
                    if channel_name_length == 1:
                        break

                    pixel_type = struct.unpack('i', exr_file.read(4 * 1))
                    byte_count += 4
                    p_linear = struct.unpack('B', exr_file.read(1 * 1))
                    byte_count += 1
                    reserved = struct.unpack('ccc', exr_file.read(1 * 3))
                    byte_count += 3
                    x_sampling = struct.unpack('i', exr_file.read(4 * 1))
                    byte_count += 4
                    y_sampling = struct.unpack('i', exr_file.read(4 * 1))
                    byte_count += 4

                    channel_data[channel_name] = {
                        u'pixel_type': pixel_type,
                        u'pLinear': p_linear,
                        u'reserved': [ord(c) for c in reserved],
                        u'xSampling': x_sampling,
                        u'ySampling': y_sampling
                    }

                    metadata[attribute_name] = channel_data

            elif attribute_type == u'chromaticities':
                chromaticities = struct.unpack('f' * 8, exr_file.read(4 * 8))
                metadata[attribute_name] = {
                    u'redX': chromaticities[0],
                    u'redY': chromaticities[1],
                    u'greenX': chromaticities[2],
                    u'greenY': chromaticities[3],
                    u'blueX': chromaticities[4],
                    u'blueY': chromaticities[5],
                    u'whiteX': chromaticities[6],
                    u'whiteY': chromaticities[7],
                }

            elif attribute_type == u'compression':
                compression_value = struct.unpack('B', exr_file.read(1))
                compression_value = int(compression_value[0])

                try:
                    metadata[u'compression'] = EXR_ATTRIBUTES.COMPRESSION_VALUES[
                        compression_value]

                except IndexError:
                    metadata[u'compression'] = u'unknown'

            elif attribute_type == u'double':
                attribute_value = struct.unpack('d', exr_file.read(8 * 1))
                metadata[attribute_name] = attribute_value[0]

            elif attribute_type == u'envmap':
                attribute_value = struct.unpack('B', exr_file.read(1 * 1))

                try:
                    metadata[attribute_name] = EXR_ATTRIBUTES.ENVMAP_TYPES[
                        attribute_value[0]]
                except IndexError:
                    metadata[attribute_name] = u'unknown'

            elif attribute_type == u'float':
                float_value = struct.unpack('f', exr_file.read(4))
                metadata[attribute_name] = float_value[0]

            elif attribute_type == u'int':
                attribute_value = int(
                    struct.unpack('i', exr_file.read(4 * 1))[0])

                metadata[attribute_name] = attribute_value

            elif attribute_type == u'keycode':
                attribute_values = struct.unpack('i' * 7, exr_file.read(4 * 7))

                metadata[attribute_name] = {
                    u'filmMfcCode': attribute_values[0],
                    u'filmType': attribute_values[1],
                    u'prefix': attribute_values[2],
                    u'count': attribute_values[3],
                    u'perfOffset': attribute_values[4],
                    u'perfsPerFrame': attribute_values[5],
                    u'perfsPerCount': attribute_values[6]
                }

            elif attribute_type == u'lineOrder':
                line_order = int(struct.unpack('B', exr_file.read(1))[0])
                metadata[attribute_name] = EXR_ATTRIBUTES.LINE_ORDER[line_order]

            elif attribute_type == u'm33f':
                attribute_values = struct.unpack('f' * 9, exr_file.read(4 * 9))
                metadata[attribute_name] = attribute_values

            elif attribute_type == u'm44f':
                attribute_values = struct.unpack('f' * 16,
                                                 exr_file.read(4 * 16))
                metadata[attribute_name] = attribute_values

            elif attribute_type == u'preview':

                width = struct.unpack('I', exr_file.read(4 * 1))
                height = struct.unpack('I', exr_file.read(4 * 1))

                pixel_data = struct.unpack(
                    'B', exr_file.read(1 * 4 * width * height))

                metadata[attribute_name] = {
                    u'width': width,
                    u'height': height,
                    u'pixel_data': pixel_data
                }

            elif attribute_type == u'rational':
                first_part = struct.unpack('i', exr_file.read(4))
                second_part = struct.unpack('I', exr_file.read(4))
                metadata[attribute_name] = {
                    u'first_num': first_part[0],
                    u'second_num': second_part[0]
                }

            elif attribute_type == u'string':

                string_content = struct.unpack('c' * attribute_size,
                                               exr_file.read(attribute_size))

                metadata[attribute_name] = ''.join(string_content)

            elif attribute_type == u'stringvector':
                metadata[attribute_name] = []

                while byte_count < attribute_size:

                    string_length = int(struct.unpack('i', exr_file.read(4))[0])
                    byte_count += 4

                    string_content = struct.unpack('c' * string_length,
                                                   exr_file.read(string_length))
                    byte_count += string_length

                    # print('string length: {}'.format(string_length))
                    # print('string content: {}'.format(string_content))

                    metadata[attribute_name].append(''.join(string_content))

            elif attribute_type == u'tiledesc':
                x_size = struct.unpack('I', exr_file.read(4 * 1))
                y_size = struct.unpack('I', exr_file.read(4 * 1))
                mode = struct.unpack('B', exr_file.read(1 * 1))

                metadata[attribute_name] = {
                    u'xSize': x_size,
                    u'ySize': y_size,
                    u'mode': mode
                }

            elif attribute_type == u'timecode':
                time_and_flags = struct.unpack('I', exr_file.read(4 * 1))
                user_data = struct.unpack('I', exr_file.read(4 * 1))

                metadata[attribute_name] = {
                    u'timeAndFlags': time_and_flags,
                    u'userData': user_data
                }

            elif attribute_type == u'v2i':
                vector_2d_value = struct.unpack('ii', exr_file.read(4 * 2))

                metadata[attribute_name] = []
                metadata[attribute_name].append(vector_2d_value[0])
                metadata[attribute_name].append(vector_2d_value[1])

            elif attribute_type == u'v2f':
                vector_2d_value = struct.unpack('ff', exr_file.read(4 * 2))

                metadata[attribute_name] = []
                metadata[attribute_name].append(vector_2d_value[0])
                metadata[attribute_name].append(vector_2d_value[1])

            elif attribute_type == u'v3i':
                vector_3d_value = struct.unpack('iii', exr_file.read(4 * 3))

                metadata[attribute_name] = []
                metadata[attribute_name].append(vector_3d_value[0])
                metadata[attribute_name].append(vector_3d_value[1])
                metadata[attribute_name].append(vector_3d_value[2])

            elif attribute_type == u'v3f':
                vector_3d_value = struct.unpack('fff', exr_file.read(4 * 3))

                metadata[attribute_name] = []
                metadata[attribute_name].append(vector_3d_value[0])
                metadata[attribute_name].append(vector_3d_value[1])
                metadata[attribute_name].append(vector_3d_value[2])

            else:
                logger.error(
                    'unknown attribute type: {}!!'.format(attribute_type))

                metadata[attribute_name] = u'unknown attribute type!'

                raise TypeError(
                    'unknown attribute type: {}'.format(attribute_type))

            i += 1

    finally:
        exr_file.close()

    return metadata
