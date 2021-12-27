#!/usr/bin/env python
from __future__ import print_function

import os
import sys
import pprint
import logging
import argparse

log = logging.getLogger('vvzen.parse_metadata')
log.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
log.addHandler(console_handler)

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

sys.path.append(os.path.join(CURRENT_DIR, ".."))
import parse_metadata

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(type=str,
                        nargs="+",
                        dest="source_paths",
                        help="Path to source exr image")

    args = parser.parse_args()

    for path in args.source_paths:
        if not os.path.exists(path):
            log.error("Source Path was not found on disk: %s", path)
            continue

        metadata = parse_metadata.read_exr_header(path)
        print(pprint.pformat(metadata))

if __name__ == '__main__':
    main()
