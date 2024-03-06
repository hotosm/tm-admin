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
from tm_admin.types_tm import Taskcreationmode, Taskstatus, Teamroles
from tm_admin.projects.projects_class import ProjectsTable
from tm_admin.tasks.tasks_class import TasksTable
from tm_admin.messages.messages import MessagesDB
from tm_admin.projects.projects import ProjectsDB
from tm_admin.users.users import UsersDB
from tm_admin.teams.teams import TeamsDB
from shapely import wkb, get_coordinates
from tm_admin.dbsupport import DBSupport
from tm_admin.generator import Generator
import re
# from progress import Bar, PixelBar
from tqdm import tqdm
import tqdm.asyncio
from codetiming import Timer
import asyncio
from tm_admin.pgsupport import PGSupport

# The number of threads is based on the CPU cores
info = get_cpu_info()
cores = info["count"] * 2

# Instantiate logger
log = logging.getLogger(__name__)

class TasksAPI(PGSupport):
    def __init__(self):
        """
        Create a class to handle the backend API calls, so the code can be shared
        between test cases and the actual code.

        Returns:
            (TasksAPI): An instance of this class
        """
        super().__init__("tasks")

    async def initialize(self,
                      inuri: str,
                      ):
        """
        Connect to all tables for API endpoints that require
        accessing multiple tables.

        Args:
            inuri (str): The URI for the TM Admin output database
        """
        await self.connect(inuri)
        await self.getTypes("tasks")

    async def getStatus(self,
                      task_id: int,
                      project_id: int,
                    ):
        """
        Get the current status for a task using it's project and task IDs.

        Args:
            task_id (int): The task to lock
            project_id (int): The team to get the data for

        Returns:
            (dict): the project information
        """
        log.debug(f"--- getByID() ---")
        sql = f"SELECT task_status FROM tasks WHERE project_id={project_id} AND id={task_id}"
        results = await self.execute(sql)
        return results

    async def getByID(self,
                      task_id: int,
                      project_id: int,
                    ):
        """
        Get all the information for a task using it's project and task IDs.

        Args:
            task_id (int): The task to lock
            project_id (int): The team to get the data for

        Returns:
            (dict): the project information
        """
        log.debug(f"--- getByID() ---")
        sql = f"SELECT * FROM tasks WHERE project_id={project_id} AND id={task_id}"
        results = await self.execute(sql)
        return results

    async def getByUser(self,
                        user_id: int,
                        task_id: int,
                        project_id: int,
                        ):
        """
        Get all the information for a project using it's ID

        Args:
            user_id (int): The user ID to lock
            task_id (int): The task to lock
            project_id (int): The project this task is part of

        Returns:
            (dict): the task information
        """
        log.debug(f"--- getByID() ---")
        sql = f"SELECT * FROM tasks WHERE project_id={project_id} AND id={task_id} AND user_id={user_id}"
        results = await self.execute(sql)
        return results

    async def create(self,
                     task: TasksTable,
                     ):
        """
        Create a task and add it to the database.

        Args:
            task (TasksTable): The task data

        Returns:
            (bool): Whether the task got created
        """
        # log.warning(f"create(): unimplemented!")
        result = await self.insertRecords([task])

        # The ID of the record that just got inserted is returned
        if result:
            return True

        return False

    async def update(self,
                     task: TasksTable,
                     ):
        """
        Update a task that is already in the database.

        Args:
            task (TasksTable): The task data

        Returns:
            (bool): Whether the task got updated
        """
        log.warning(f"update(): unimplemented!")

        return False

    async def delete(self,
                    task_id: int,
                     ):
        """
        Delete a task from the database.

        Args:
            task_id (int): The team to delete

        Returns:
            (bool): Whether the task got deleted
        """
        log.warning(f"delete(): unimplemented!")

        return False

    async def changeStatus(self,
                        user_id: int,
                        task_id: int,
                        project_id: int,
                        status: Taskstatus,
                        ):
        """
        Manage the status of a task. This would be locking or unlocking,
        validation status, etc...

        Args:
            user_id (int): The mapper locking the task
            task_id (int): The task to lock
            project_id (int): The project containing the task
            status (TaskStatus): The status to change to

        Returns:
            (bool): Whether locking/unlocking the task was sucessful
        """
        log.warning(f"delete(): unimplemented!")

    async def markAllMapped(self):
        """

        Args:
            
        Returns:
            
        """
        log.warning(f"markAllMapped(): unimplemented!")

        return False

    async def resetBadImagery(self):
        """

        Args:
            
        Returns:
            
        """
        log.warning(f"resetBadImagery(): unimplemented!")

        return False

    async def undoMapping(self):
        """

        Args:
            
        Returns:
            
        """
        log.warning(f"undoMapping(): unimplemented!")

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
