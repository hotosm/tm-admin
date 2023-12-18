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
from tm_admin.users.users_proto import UsersMessage
#from tm_admin.yamlfile import YamlFile
from tm_admin.users.users import UsersDB
from tm_admin.types_tm import Userrole, Mappinglevel
from datetime import datetime

# Instantiate logger
log = logging.getLogger(__name__)

import tm_admin as tma
rootdir = tma.__path__[0]

# FIXME: For now these tests assume you have a local postgres installed. One has the TM
# database, the other for tm_admin.

def test_all(user):
    all = user.getAll()
    assert len(all) > 0
    
def test_by_id(user):
    id = 4606673
    all = user.getByID(id)
    assert len(all) > 0
    
def test_by_name(user):
    name = 'rsavoye'
    all = user.getByName(name)
    assert len(all) > 0

def test_role(user):
    id = 4606673
    role = Userrole(1)
    result = user.updateRole(id, role)
    assert result
    
def test_level(user):
    id = 4606673
    level = Mappinglevel(1)
    result = user.updateMappingLevel(id, level)
    assert result
    
def test_expert(user):
    id = 4606673
    mode = True
    result = user.updateColumn(id, {'is_expert': mode})
    assert result
    
def test_registered(user):
    start = '2020-11-20 08:36:55'
    stime = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
    end = '2023-02-07 12:28:30'
    etime =  datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
    result = user.getRegistered(stime, etime)
    assert result
    

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

    user = UsersDB(args.uri)
    
    print("--- test_by_id() ---")
    test_by_id(user)

    print("--- test_by_name() ---")
    test_by_name(user)

    print("--- test_role() ---")
    test_role(user)

    print("--- test_level() ---")
    test_level(user)

    print("--- test_expert() ---")
    test_expert(user)

    print("--- test_registered() ---")
    test_registered(user)

    print("--- test_all() ---")
    test_all(user)
    
    
