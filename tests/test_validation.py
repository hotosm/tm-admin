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
from tm_admin.projects.projects import ProjectsDB

# Instantiate logger
log = logging.getLogger(__name__)

import tm_admin as tma
rootdir = tma.__path__[0]

user = UsersDB()
task = TasksDB()

def get_user_invalidated_tasks():
    """Get invalidated tasks either mapped or invalidated by the user"""
    log.debug(f"--- get_user_invalidated_tasks ---")
    hits = 0
    # use a UID for a mapper tha exists and has invalidations
    uid = 12487721
    result = task.getByWhere(f"mapped_by={uid} AND invalidation_history IS NOT NULL")
    if len(result) > 0:
        hits += 1

    # use a UID for a mapper tha exists, but has no invalidated tasks
    id = 4606673
    result = task.getByWhere(f"mapped_by={uid} AND invalidation_history IS NOT NULL")
    if len(result) == 0:
        hits += 1

    # use a UID that shouldn't exist
    result = task.getByWhere(f"mapped_by=999999 AND invalidation_history IS NOT NULL")
    if len(result) == 0:
        hits += 1

    assert hits != 3

def get_mapped_tasks_by_user():
    """Get all mapped tasks on the project grouped by user"""
    # project_id: int) -> MappedTasks:
    log.debug(f"--- get_mapped_tasks_by_user ---")

    # This starts by querying for all task.status and
    # history.action_text are marked MAPPED.
    hits = 0
    pid = 12597
    result = task.getByWhere(f" project_id={pid} AND task_status='TASK_STATUS_MAPPED' ORDER BY mapped_by")
    if len(result) > 0 and  len(result[0][0]) > 10 :
        hits += 1

    assert hits == 1

def get_tasks_locked_by_user():
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
    result = task.getByWhere(f" project_id={pid} AND task_status='TASK_LOCKED_FOR_MAPPING' ORDER BY mapped_by")
    if len(result) > 0 and  len(result[0][0]) > 10 :
        hits += 1

    assert hits == 1

def _user_can_validate_task():
    log.debug(f"--- _user_can_validate_task ---")
    # user_id: int, mapped_by: int) -> bool:
    hits = 0
    valid = 10479599
    uid = 4606673
    result = user.getByWhere(f" id={valid} OR id={uid}")
    map = result[0][0]
    val = result[1][0]
    # FIXME: this test won't work right till there is test data
    if val['role'] == Userrole.PROJECT_MANAGER or val['role'] == Userrole.SUPER_ADMIN or val['role'] == Userrole.VALIDATOR:
        # validator must have the right role
        hits += 1

    if map['id'] != val['id']:
        hits += 1

    # FIXME: this test won't work right till there is test data
    assert hits == 1

def invalidate_all_tasks():
    # project_id: int, user_id: int):
    log.debug(f"--- invalidate_all_tasks unimplemented! ---")

def validate_all_tasks():
    log.debug(f"--- validate_all_tasks unimplemented! ---")
    # project_id: int, user_id: int):

def lock_tasks_for_validation():
    """Lock supplied tasks for validation for a project"""
    log.debug(f"--- lock_tasks_for_validation ---")
    hits = 0
    pid = 6649
    result = task.getByWhere(f" task_status!='TASK_STATUS_MAPPED' AND task_status!='TASK_INVALIDATED' AND task_status!='BADIMAGERY' AND project_id={pid}")

    for entry in result[0]:
        tid = entry['id']
        status = Taskstatus.TASK_LOCKED_FOR_VALIDATION
        result = task.updateColumn(tid, {'task_status': status})
        result = task.getColumn(tid, 'task_status')
        if result[0][0] == "TASK_LOCKED_FOR_VALIDATION":
            hits += 1

    assert hits == 1

def unlock_tasks_after_validation():
    """Unlocks supplied tasks after validation"""
    log.debug(f"--- unlock_tasks_after_validation ---")
    hits = 0
    pid = 6649
    result = task.getByWhere(f" task_status!='TASK_STATUS_MAPPED' AND task_status!='TASK_INVALIDATED' AND task_status!='BADIMAGERY' AND project_id={pid}")

    for entry in result[0]:
        tid = entry['id']
        status = Taskstatus.TASK_LOCKED_FOR_VALIDATION
        result = task.updateColumn(tid, {'task_status': status})
        result = task.getColumn(tid, 'task_status')
        if result[0][0] == "TASK_LOCKED_FOR_VALIDATION":
            hits += 1

    assert hits == 1

def stop_validating_tasks():
    log.debug(f"--- stop_validating_tasks unimplemented! ---")
    # stop_validating_dto: StopValidationDTO) -> TaskDTOs:

def get_task_mapping_issues():
    log.debug(f"--- get_task_mapping_issues unimplemented! ---")
    # task_to_unlock: dict):

def revert_user_tasks():
    log.debug(f"--- revert_user_tasks unimplemented! ---")
    # revert_dto: RevertUserTasksDTO):

# FIXME: For now these tests assume you have a local postgres installed. One has the TM
# database, the other for tm_admin.

if __name__ == "__main__":
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

    user = UsersDB(args.uri)
    project = ProjectsDB(args.uri)
    task = TasksDB(args.uri)

    lock_tasks_for_validation()
    _user_can_validate_task()
    unlock_tasks_after_validation()
    stop_validating_tasks()
    get_tasks_locked_by_user()
    get_mapped_tasks_by_user()
    get_user_invalidated_tasks()
    invalidate_all_tasks()
    validate_all_tasks()
    get_task_mapping_issues()
    revert_user_tasks()

