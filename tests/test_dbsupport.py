#!/usr/bin/python3

# Copyright (c) 2022, 2023 Humanitarian OpenStreetMap Team
#
# This file is part of tm-admin.
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with tm-admin.  If not, see <https:#www.gnu.org/licenses/>.
#

import logging
import os
import argparse
import sys

# import tm_admin as tma
# rootdir = tma.__path__[0]

# Instantiate logger
log = logging.getLogger(__name__)

# def test_dummy():
#     """Placeholder to allow CI to pass."""
#     assert True

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", nargs="?", const="0", help="verbose output")
    args = parser.parse_args()

    # if verbose, dump to the terminal.
    log_level = os.getenv("LOG_LEVEL", default="INFO")
    if args.verbose is not None:
        log_level = logging.DEBUG
        logging.basicConfig(
                level=log_level,
                format=("%(asctime)s.%(msecs)03d [%(levelname)s] " "%(name)s | %(funcName)s:%(lineno)d | %(message)s"),
                datefmt="%y-%m-%d %H:%M:%S",
        stream=sys.stdout,
        )
        
    # test_dummy()
    log.debug("foo")
