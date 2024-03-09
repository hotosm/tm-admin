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
# from tm_admin.users.users_proto import UsersMessage
#from tm_admin.yamlfile import YamlFile
# from tm_admin.users.users import UsersDB
# from tm_admin.projects.projects import ProjectsDB
from tm_admin.types_tm import Taskstatus, Taskaction, Mapping_issue
from datetime import datetime
from tm_admin.tasks.tasks_class import TasksTable
from tm_admin.tasks.task_history_class import Task_historyTable
from tm_admin.tasks.task_issues_class import Task_issuesTable
from tm_admin.tasks.task_invalidation_history_class import Task_invalidation_historyTable
from tm_admin.tasks.api import TasksAPI
import asyncio
from codetiming import Timer

# Instantiate logger
log = logging.getLogger(__name__)

tasks = TasksAPI()

# FIXME: For now these tests assume you have a local postgres installed. One has the TM
# database, the other for tm_admin.

async def create_tasks():
    await tasks.deleteRecords([1, 2, 3])
    await tasks.resetSequence()
    project_id = 1
    user_id = 1
    tl = list()
    tl.append(TasksTable(id = 1, project_id = 1,
                        project_task_name = "testing, 1,2,3",
                        is_square = False,
                        task_status = Taskstatus.READY))
    task_id = 1
    project_id = 1
    history = list()
    history.append({"action": Taskaction.RELEASED_FOR_MAPPING,
                   "action_text": "validated task",
                   "action_date": "2024-01-25 10:50:56.140958",
                   "user_id": user_id})
    await tasks.updateHistory(history, task_id, project_id)

    task_id = 1
    history = list()
    history.append({"action": Taskaction.LOCKED_FOR_MAPPING,
                "action_text": "locked for mapping",
                "action_date": "2024-01-23 10:50:56.140958",
                "user_id": user_id})

    history.append({"action": Taskaction.LOCKED_FOR_VALIDATION,
                "action_text": "marked mapped",
                "action_date": "2024-01-24 10:50:56.140958",
                "user_id": user_id})

    history.append({"action": Taskaction.VALIDATED,
                "action_text": "marked mapped",
                "action_date": "2024-01-25 10:50:56.140958",
                "user_id": user_id})
    await tasks.appendHistory(history, task_id, project_id)

    tl.append(TasksTable(id = 2, project_id = 1,
                        project_task_name = "testing, 1,2,3",
                        is_square = True,
                        task_status = Taskstatus.READY))

    # Insert all the tables
    result = await tasks.insertRecords(tl)

    # Now add some data to the jsonb columns
    history.append({"action": Taskaction.RELEASED_FOR_MAPPING,
                   "action_text": "validated task",
                   "action_date": "2024-01-25 10:50:56.140958",
                   "user_id": user_id})
    await tasks.updateHistory(history, task_id, project_id)

    task_id = 1
    project_id = 1
    history = list()
    history.append({"action": Taskaction.RELEASED_FOR_MAPPING,
                   "action_text": "validated task",
                   "action_date": "2024-01-25 10:50:56.140958",
                   "user_id": user_id})
    await tasks.updateHistory(history, task_id, project_id)

    task_id = 1
    project_id = 1
    history = list()
    history.append({"action": Taskaction.LOCKED_FOR_MAPPING,
                "action_text": "locked for mapping",
                "action_date": "2024-01-23 10:50:56.140958",
                "user_id": user_id})

    history.append({"action": Taskaction.LOCKED_FOR_VALIDATION,
                "action_text": "marked mapped",
                "action_date": "2024-01-24 10:50:56.140958",
                "user_id": user_id})

    history.append({"action": Taskaction.VALIDATED,
                "action_text": "marked mapped",
                "action_date": "2024-01-25 10:50:56.140958",
                "user_id": user_id})
    await tasks.appendHistory(history, task_id, project_id)

    # Add some mapping issues
    issuses = list()
    issuses.append({"issue": Mapping_issue.FEATURE_GEOMETRY, "count": 3})
    issuses.append({"issue": Mapping_issue.MISSED_FEATURE, "count": 10})
    await tasks.updateIssues(issuses, task_id, project_id)

    # Add some invalidation entries
    mapper_id = 1
    mapped_date = "2024-01-25 10:50:56.140958";
    invalidator_id = 2
    invalidated_date = "2024-01-25 10:50:56.140958";
    validator_id = 3
    validated_date = "2024-01-25 10:50:56.140958";
    updated_date = "2024-01-25 10:50:56.140958";

    validation = {"is_closed": False, "mapper_id": mapper_id,
                "invalidator_id": invalidator_id,
                "validator_id": validator_id,
                "updated_date": updated_date,
                }
    await tasks.appendHistory([validation], task_id, project_id)

async def get_task():
    # task_id: int, project_id: int) -> Task:
    log.debug(f"--- get_task() unimplemented!")
    task_id = 1
    # result = await tasks.getByID(task_id)
    # print(result)

async def _is_task_undoable():
    """Determines if the current task status can be undone by the logged in user"""
    log.debug(f"--- _is_task_undoable() unimplemented!")
    #logged_in_user_id: int, task: Task) -> bool:

async def lock_task_for_mapping():
    log.debug(f"--- lock_task_for_mapping() unimplemented!")
    user_id = 1
    task_id = 1
    project_id = 3
    status = Taskstatus(Taskstatus.TASK_LOCKED_FOR_MAPPING)
    result = await tasks.changeStatus(user_id, task_id, project_id, status)
    # lock_task_dto: LockTaskDTO) -> TaskDTO:

async def unlock_task_after_mapping():
    """Unlocks the task and sets the task history appropriately"""
    log.debug(f"--- unlock_task_after_mapping() unimplemented!")
    user_id = 1
    task_id = 1
    project_id = 3
    status = Taskstatus(Taskstatus.TASK_LOCKED_FOR_MAPPING)
    result = await tasks.changeStatus(user_id, task_id, project_id, status)
    # mapped_task: MappedTaskDTO) -> TaskDTO:

async def stop_mapping_task():
    # stop_task: StopMappingTaskDTO) -> TaskDTO:
    log.debug(f"--- unlock_task_after_mapping() unimplemented!")
    user_id = 1
    task_id = 2
    project_id = 3
    status = Taskstatus(Taskstatus.TASK_LOCKED_FOR_MAPPING)
    result = await tasks.changeStatus(user_id, task_id, project_id, status)
    log.debug(f"--- stop_mapping_task() unimplemented!")

    """Unlocks the task and revert the task status to the last one"""
async def get_task_locked_by_user():
    log.debug(f"--- get_task_locked_by_user() unimplemented!")
    # project_id: int, task_id: int, user_id: int) -> Task:

async def add_task_comment():
    """Adds the comment to the task history"""
    log.debug(f"--- add_task_comment() unimplemented!")
    # task_comment: TaskCommentDTO) -> TaskDTO:

async def generate_gpx():
    log.debug(f"--- generate_gpx() unimplemented!")
    # project_id: int, task_ids_str: str, timestamp=None):

async def generate_osm_xml():
    log.debug(f"--- generate_osm_xml() unimplemented!")
    # project_id: int, task_ids_str: str) -> str:

    """Generate xml response suitable for loading into JOSM.  A sample output file is in"""
async def undo_mapping():
    log.debug(f"--- undo_mapping() unimplemented!")
    #project_id: int, task_id: int, user_id: int, preferred_locale: str = "en"

async def map_all_tasks():
    log.debug(f"--- map_all_tasks() unimplemented!")
    result = await tasks.markAllMapped()
    # project_id: int, user_id: int):

    """Marks all tasks on a project as mapped"""
async def reset_all_badimagery():
    log.debug(f"--- reset_all_badimagery() unimplemented!")
    result = await tasks.resetBadImagery()
    # project_id: int, user_id: int):

    """Marks all bad imagery tasks ready for mapping"""

async def lock_time_can_be_extended():
    log.debug(f"--- lock_time_can_be_extended() unimplemented!")
    # project_id, task_id, user_id):

    # task = Task.get(task_id, project_id)
async def extend_task_lock_time():
    log.debug(f"--- extend_task_lock_time() unimplemented!")
    #extend_dto: ExtendLockTimeDTO):

# FMTM API tests
async def get_task_count_in_project():
    # db: Session, project_id: int):
    log.debug(f"--- get_task_count_in_project() unimplemented!")

async def get_task_lists():
    # db: Session, project_id: int):
    log.debug(f"--- get_task_lists() unimplemented!")

async def get_tasks():
    #
    log.debug(f"--- get_tasks() unimplemented!")

async def get_task():
    # db: Session, task_id: int, db_obj: bool = False):
    log.debug(f"--- get_task() unimplemented!")

async def update_task_status():
    # db: Session, user_id: int, task_id: int, new_status: TaskStatus):
    log.debug(f"--- update_task_status() unimplemented!")

async def update_qrcode():
    log.debug(f"--- update_qrcode() unimplemented!")

async def create_task_history_for_status_change():
    log.debug(f"--- create_task_history_for_status_change() unimplemented!")

async def convert_to_app_history():
    # db_histories: List[db_models.DbTaskHistory]):
    log.debug(f"--- convert_to_app_history() unimplemented!")

async def convert_to_app_task():
    # db_task: db_models.DbTask):
    log.debug(f"--- convert_to_app_task() unimplemented!")

async def convert_to_app_tasks():
    # db_tasks: List[db_models.DbTask]):
    log.debug(f"--- convert_to_app_tasks() unimplemented!")

async def get_qr_codes_for_task():
    log.debug(f"--- get_qr_codes_for_task() unimplemented!")

async def get_task_by_id():
    # db: Session, task_id: int):
    log.debug(f"--- get_task_by_id() unimplemented!")

async def update_task_files():
    log.debug(f"--- update_task_files() unimplemented!")

async def edit_task_boundary():
    # db: Session, task_id: int, boundary: str):
    log.debug(f"--- edit_task_boundary() unimplemented!")

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", nargs="?", const="0", help="verbose output")
    parser.add_argument("-u", "--uri", default='localhost/testdata', help="Database URI")
    args = parser.parse_args()
    # if verbose, dump to the terminal.
    log_level = os.getenv("LOG_LEVEL", default="INFO")
    if args.verbose is not None:
        log_level = logging.DEBUG

    logging.basicConfig(
        level=log_level,
        # format=("%(asctime)s.%(msecs)03d [%(levelname)s] " "%(name)s | %(funcName)s:%(lineno)d | %(message)s"),
        format=("[%(levelname)s] " "%(name)s | %(funcName)s:%(lineno)d | %(message)s"),
        datefmt="%y-%m-%d %H:%M:%S",
        stream=sys.stdout,
    )

    # user = UsersDB(args.uri)
    # task = TasksDB(args.uri)
    await tasks.initialize(args.uri)
    await create_tasks()
    # project = ProjectsDB(args.uri)
    
    await get_tasks()
    # await get_task_as_dto()
    await _is_task_undoable()
    await lock_task_for_mapping()
    await unlock_task_after_mapping()
    await stop_mapping_task()
    await get_task_locked_by_user()
    await add_task_comment()
    await generate_gpx()
    await generate_osm_xml()
    await undo_mapping()
    await map_all_tasks()
    await reset_all_badimagery()
    await lock_time_can_be_extended()
    await extend_task_lock_time()

    # FMTM API tests
    await get_tasks()
    await get_task()
    await update_task_status()
    await update_qrcode()
    await create_task_history_for_status_change()
    await convert_to_app_history()
    await convert_to_app_task()
    await convert_to_app_tasks()
    await get_qr_codes_for_task()
    await get_task_by_id()
    await update_task_files()
    await edit_task_boundary()

if __name__ == "__main__":
    """This is just a hook so this file can be run standalone during development."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
