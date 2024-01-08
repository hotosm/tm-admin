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
from tm_admin.users.users import UsersDB
from tm_admin.projects.projects import ProjectsDB
from tm_admin.types_tm import Userrole, Mappinglevel
from datetime import datetime
from tm_admin.users.users_class import UsersTable
from tm_admin.tasks.tasks_class import TasksTable
from tm_admin.tasks.tasks import TasksDB

# Instantiate logger
log = logging.getLogger(__name__)

import tm_admin as tma
rootdir = tma.__path__[0]

user = UsersDB()
project = ProjectsDB()
task = TasksDB()

def lock_tasks_for_validation():
    log.debug(f"--- lock_tasks_for_validation unimplemented! ---")
    # validation_dto: LockForValidationDTO) -> TaskDTOs:
def _user_can_validate_task():
    log.debug(f"--- _user_can_validate_task unimplemented! ---")
    # user_id: int, mapped_by: int) -> bool:
def unlock_tasks_after_validation():
    log.debug(f"--- unlock_tasks_after_validation unimplemented! ---")
def stop_validating_tasks():
    log.debug(f"--- stop_validating_tasks unimplemented! ---")
    # stop_validating_dto: StopValidationDTO) -> TaskDTOs:
def get_tasks_locked_by_user():
    log.debug(f"--- get_tasks_locked_by_user unimplemented! ---")
    # project_id: int, unlock_tasks, user_id: int):
def get_mapped_tasks_by_user():
    log.debug(f"--- get_mapped_tasks_by_user unimplemented! ---")
    # project_id: int) -> MappedTasks:
def get_user_invalidated_tasks():
    log.debug(f"--- get_user_invalidated_tasks unimplemented! ---")
def invalidate_all_tasks():
    log.debug(f"--- invalidate_all_tasks unimplemented! ---")
    # project_id: int, user_id: int):
def validate_all_tasks():
    log.debug(f"--- validate_all_tasks unimplemented! ---")
    # project_id: int, user_id: int):
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

    # user = UsersDB(args.uri)
    # project = ProjectsDB(args.uri)
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

