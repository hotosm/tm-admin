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
from tm_admin.types_tm import Taskcreationmode, Taskstatus, Teamrole, Taskaction
from tm_admin.projects.projects_class import ProjectsTable
from tm_admin.projects.projects_teams_class import Projects_teamsTable
from tm_admin.tasks.tasks_class import TasksTable
from shapely import wkb, get_coordinates
from tm_admin.tasks.task_history_class import Task_historyTable
import re
# from progress import Bar, PixelBar
from tqdm import tqdm
import tqdm.asyncio
from codetiming import Timer
import asyncio
from tm_admin.pgsupport import PGSupport
import typing
#if typing.TYPE_CHECKING:
#    from tm_admin.projects.api import ProjectsAPI
#    from tm_admin.users.api import UsersAPI

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
        self.projects =  tm_admin.projects.api.ProjectsAPI()
        self.users = tm_admin.users.api.UsersAPI()

    async def initialize(self,
                      inuri: str,
                      ) -> None:
        """
        Connect to all tables for API endpoints that require
        accessing multiple tables.

        Args:
            inuri (str): The URI for the TM Admin output database
        """
        await self.connect(inuri)
        await self.getTypes("tasks")
        self.projects = tm_admin.projects.api.ProjectsAPI()
        self.users = tm_admin.users.api.UsersAPI()

    async def getStatus(self,
                      task_id: int,
                      project_id: int,
                    ) -> Taskstatus:
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

    async def changeAction(self,
                        user_id: int,
                        task_id: int,
                        project_id: int,
                        action: Taskaction,
                        ):
        """
        Manage the status of a task. This would be locking or unlocking,
        validation status, etc...

        Args:
            user_id (int): The mapper locking the task
            task_id (int): The task to lock
            project_id (int): The project containing the task
            action (Taskaction): The action to change to

        Returns:
            (bool): Whether the change was sucessful
        """
        # log.warning(f"changeStatus(): unimplemented!")

        # FIXME: Make sure the user is in the allowed_user in the projects table
        # the history
        history = None
        status = None
        now = datetime.now()
        # All actions get written to the history
        history = {"action": action,
                   "action_text": action.name,
                   "action_date": '{:%Y-%m-%dT%H:%M:%S}'.format(now),
                   "user_id": user_id}
        # Actions change the status
        if action == Taskaction.LOCKED_FOR_MAPPING:
            status = Taskstatus(Taskstatus.TASK_LOCKED_FOR_MAPPING)
        elif action == Taskaction.LOCKED_FOR_VALIDATION:
            status = Taskstatus(Taskstatus.TASK_LOCKED_FOR_VALIDATIONG)
        elif action == Taskaction.STATE_CHANGE:
            pass
        elif action == Taskaction.COMMENT:
            pass
        elif action == Taskaction.AUTO_UNLOCKED_FOR_MAPPING:
            status = Taskstatus(Taskstatus.READY)
        elif action == Taskaction.AUTO_UNLOCKED_FOR_VALIDATION:
            status = Taskstatus(Taskstatus.TASK_LOCKED_FOR_VALIDATION)
        elif action == Taskaction.EXTENDED_FOR_MAPPING:
            status = Taskactipon(Taskaction.READY) # FIXME: Huh ?
        elif action == Taskaction.EXTENDED_FOR_VALIDATION:
            status = Taskaction(Taskaction.READY) # FIXME: Huh ?
        elif action == Taskaction.RELEASED_FOR_MAPPING:
            status = Taskstatus(Taskaction.READY) # FIXME: Huh ?
        elif action == Taskaction.MARKED_MAPPED:
            status = Taskstatus(Taskaction.TASK_STATUS_MAPPED)
        elif action == Taskaction.VALIDATED:
            status = Taskstatus(Taskaction.VALIDATED)
        elif action == Taskaction.TASK_MARKED_INVALID:
            status = Taskstatus(Taskaction.TASK_INVALIDATED)
        elif action == Taskaction.MARKED_BAD:
            # FIXME: this should set the mapping issue
            status = Taskstatus(Taskaction.READY) # FIXME: Huh ?
        elif action == Taskaction.SPLIT_NEEDED:
            status = Taskstatus(Taskaction.SPLIT)
        elif action == Taskaction.RECREATED:
            status = Taskstatus(Taskaction.READY) # FIXME: Huh ?

        # FIXME: For some reason if I try to pass the dict inline,
        # it gets converted to a set, so then fails.
        stats = {"task_status": status}
        await self.updateColumns(stats,
                                 {"task_id": task_id,
                                  "project_id": project_id})

    async def lockTask(self,
                       task_id: int,
                       project_id: int,
                       user_id: int,
                       ):
        """
        Lock a task to a mapper

        Args:
            user_id (int): The user ID to lock
            task_id (int): The task to update
            project_id (int): The project this task is in

        Returns:
            (Mappingnotallowed): If locking was sucessful or not
        """

        # FIXME: First see if a task is in a valid state to map.
        # Errors from Mappingnotallowed

        result = await projects.permittdUser(user_id, project_id)

        if result == Mappingnotallowed.USER_ALLOWED:
            result = await tasks.changeAction(user_id, task_id, project_id,
                                              Taskaction.LOCKED_FOR_MAPPING)
        else:
            return result

    async def updateHistory(self,
                            history: list,
                            task_id: int,
                            project_id: int,
                            ):
        """
        Update the task history column.

        Args:
            history (list): The task history to update
            task_id (int): The task to update
            project_id (int): The project this task is in

        Returns:
            (bool): If it worked
        """
        # log.warning(f"updateHistory(): unimplemented!")

        data = str()
        for entry in history:
            for k, v in entry.items():
                if str(type(v))[:5] == "<enum":
                    data += f'" {v.name}", '
                else:
                    data += f'" {v}", '
                #asc = str(entry).replace("'", '"').replace("\\'", "'")
            sql = "UPDATE tasks SET history = '{\"history\": [%s]}' WHERE id=%d AND project_id=%d" % (data[:-2], task_id, project_id)
            # print(sql)
            result = await self.execute(sql)

    async def appendHistory(self,
                            history: list,
                            task_id: int,
                            project_id: int,
                            ):
        """
        Update the task history column.

        Args:
            history (list): The task history to update
            task_id (int): The task to update
            project_id (int): The project this task is in

        Returns:
            (bool): If it worked
        """
        # log.warning(f"updateHistory(): unimplemented!")

        data = dict()
        data['history'] = list()
        for entry in history:
            # SQL wants the string value
            if "action" in entry:
                entry['action'] = entry['action'].name
            if "is_closed" in entry:
                entry['is_closed'] = str(entry['is_closed']).lower()
            asc = str(entry).replace("'", '"').replace("\\'", "'")
            sql = "UPDATE tasks SET history = history||'[%s]'::jsonb WHERE id=%d AND project_id=%d" % (asc, task_id, project_id)
            # print(sql)
            result = await self.execute(sql)

            # Update the task status
            if "action" in entry:
                status = None
                if entry['action'] == Taskaction.VALIDATED:
                    status = Taskstatus.TASK_VALIDATED
                elif entry['action'] == Taskaction.MARKED_INVALID:
                    status = Taskstatus.TASK_INVALIDATED
                elif entry['action'] == Taskaction.MARKED_INVALID:
                    status = Taskstatus.TASK_VALIDATED
                if status:
                    result = await self.updateColumns({"status": status},
                                                      {"id": task_id,
                                                      "project_id": project_id})

    async def updateIssues(self,
                            issues: list,
                            task_id: int,
                            project_id: int,
                            ):
        """
        Update the task history column.

        Args:
            issues (list): The issues for this task
            task_id (int): The task to update
            project_id (int): The project this task is in

        Returns:
            (bool): If it worked
        """
        # log.warning(f"updateHistory(): unimplemented!")

        data = str()
        for entry in issues:
            for k, v in entry.items():
                if str(type(v))[:5] == "<enum":
                    data += f'" {v.name}", '
                else:
                    data += f'" {v}", '
                #asc = str(entry).replace("'", '"').replace("\\'", "'")
            sql = "UPDATE tasks SET issues = '{\"issues\": [%s]}' WHERE id=%d AND project_id=%d" % (data[:-2], task_id, project_id)
            # print(sql)
            result = await self.execute(sql)

    async def mapAllAPI(self,
                        project_id: int,
                        ):
        """
        Map all tasks on a project. Can only be done by the project
        manager.

        Args:
            
        Returns:
            
        """
        # FIXME use Access() class
        log.warning(f"mapAllAPI(): unimplemented!")

        return False

    async def validateAllAPI(self,
                                    project_id: int,
                                    flip: bool,
                                    ):
        """
        Validate or invalidate all tasks on a project. Can only be done
        by the project manager.

        Args:
            project_id (id): The project ID
            flip: Invalidate all tasks
            
        Returns:
            
        """
        # FIXME use Access() class
        log.warning(f"validateAllAPI(): unimplemented!")

        return False

    async def resetBadImagery(self):
        """
        Set all bad imagery tasks as ready for mapping.

        Args:

        Returns:

        """
        # FIXME use Access() class,
        log.warning(f"resetBadImageryAllAPI(): unimplemented!")

        return False

    async def resetAllAPI(self,
                                      project_id: int,
                                      ):
        """
        Reset all tasks on project back to ready, preserving history.

        Args:

        Returns:

        """
        # FIXME use Access() class,
        log.warning(f"resetAllAPI(): unimplemented!")

        return False

    async def undoMapping(self):
        """

        Args:
            
        Returns:
            
        """
        log.warning(f"undoMapping(): unimplemented!")

        return False

    async def permittedUser(self,
                            user_id: int,
                            project_id: int,
                            ):
        """
        Is user action permitted on project.

        # FIXME: See if team role is project manager

        # FIXME: See if user role is project manager

        # FIXME: See if user is org manager

        """

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
