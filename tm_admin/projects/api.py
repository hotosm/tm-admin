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
from datetime import datetime
from dateutil.parser import parse
import tm_admin.types_tm
import geojson
from cpuinfo import get_cpu_info
from shapely.geometry import shape
from shapely import centroid
from tm_admin.types_tm import Mappingtypes, Projectstatus, Taskcreationmode, Editors, Permissions, Projectpriority, Projectdifficulty, Teamroles
from tm_admin.projects.projects_class import ProjectsTable
from tm_admin.tasks.tasks_class import TasksTable
from tm_admin.messages.messages import MessagesDB
from tm_admin.projects.projects import ProjectsDB
from tm_admin.users.users import UsersDB
from tm_admin.teams.teams import TeamsDB
from shapely import wkb, get_coordinates
from tm_admin.dbsupport import DBSupport
from tm_admin.generator import Generator
from tm_admin.pgsupport import PGSupport
from osm_rawdata.pgasync import PostgresClient
import re
# from progress import Bar, PixelBar
from tqdm import tqdm
import tqdm.asyncio
from codetiming import Timer
import asyncio
from shapely import wkb, wkt

# The number of threads is based on the CPU cores
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
        self.allowed_roles = [
            Teamroles.TEAM_MAPPER,
            Teamroles.TEAM_VALIDATOR,
            Teamroles.TEAM_MANAGER,
        ]
        self.messagesdb = MessagesDB()
        self.usersdb = UsersDB()
        self.teamsdb = TeamsDB()
        super().__init__("projects")

    async def initialize(self,
                      uri: str,
                      ):
        """
        Connect to all tables for API endpoints that require accessing multiple tables.

        Args:
            inuri (str): The URI for the TM Admin output database
        """
        await self.connect(uri)
        await self.getTypes("projects")

    async def create(self,
                     project: ProjectsTable,
                     ):
        """
        Create a project and add it to the database.

        Args:
            project (ProjectsTable): The team data

        Returns:
            (bool): Whether the project got created
        """
        # log.warning(f"--- create() ---")
        result = await self.insertRecords([project])

        # The ID of the record that just got inserted is returned
        if result > 0:
            return True

        return False

    async def update(self,
                     project: ProjectsTable,
                     ):
        """
        Update a project that is already in the database.

        Args:
            project (ProjectsTable): The project data

        Returns:
            (bool): Whether the project got updated
        """
        log.warning(f"update(): unimplemented!")

        return False

    async def delete(self,
                    project_ids: int,
                    ):
        """
        Delete a project from the database.

        Args:
            project_ids (id): The project to delete

        Returns:
            (bool): Whether the project got deleted
        """
        # log.warning(f"delete(): unimplemented!")
        await self.deleteRecords([project_ids])

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
        
        """
        teamperm = Mappingnotallowed('USER_NOT_TEAM_MEMBER')
        result = await project.getByWhere(f" ")
        
        # See if user is on a team with team permissions
        level = user.getColumn(uid, 'mapping_level')
        if level != Permissions() or Permissions():
            pass

        return False

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
        log.warning(f"getProjectByTeam(): unimplemented!")
        # sql = f"SELECT FROM projects WHERE project_id={project_id}"
        # where = [{'teams': {"team_id": team_id, "project_id": project_id}}]
        #data = await self.getColumns(['id', 'teams'], where)
        # The role is in a list of dicts in a jsonb column.

        sql = f"SELECT jsonb_path_query(teams, '$.teams[*] ? (@.team_id[*] == {team_id})') AS results FROM projects WHERE id = {project_id};"
        results = await self.execute(sql)

        # There should only be one item in the results. Since it's a jsonb column
        # the data is returned as a string. In the string is an enum value, which
        # gets converted to the actual enum for Teamroles.
        if results[0]['results'][0] == '{':
            tmp1 = eval(results[0]['results'])
            tmp2 = f"Teamroles.{tmp1['role']}"
            role = eval(tmp2)
            return role
        else:
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
        log.warning(f"delete(): unimplemented!")

        return False

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

    async def deleteTasks(self,
                              project_id: int,
                             ):
        """

        Args:
            

        Returns:
            
        """
        log.warning(f"deleteTasks(): Unimplemented!")

        return False

    async def getTasks(self):
        """

        Args:
            

        Returns:
            
        """
        log.warning(f"getTasks(): Unimplemented!")

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
