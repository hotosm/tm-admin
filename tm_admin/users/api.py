#!/usr/bin/python3

# Copyright (c) 2022, 2023, 2024 Humanitarian OpenStreetMap Team
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
from datetime import datetime
from dateutil.parser import parse
import tm_admin.types_tm
import geojson
from cpuinfo import get_cpu_info
from shapely.geometry import shape
from shapely import centroid
from tm_admin.types_tm import Editors, Permissions, Userrole, Mappinglevel, Teamroles
from tm_admin.projects.projects_class import ProjectsTable
from tm_admin.users.users_class import UsersTable
from tm_admin.messages.messages import MessagesDB
from tm_admin.projects.projects import ProjectsDB
from tm_admin.users.users import UsersDB
from tm_admin.teams.teams import TeamsDB
from shapely import wkb, get_coordinates
from tm_admin.dbsupport import DBSupport
from tm_admin.generator import Generator
from tm_admin.pgsupport import PGSupport
import re
# from progress import Bar, PixelBar
from tqdm import tqdm
import tqdm.asyncio
from codetiming import Timer
import asyncio

# The number of threads is based on the CPU cores
info = get_cpu_info()
cores = info["count"] * 2

# Instantiate logger
log = logging.getLogger(__name__)

class UsersAPI(PGSupport):
    def __init__(self):
        self.allowed_roles = [
            Teamroles.TEAM_MAPPER,
            Teamroles.TEAM_VALIDATOR,
            Teamroles.TEAM_MANAGER,
        ]
        self.messagesdb = MessagesDB()
        self.projectsdb = ProjectsDB()
        super().__init__("users")

    async def initialize(self,
                      uri: str,
                      ):
        """
        Connect to all tables for API endpoints that require
        accessing multiple tables.

        Args:
            inuri (str): The URI for the TM Admin output database
        """
        await self.connect(uri)
        await self.getTypes("users")
        #await self.messagesdb.connect(uri)
        #await self.usersdb.connect(uri)
        #await self.teamsdb.connect(uri)

    async def create(self,
                     user: UsersTable,
                     ):
        """
        Create a user and add them to the database.

        Args:
            user (UsersTable): The user's data

        Returns:
            (bool): Whether the user got created
        """
        log.warning(f"create(): unimplemented!")

    async def update(self,
                     org: UsersTable,
                     ):
        """
        Update a user that is already in the database.

        Args:
            user (UsersTable): The user's data

        Returns:
            (bool): Whether the user got updated
        """
        log.warning(f"update(): unimplemented!")

    async def delete(self,
                    user_id: int,
                     ):
        """
        Delete a user from the database.

        Args:
            user_id (int): The user's ID

        Returns:
            (bool): Whether the user got deleted
        """
        log.warning(f"delete(): unimplemented!")

    async def getByID(self,
                     user_id: int,
                    ):
        """
        Get all the information for a project using it's ID

        Args:
            project_id (int): The team to get the data for

        Returns:
            (dict): the project information
        """
        log.debug(f"--- getByID() ---")
        sql = f"SELECT * FROM users WHERE id={user_id}"
        results = await self.execute(sql)
        return results

    async def getByName(self,
                        name: str,
                        ):
        """
        Get all the information for a project using the name

        Args:
            name (str): The project to get the data for

        Returns:
            (dict): the project information
        """
        log.debug(f"--- getByName() ---")
        sql = f"SELECT * FROM users WHERE name='{name}'"
        results = await self.execute(sql)
        return results

    async def updateRole(self,
                   id: int,
#                   role: Userrole,
                   ):
        """
        Update the role for a user.

        Args:
            id (int): The users ID
            role (Userrole): The new role.
        """
 #       role = Userrole(role)
 #       return self.updateColumn(id, {'role': role.name})

    async def updateMappingLevel(self,
                   id: int,
                   level: Mappinglevel,
                   ):
        """
        Update the mapping level for a user.

        Args:
            id (int): The users ID.
            level (Mappinglevel): The new level.
        """
        mlevel = Mappinglevel(level)
        result = await self.updateColumn(id, {'mapping_level': mlevel.name})
        return result

    async def updateExpert(self,
                   id: int,
                   mode: bool,
                   ):
        """
        Toggle the expert mode for a user.

        Args:
            id (int): The users ID.
            mode (bool): The new mode..
        """
        result = await self.updateColumn(id, {'expert_mode': mode})
        return result

    async def getRegistered(self,
                      start: datetime,
                      end: datetime,
                      ):
        """
        Get all users registered in this timeframe.

        Args:
            start (datetime): The starting timestamp
            end (datetime): The starting timestamp

        Returns:
            (list): The users registered in this timeframe.
        """

        where = f" date_registered > '{start}' and date_registered < '{end}'"
        # result = self.getByWhere(where)
        # return result

async def main():
    """This main function lets this class be run standalone by a bash script."""
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

if __name__ == "__main__":
    """This is just a hook so this file can be run standalone during development."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
