#!/usr/bin/python3

# Copyright (c) 2023, 2024 Humanitarian OpenStreetMap Team
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
import tm_admin.types_tm
from tm_admin.types_tm import Teamrole, Userrole, Roles
from codetiming import Timer
from tm_admin.yamlfile import YamlFile
import asyncio
from rbac import RBAC
from enum import IntEnum
# This is only used for debugging output during development
import json

# Instantiate logger
log = logging.getLogger(__name__)

import tm_admin as tma
rootdir = tma.__path__[0]

class Operation(IntEnum):
    READ = 1
    CREATE = 2
    MODIFY = 3
    DELETE = 4

class Access(object):
    def __init__(self,
                 yamlfile: str = None,
                 ):
        self.rbac = RBAC()
        yaml = YamlFile(f"{rootdir}/{yamlfile}")
        
        self.perms = dict()
        self.permissions = dict()
        self.domains = dict()
        self.roles = dict()
        # self.subjects = dict()
        
        # Convert to a dict to make it easy to query
        create = self.rbac.create_permission('c')
        delete = self.rbac.create_permission('d')
        update = self.rbac.create_permission('u')
        read = self.rbac.create_permission('r')
        self.perms = {"create": create,
                      "delete": delete,
                      "update": update,
                      "read": read}
        # Parse the YAML config file into a data structure
        for entry in yaml.yaml:
            for category, values in entry.items():
                if category == "domains":
                    for entry in values:
                        self.domains[entry] = self.rbac.create_domain(entry)
                    continue
                if category == "permissions":
                    for roles in values:
                        [[k, v]] = roles.items()
                        self.permissions[k] = dict()
                        self.roles[k] = self.rbac.create_role(k)
                        # print(f"\t{k}, {v}")
                        if type(v) == list:
                            for i in v:
                                if type(i) == dict:
                                    [[k1, v1]] = i.items()
                                    # print(f"DICT: {k1} = {v1}")
                                    if k1 == 'children':
                                        # print(f"CHILDREN: {k1} {v1}")
                                        self.permissions[k]['children'] = v1
                                    elif k1 == 'tables':
                                        # print(f"TABLES: {v1}")
                                        self.permissions[k]['tables'] = v1
                                else:
                                    # This is an access permission
                                    # print(f"STR: {k} = {i}")
                                    self.permissions[k]['access'] = i
        #for role in self.roles:
        #    subject.authorize(role)
        # print(json.dumps(self.permissions, indent=4))
        # print("------------------")
        for k, v in self.permissions.items():
            if 'children' in v:
                # print(f"CHILD: {k} = {v['children']}")
                self.rbac.create_role(k, children=v['children'])
            elif 'tables' in v:
                # print(f"TABLE: {k1} = {v['tables']}")
                for table in v['tables']:
                    self.roles[k].add_permission(self.perms[v['access']], self.domains[table])

        for role, data in self.roles.items():
            # [[ k, v]] =
            subject = self.rbac.create_subject(role)
            subject.authorize(self.roles[role])
        
        self.rbac.lock()

    async def check(self,
                    domain: str,
                    access: str,
                    userrole: Userrole = None,
                    teamrole: Teamrole = None,
                    ):
        """
        Check a role in a domain for access permissions.

        Args:
            domain (str): The domain to check for the role
            access (str): The access permissions
            userrole (Userrole): A user role
            teamrole (Teamrole): A team role
        """
        return self.rbac.go(self.roles[role.lower()],
                            self.domains[domain.lower()],
                            self.perms[access.lower()])

async def main():
    """This main function lets this class be run standalone by a bash script."""
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
    role = Userrole(Userrole.PROJECT_MANAGER)
    op = Operation(Operation.READ)
    # await acl.check('projects', userrole=op)

    # rights = await roles.getRights(Userrole.PROJECT_MANAGER)
    # print(rights)

if __name__ == "__main__":
    """This is just a hook so this file can be run standalone during development."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
