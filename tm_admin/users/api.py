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

from __future__ import annotations

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
from tm_admin.types_tm import Editors, Permissions, Userrole, Mappinglevel, Teamrole, Taskstatus, Projectstatus
from tm_admin.projects.projects_class import ProjectsTable
from tm_admin.users.users_class import UsersTable
from tm_admin.users.user_stats_class import UserstatsTable
from shapely import wkb, get_coordinates
from tm_admin.pgsupport import PGSupport
import typing
if typing.TYPE_CHECKING:
    from tm_admin.projects.api import ProjectsAPI
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
        self.projects = None #ProjectsAPI()
        # self.projects = projects.api.ProjectsAPI()
        self.cursor = None
        super().__init__("users")

    async def initialize(self,
                      inuri: str,
                      papi: ProjectsAPI,
                      ) -> None:
        """
        Connect to all tables for API endpoints that require
        accessing multiple tables.

        Args:
            inuri (str): The URI for the TM Admin output database
        """
        await self.connect(inuri)
        await self.getTypes("users")
        # await self.projects.initialize(inuri)
        await papi.initialize(inuri, self)
        self.projects = papi
        # self.cursor = "DECLARE user_cursor CURSOR FOR SELECT * FROM users;"

    async def getByID(self,
                     user_id: int,
                    ):
        """
        Get all the information for a user using it's ID

        Args:
            user_id (int): The user to get the data for

        Returns:
            (dict): the user information
        """
        # log.debug(f"--- getByID() ---")
        result = await self.getColumns(['*'], {"id": user_id})
        return result

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

    async def getRole(self,
                  user_id: int,
                  ):
        """
        Get the role for a user.

        Args:
            user_id (int): The user's ID

        Returns:
            (Userrole): The user's role
        """
        result = await self.getColumns(['role'], {"id": user_id})

        return eval(f"Userrole.{result[0]['role']}")

    async def getBlocked(self,
                  user_id: int,
                  ):
        """
        Get the role for a user.

        Args:
            user_id (int): The user's ID

        Returns:
            (bool): If the user is blocked or not
        """
        result = await self.getColumns(['role'], {"id": user_id})

        role = eval(f"Userrole.{result[0]['role']}")
        if role == Userrole.USER_READ_ONLY:
            return True
        else:
            return False

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

    async def getFavoriteProjects(self,
                                  user_id: int,
                                  ):
        """
        Get the data for a users favorite projects.

        Args:
            user_id (int): The user to get the favorites for

        Returns:
            (list): A list of the projects data
        """
        result = await self.getColumns({"favorite_projects"}, {"id": user_id})
        data = list()
        for project_id in result[0]['favorite_projects']:
            data.append(await self.projects.getByID(project_id))

        return data

    async def getPagedUsers(self,
                            paged: bool,
                            count: int,
                            username: str = None,
                            user_id: int = None,
                            role: Userrole = None,
                            level: Mappinglevel = None,
                            ):
        """
        Get paged list of all usernames using either the
        user ID or a partial username.

        Args:
            paged (bool): Whether to page the results
            count (int): The number of entries in the page
            username (str): The partial user name
            user_id (int): The user ID
            role (Userrole): The user's role
            level (Mappinglevel): The users mapping level

        Returns:
             (list): The users matching the query
        """

    async def getFilterUsers(self,
                             username: str,
                             page: int = 10,
                             project_id: int = None,
                             close: bool = False,
                             ):
        """"
        Get paged lists of users matching OpenStreetMap
        using either the user ID or a partial username.
        The cursor gets closed when the class destructs,
        or by specifying the close parameter.

        Args:
            username (str): The partial user name
            page (int): How many records in each page
            project_id (int): Optional project ID
            close (bool): Whether to close the cursor to restart
                          from the beginning.

        Returns:
            (list): The users matching the query
        """
        try:
            result = await self.execute(f"SELECT FROM pg_cursor WHERE name = 'user_cursor'")
            print(result)
        except:
            pass
        if project_id:
            self.cursor = f"DECLARE user_cursor CURSOR WITH HOLD FOR SELECT username AS username FROM users WHERE username ILIKE '%{username}%' AND  {project_id} = ANY (projects_mapped) ORDER BY username DESC NULLS LAST, username"
        else:
            self.cursor = f"DECLARE user_cursor CURSOR WITH HOLD FOR SELECT username AS users_username FROM users WHERE username ILIKE '%{username}%' ORDER BY username DESC NULLS LAST, username"
        print(self.cursor)

        await self.execute(self.cursor)
        sql = f"FETCH FORWARD {page} FROM user_cursor"
        return await self.execute(sql)

    async def getLockedTasks(self,
                             username: str = None,
                             user_id: int = None,
                             ):
        """
        Gets any locked tasks on the project for the logged
        in user using either the user ID or a partial username.

        Args:
            username (str): The partial user name
            user_id (int): The ID of the logged in user

        Returns:
            (list): The task IDs this user has locked
        """
        result = await self.getByID(user_id)
        # FIXME: incomplete

    async def getStats(self,
                       username: str = None,
                       user_id: int = None,
                       ):
        """
        Get detailed statistics about a user using either
        the user ID or a partial username.

        Args:
            username (str): The partial user name
            user_id (int): The ID of the logged in user

        Returns:
            (UserStats): The statistics for this user
        """
        # FIXME: unimplemented

    async def getInterestsStats(self,
                                username: str = None,
                                user_id: int = None,
                                ):
        """
        Get rate of contributions from a user given their
        interests using either the user ID or a partial username.

        Args:
            username (str): The partial user name
            user_id (int): The ID of the logged in user

        Returns:
            (int): The rate of contributions
        """
        # FIXME: unimplemented

    async def getAllStats(self,
                          start: datetime,
                          end: datetime,
                          ):
        """
        Get rate of contributions from a user given their
        interests using either the user ID or a partial username.

        Args:
            start (datetime): The starting timestamp
            end (datetime): The ending timestamp

        Returns:
            (list): A list of the stats for the users in this
                    time frame
        """
        # FIXME: unimplemented

    async def getInteracts(self,
                       tstatus: Taskstatus,
                       pstatus: Projectstatus,
                       project_id: int,
                       start: datetime,
                       end: datetime,
                       sort: str,
                       page: int = 10,
                       username: str = None,
                       user_id: int = None,
                       ):
        """
        Get a list of tasks a user has interacted with
        using either the user ID or a partial username.

        Sort criteria is action_date or project_id.

        Args:
            username (str): The partial user name
            user_id (int): The ID of the logged in user
            tstatus (Taskstatus): The status of the task
            pstatus (Projectstatus): The status of the project
            project_id (int): The project ID
            start (datetime): The starting timestamp
            end (datetime): The ending timestamp
            sort (str): The column to use for sorting the results
            page (int): How many records in each page

        Returns:
            (list): FIXME! a list of task data ?
        """
        # FIXME: unimplemented, currently this is really slow!!

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

