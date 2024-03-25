#!/usr/bin/python3

# Copyright (c) 2023 Humanitarian OpenStreetMap Team
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
import asyncio
from codetiming import Timer
from tm_admin.access import Roles, Operation, Access

# Instantiate logger
log = logging.getLogger(__name__)

import tm_admin as tma
rootdir = tma.__path__[0]

async def test_mapper(acl: Access):
    hits = 0
    if await acl.check('projects', Roles.MAPPER, Operation.READ):
        hits += 1
    if await acl.check('users', Roles.MAPPER, Operation.READ):
        hits += 1
    if await acl.check('tasks', Roles.MAPPER, Operation.READ):
        hits += 1
    if await acl.check('messages', Roles.MAPPER, Operation.READ):
        hits += 1
    if await acl.check('campaigns', Roles.MAPPER, Operation.READ):
        hits += 1
    # This is supposed to fail
    if not await acl.check('campaigns', Roles.MAPPER, Operation.CREATE):
        hits += 1

    assert hits == 5

async def test_manager(acl: Access):
    hits = 0
    if await acl.check('tasks', Roles.PROJECT_MANAGER, Operation.READ):
        hits += 1
    if await acl.check('projects', Roles.PROJECT_MANAGER, Operation.UPDATE):
        hits += 1
    if await acl.check('users', Roles.PROJECT_MANAGER, Operation.DELETE):
        hits += 1

    assert hits == 3

async def test_validator(acl: Access):
    hits = 0
    if await acl.check('tasks', Roles.VALIDATOR, Operation.READ):
        hits += 1
    # This is supossed to fail
    if not await acl.check('tasks', Roles.VALIDATOR, Operation.DELETE):
        hits += 1

    assert hits == 2

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", nargs="?", const="0", help="verbose output")
    parser.add_argument("-u", "--uri", default='localhost/testdata', help="Database URI")
    parser.add_argument("-c", "--config", default='tmroles.yaml', help="The config file for this project")

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

    acl = Access(args.config)
    await test_mapper(acl)
    await test_manager(acl)
    await test_validator(acl)
    
if __name__ == "__main__":
    """This is just a hook so this file can be run standalone during development."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
