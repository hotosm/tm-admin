#!/usr/bin/python3

# Copyright (c) 2022, 2023 Humanitarian OpenStreetMap Team
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# Humanitarian OpenStreetmap Team
# 1100 13th Street NW Suite 800 Washington, D.C. 20005
# <info@hotosm.org>

import argparse
import logging
import sys
import os
from sys import argv
# from tm_admin.organizations.organizations_proto import OrganizationsMessage
#from tm_admin.yamlfile import YamlFile
from tm_admin.organizations.organizations import OrganizationsDB
from tm_admin.types_tm import Organizationtype, Mappinglevel
from datetime import datetime

# Instantiate logger
log = logging.getLogger(__name__)

import tm_admin as tma
rootdir = tma.__path__[0]

# FIXME: For now these tests assume you have a local postgres installed. One has the TM
# database, the other for tm_admin.

organization = OrganizationsDB('localhost/tm_admin')

def test_all():
    all = organization.getAll()
    assert len(all) > 0
    
def test_by_id():
    id = 100
    all = organization.getByID(id)
    assert len(all) > 0
    
def test_by_name():
    name = 'Peace Corps'
    all = organization.getByName(name)
    assert len(all) > 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", nargs="?", const="0", help="verbose output")
    parser.add_argument("-u", "--uri", default='localhost/tm_admin', help="Database URI")
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

    print("--- test_by_id() ---")
    test_by_id()

    print("--- test_by_name() ---")
    test_by_name()

    print("--- test_all() ---")
    test_all()
    
    
