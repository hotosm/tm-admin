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
from tm_admin.types_tm import Userrole, Mappinglevel, Taskstatus
from datetime import datetime
from tm_admin.users.users_class import UsersTable
from tm_admin.tasks.tasks_class import TasksTable
from tm_admin.tasks.tasks import TasksDB
from tm_admin.users.users import UsersDB
from tm_admin.tasks.api import TasksAPI
from tm_admin.projects.projects import ProjectsDB
import asyncio
from codetiming import Timer

# Instantiate logger
log = logging.getLogger(__name__)

import tm_admin as tma
rootdir = tma.__path__[0]

user = UsersDB()
task = TasksDB()
project = ProjectsDB()

async def get_user_invalidated_tasks():
    """Get invalidated tasks either mapped or invalidated by the user"""
    log.debug(f"--- get_user_invalidated_tasks ---")
    hits = 0
    # use a UID for a mapper tha exists and has invalidations
    uid = 12487721
    result = await task.getByWhere(f"mapped_by={uid} AND invalidation_history IS NOT NULL")
    if len(result) > 0:
        hits += 1

    # use a UID for a mapper tha exists, but has no invalidated tasks
    id = 4606673
    result = await task.getByWhere(f"mapped_by={uid} AND invalidation_history IS NOT NULL")
    if len(result) == 0:
        hits += 1

    # use a UID that shouldn't exist
    result = await task.getByWhere(f"mapped_by=999999 AND invalidation_history IS NOT NULL")
    if len(result) == 0:
        hits += 1

    assert hits != 3

async def get_mapped_tasks_by_user():
    """Get all mapped tasks on the project grouped by user"""
    # project_id: int) -> MappedTasks:
    log.debug(f"--- get_mapped_tasks_by_user ---")

    # This starts by querying for all task.status and
    # history.action_text are marked MAPPED.
    hits = 0
    pid = 12597
    result = await task.getByWhere(f" project_id={pid} AND task_status='TASK_STATUS_MAPPED' ORDER BY mapped_by")
    if len(result) > 0 and  len(result[0][0]) > 10 :
        hits += 1

    # assert hits == 1

async def get_tasks_locked_by_user():
    """
    Returns tasks specified by project id and unlock_tasks
    list if found and locked for validation by user.
    """
    # project_id: int, unlock_tasks[], user_id: int):
    log.debug(f"--- get_tasks_locked_by_user ---")
    # result = task.getByWhere(f"mapped_by=999999 AND invalidation_history IS NOT NULL")
    hits = 0
    pid = 12597
    id = 4606673
    tasks = [4872, 4873, 4874, 4875]
    result = await task.getByWhere(f" project_id={pid} AND task_status='TASK_LOCKED_FOR_MAPPING' ORDER BY mapped_by")
    if len(result) > 0 and  len(result[0][0]) > 10 :
        hits += 1

    # assert hits == 1

async def _user_can_validate_task():
    log.debug(f"--- _user_can_validate_task ---")
    # user_id: int, mapped_by: int) -> bool:
    hits = 0
    valid = 10479599
    uid = 4606673
    # result = await user.getByWhere(f" id={valid} OR id={uid}")
    # map = result[0][0]
    # val = result[1][0]
    # FIXME: this test won't work right till there is test data
    # if val['role'] == Userrole.PROJECT_MANAGER or val['role'] == Userrole.SUPER_ADMIN or val['role'] == Userrole.VALIDATOR:
    #     # validator must have the right role
    #     hits += 1

    # if map['id'] != val['id']:
    #     hits += 1

    # FIXME: this test won't work right till there is test data
    # assert hits == 1

async def invalidate_all_tasks():
    # project_id: int, user_id: int):
    log.debug(f"--- invalidate_all_tasks unimplemented! ---")

async def validate_all_tasks():
    log.debug(f"--- validate_all_tasks unimplemented! ---")
    # project_id: int, user_id: int):

async def lock_tasks_for_validation():
    """Lock supplied tasks for validation for a project"""
    log.debug(f"--- lock_tasks_for_validation ---")
    hits = 0
    pid = 6649
    result = await task.getByWhere(f" task_status!='TASK_STATUS_MAPPED' AND task_status!='TASK_INVALIDATED' AND task_status!='BADIMAGERY' AND project_id={pid}")

    # for entry in result[0]:
    #     tid = entry['id']
    #     status = Taskstatus.TASK_LOCKED_FOR_VALIDATION
    #     result = await task.updateColumn(tid, {'task_status': status})
    #     result = await task.getColumn(tid, 'task_status')
    #     if result[0][0] == "TASK_LOCKED_FOR_VALIDATION":
    #         hits += 1

    # assert hits == 1

async def unlock_tasks_after_validation():
    """Unlocks supplied tasks after validation"""
    log.debug(f"--- unlock_tasks_after_validation ---")
    hits = 0
    pid = 6649
    result = await task.getByWhere(f" task_status!='TASK_STATUS_MAPPED' AND task_status!='TASK_INVALIDATED' AND task_status!='BADIMAGERY' AND project_id={pid}")

    # for entry in result[0]:
    #     tid = entry['id']
    #     status = Taskstatus.TASK_VALIDATED
    #     task.updateColumn(tid, {'task_status': status.name})
    #     result = await task.getColumn(tid, 'task_status')
    #     if result[0][0] == "TASK_VALIDATED":
    #         hits += 1

    # assert hits == 1

async def stop_validating_tasks():
    log.debug(f"--- stop_validating_tasks unimplemented! ---")
    # stop_validating_dto: StopValidationDTO) -> TaskDTOs:

async def get_task_mapping_issues():
    log.debug(f"--- get_task_mapping_issues unimplemented! ---")
    # task_to_unlock: dict):

async def revert_user_tasks():
    log.debug(f"--- revert_user_tasks unimplemented! ---")
    # revert_dto: RevertUserTasksDTO):

# FIXME: For now these tests assume you have a local postgres installed. One has the TM
# database, the other for tm_admin.

async def main():
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
        # format=("%(asctime)s.%(msecs)03d [%(levelname)s] " "%(name)s | %(funcName)s:%(lineno)d | %(message)s"),
        format=("[%(levelname)s] " "%(name)s | %(funcName)s:%(lineno)d | %(message)s"),
        datefmt="%y-%m-%d %H:%M:%S",
        stream=sys.stdout,
    )

    await user.connect(args.uri)
    await project.connect(args.uri)
    await task.connect(args.uri)

    await lock_tasks_for_validation()
    await _user_can_validate_task()
    await unlock_tasks_after_validation()
    await stop_validating_tasks()
    await get_tasks_locked_by_user()
    await get_mapped_tasks_by_user()
    await get_user_invalidated_tasks()
    await invalidate_all_tasks()
    await validate_all_tasks()
    await get_task_mapping_issues()
    await revert_user_tasks()

if __name__ == "__main__":
    """This is just a hook so this file can be run standalone during development."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())

