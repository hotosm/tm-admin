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
from shapely.geometry import shape
from shapely import centroid
from tm_admin.types_tm import Mappingtypes, Projectstatus, Taskcreationmode, Editors, Permissions, Projectpriority, Projectdifficulty
from tm_admin.projects.projects_class import ProjectsTable
from tm_admin.tasks.tasks_class import TasksTable
from shapely import wkb, get_coordinates
from tm_admin.pgsupport import PGSupport
from osm_rawdata.pgasync import PostgresClient
import re
from tm_admin.access import Roles
# from progress import Bar, PixelBar
from tqdm import tqdm
import tqdm.asyncio
from codetiming import Timer
import asyncio
from shapely import wkb, wkt
import tm_admin

from cpuinfo import get_cpu_info
info = get_cpu_info()
cores = info["count"] * 2

# Instantiate logger
log = logging.getLogger(__name__)

class ProjectsAPI(PGSupport):
    def __init__(self):
        """
        Create a class to handle the backend API calls, so the code can be shared
        between test cases and the actual code.

        Returns:
            (ProjectsAPI): An instance of this class
        """
        # self.allowed_roles = [
        #     Teamrole.MAPPER,
        #     Teamrole.VALIDATOR,
        #     Teamrole.MANAGER,
        # ]
        from tm_admin.users.api import UsersAPI
        self.users = None
        self.tasks = None
        super().__init__("projects")

    async def initialize(self,
                         inuri: str,
                      ) -> None:
        """
        Connect to all tables for API endpoints that require accessing multiple tables.

        Args:
            inuri (str): The URI for the TM Admin output database
        """
        await self.connect(inuri)
        await self.getTypes("projects")
        self.users = tm_admin.users.api.UsersAPI()
        self.tasks = tm_admin.tasks.api.TasksAPI()

    async def getByID(self,
                     project_id: int,
                    ):
        """
        Get all the information for a project using it's ID

        Args:
            project_id (int): The team to get the data for

        Returns:
            (dict): the project information
        """
        log.debug(f"--- getByID() ---")
        sql = f"SELECT * FROM projects WHERE id={project_id}"
        results = await self.execute(sql)
        return results

    async def getTeamRole(self,
                        project_id: int,
                        team_id: int,
                        ):
        """
        Args:
            project_id (id): The project ID
            team_id (id): The team ID

        Returns:
            (Teamrole): The role of this team in this project
        """
        # log.warning(f"getProjectByTeam(): unimplemented!")
        # sql = f"SELECT FROM projects WHERE project_id={project_id}"
        # where = [{'teams': {"team_id": team_id, "project_id": project_id}}]
        #data = await self.getColumns(['id', 'teams'], where)
        # The role is in a list of dicts in a jsonb column.

        sql = f"SELECT jsonb_path_query(members, '$.members[*] ? (@.team_id[*] == {team_id})') AS results FROM projects WHERE id = {project_id};"
        # print(sql)
        results = await self.execute(sql)

        # There should only be one item in the results. Since it's a jsonb column
        # the data is returned as a string. In the string is an enum value, which
        # gets converted to the actual enum for Teamrole.
        if len(results) > 0:
            if results[0]['results'][0] == '{':
                tmp1 = eval(results[0]['results'])
                tmp2 = f"Roles.{tmp1['role']}"
                role = eval(tmp2)
                return role

        # we should never get here, but you never know...
            return None

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
        sql = f"SELECT * FROM projects WHERE name='{name}'"
        results = await self.execute(sql)
        return results

    async def changeStatus(self,
                        project_id: int,
                        status: Projectstatus,
                        ):
        """
        Manage the status of a task. This would be locking or unlocking,
        validation status, etc...

        Args:
            project_id (int): The project ID to change
            status (ProjectStatus): The status to change to

        Returns:
            (bool): Whether locking/unlocking the task was sucessful
        """
        log.warning(f"changeStatus(): unimplemented!")

        return False

    async def evaluateMappingPermissions(self,
                                   uid: int,
                                   pid: int,
                                   perm: Permissions,
                                   ):
        """
        evaluate_mapping_permission()

        Args:
            uid (int): The user ID
            pid (int): The project ID
            perm (Permissions): The permission level to check against

        Returns:
            (bool): If the user has the right permissions for this project
        """
        teamperm = Mappingnotallowed('USER_NOT_TEAM_MEMBER')
        result = await project.getByWhere(f" ")

        # See if user is on a team with team permissions
        level = user.getColumn(uid, 'mapping_level')
        if level != Permissions() or Permissions():
            pass

        return False

    async def permittedUser(self,
                            project_id: int,
                            user_id: int,
                            ):
        """
        Is a user permitted to map on this project.

        Args:
            user_id (int): The user ID to lock
            project_id (int): The project this task is in

        Returns:
            (Mappingnotallowed): The results of checking permissions
        """

        # FIXME: is the user blocked ?

        # FIXME: see it the users is allowed to work on this project
        log.warning(f"permittedUser(): unimplemented!")
        result = await self.getColumns(["allowed_users"],
                                        {"project_id": project_id})

        # FIXME: Has user accepted license
        log.warning(f"permittedUser(): unimplemented!")
        result = await self.users.getColumns(["licenses"],
                                        {"user_id": user_id})
        if len(result) == 0:
            return Mappingnotallowed.USER_NOT_ACCEPTED_LICENSE

        # FIXME: Then check project status
        result = await self.getColumns(["status"],
                                        {"project_id": project_id})
        if len(result) == 0:
            return Mappingnotallowed.PROJECT_NOT_PUBLISHED

        # FIXME: Then see if task is already locked
        result = await self.users.getColumns(["task_status"],
                                        {"user_id": user_id})


        if user_id in result[0]:
            return Mappingnotallowed.USER_ALLOWED
        else:
            # FIXME: add errors
            pass

    async def toggleFavorites(self,
                              flag: bool = None,
                              ):
        """
        Add or remove this project favorites for a user.

        Args:
            flag (bool): The value to set to, otherwise defaults to flipping it.
        """
        log.warning(f"toggleFavorites(): Unimplemented!")

        return False

    async def toggleFeatures(self,
                              flag: bool = None,
                             ):
        """

        Args:
            

        Returns:
            
        """
        log.warning(f"toggleFeatures(): Unimplemented!")

        return False

    async def unlockTasks(self,
                              project_id: int,
                             ):
        """

        Args:
            

        Returns:
            
        """
        log.warning(f"toggleFeatures(): Unimplemented!")

        return False

    async def getUserStats(self,
                            user_id: int,
                            project_id: int,
                             ):
        """

        Args:
            

        Returns:
            
        """
        log.warning(f"getUserStats(): Unimplemented!")

        return False

    async def getProjectStats(self,
                             project_id: int,
                             ):
        """

        Args:
            

        Returns:
            
        """
        log.warning(f"getProjectStats(): Unimplemented!")

        return False

    async def getAOI(self,
                         project_id: int,
                         ):
        """

        Args:
            project_id (int): The project to get the data for
            
        Returns:
            
        """
        # log.warning(f"getAOI(): Unimplemented!")
        data = await self.getColumns(['geometry'],  {"id": project_id})

        # Convert the WKB to a Polygon.
        return wkb.loads(data[0]['geometry'])

    async def getDailyContributions(self,
                               project_id: int,
                                ):
        """

        Args:
            project_id (int): The project to get the data for
            

        Returns:
            
        """
        log.warning(f"getDailyContributions(): Unimplemented!")

        return False

    async def getProjectSummary(self):
        """

        Args:
            

        Returns:
            
        """
        log.warning(f"getProjectSummary(): Unimplemented!")

        return False

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
