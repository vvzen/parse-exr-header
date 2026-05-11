from __future__ import print_function

import os
import pprint
import logging
import argparse

import parse_exr_header.lib

log = logging.getLogger('vvzen.parse_metadata')
log.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
log.addHandler(console_handler)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(type=str,
                        nargs="+",
                        dest="source_paths",
                        help="Path to source exr image")

    args = parser.parse_args()
    paths = args.source_paths

    for path in paths:
        if not os.path.exists(path):
            log.error("Source Path was not found on disk: %s", path)
            continue

        metadata = parse_exr_header.lib.read_exr_header(path)
        print(pprint.pformat(metadata))
        if len(paths) > 1:
            print("-"*80)

if __name__ == '__main__':
    main()
