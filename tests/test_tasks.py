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
from tm_admin.tasks.api import TasksAPI

# Instantiate logger
log = logging.getLogger(__name__)

import tm_admin as tma
rootdir = tma.__path__[0]

task = TasksAPI()

# FIXME: For now these tests assume you have a local postgres installed. One has the TM
# database, the other for tm_admin.

def get_task():
    log.debug(f"--- get_task() unimplemented!")
    # task_id: int, project_id: int) -> Task:

def _is_task_undoable():
    """Determines if the current task status can be undone by the logged in user"""
    log.debug(f"--- _is_task_undoable() unimplemented!")
    #logged_in_user_id: int, task: Task) -> bool:

def lock_task_for_mapping():
    log.debug(f"--- lock_task_for_mapping() unimplemented!")
    # lock_task_dto: LockTaskDTO) -> TaskDTO:

def unlock_task_after_mapping():
    """Unlocks the task and sets the task history appropriately"""
    log.debug(f"--- unlock_task_after_mapping() unimplemented!")
    # mapped_task: MappedTaskDTO) -> TaskDTO:

def stop_mapping_task():
    # stop_task: StopMappingTaskDTO) -> TaskDTO:
    log.debug(f"--- stop_mapping_task() unimplemented!")

    """Unlocks the task and revert the task status to the last one"""
def get_task_locked_by_user():
    log.debug(f"--- get_task_locked_by_user() unimplemented!")
    # project_id: int, task_id: int, user_id: int) -> Task:

def add_task_comment():
    """Adds the comment to the task history"""
    log.debug(f"--- add_task_comment() unimplemented!")
    # task_comment: TaskCommentDTO) -> TaskDTO:

def generate_gpx():
    log.debug(f"--- generate_gpx() unimplemented!")
    # project_id: int, task_ids_str: str, timestamp=None):

def generate_osm_xml():
    log.debug(f"--- generate_osm_xml() unimplemented!")
    # project_id: int, task_ids_str: str) -> str:

    """Generate xml response suitable for loading into JOSM.  A sample output file is in"""
def undo_mapping():
    log.debug(f"--- undo_mapping() unimplemented!")
    #project_id: int, task_id: int, user_id: int, preferred_locale: str = "en"

def map_all_tasks():
    log.debug(f"--- map_all_tasks() unimplemented!")
    # project_id: int, user_id: int):

    """Marks all tasks on a project as mapped"""
def reset_all_badimagery():
    log.debug(f"--- reset_all_badimagery() unimplemented!")
    # project_id: int, user_id: int):

    """Marks all bad imagery tasks ready for mapping"""
def lock_time_can_be_extended():
    log.debug(f"--- lock_time_can_be_extended() unimplemented!")
    # project_id, task_id, user_id):
    
    # task = Task.get(task_id, project_id)
def extend_task_lock_time():
    log.debug(f"--- extend_task_lock_time() unimplemented!")
    #extend_dto: ExtendLockTimeDTO):

def get_task_as_dto():
    log.debug(f"--- get_task_as_dto( unimplemented!")
    # task_id: int,
    
# FMTM API tests
def get_task_count_in_project():
    # db: Session, project_id: int):
    log.debug(f"--- get_task_count_in_project() unimplemented!")

def get_task_lists():
    # db: Session, project_id: int):
    log.debug(f"--- get_task_lists() unimplemented!")

def get_tasks():
    #
    log.debug(f"--- get_tasks() unimplemented!")

def get_task():
    # db: Session, task_id: int, db_obj: bool = False):
    log.debug(f"--- get_task() unimplemented!")

def update_task_status():
    # db: Session, user_id: int, task_id: int, new_status: TaskStatus):
    log.debug(f"--- update_task_status() unimplemented!")

def update_qrcode():
    log.debug(f"--- update_qrcode() unimplemented!")

def create_task_history_for_status_change():
    log.debug(f"--- create_task_history_for_status_change() unimplemented!")

def convert_to_app_history():
    # db_histories: List[db_models.DbTaskHistory]):
    log.debug(f"--- convert_to_app_history() unimplemented!")

def convert_to_app_task():
    # db_task: db_models.DbTask):
    log.debug(f"--- convert_to_app_task() unimplemented!")

def convert_to_app_tasks():
    # db_tasks: List[db_models.DbTask]):
    log.debug(f"--- convert_to_app_tasks() unimplemented!")

def get_qr_codes_for_task():
    log.debug(f"--- get_qr_codes_for_task() unimplemented!")

def get_task_by_id():
    # db: Session, task_id: int):
    log.debug(f"--- get_task_by_id() unimplemented!")

def update_task_files():
    log.debug(f"--- update_task_files() unimplemented!")

def edit_task_boundary():
    # db: Session, task_id: int, boundary: str):
    log.debug(f"--- edit_task_boundary() unimplemented!")

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
    # task = TasksDB(args.uri)
    await task.connect(args.uri)
    # project = ProjectsDB(args.uri)
    
    get_task()
    get_task_as_dto()
    _is_task_undoable()
    lock_task_for_mapping()
    unlock_task_after_mapping()
    stop_mapping_task()
    get_task_locked_by_user()
    add_task_comment()
    generate_gpx()
    generate_osm_xml()
    undo_mapping()
    map_all_tasks()
    reset_all_badimagery()
    lock_time_can_be_extended()
    extend_task_lock_time()

    # FMTM API tests
    
    get_tasks()
    get_task()
    update_task_status()
    update_qrcode()
    create_task_history_for_status_change()
    convert_to_app_history()
    convert_to_app_task()
    convert_to_app_tasks()
    get_qr_codes_for_task()
    get_task_by_id()
    update_task_files()
    edit_task_boundary()
