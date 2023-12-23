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
from tm_admin.types_tm import Mappinglevel
from datetime import datetime
from tm_admin.users.users_class import UsersTable
from tm_admin.projects.projects_class import ProjectsTable

# Instantiate logger
log = logging.getLogger(__name__)

import tm_admin as tma
rootdir = tma.__path__[0]

# FIXME: For now these tests assume you have a local postgres installed. One has the TM
# database, the other for tm_admin.

user = UsersDB('localhost/testdata')
project = ProjectsDB('localhost/testdata')


def get_project_by_id():
    # project_id: int) -> Project:
    log.debug(f"get_project_by_id() unimplemented!")

def exists():
    # project_id: int) -> bool:
    log.debug(f"exists() unimplemented!")

def get_project_by_name():
    # project_id: int) -> Project:
    log.debug(f"get_project_by_name() unimplemented!")

def auto_unlock_tasks():
    # project_id: int):
    log.debug(f"auto_unlock_tasks() unimplemented!")

def delete_tasks():
    # project_id: int, tasks_ids):
    log.debug(f"delete_tasks() unimplemented!")

def get_contribs_by_day():
    # project_id: int) -> ProjectContribsDTO:
    log.debug(f"get_contribs_by_day() unimplemented!")

def get_project_dto_for_mapper():
    log.debug(f"get_project_dto_for_mapper() unimplemented!")

def get_project_tasks():
    #
    log.debug(f"get_project_tasks() unimplemented!")

def get_project_aoi():
    # project_id):
    log.debug(f"get_project_aoi() unimplemented!")

def get_project_priority_areas():
    # project_id):
    log.debug(f"get_project_priority_areas() unimplemented!")

def get_task_for_logged_in_user():
    # user_id: int):
    log.debug(f"get_task_for_logged_in_user() unimplemented!")

def get_task_details_for_logged_in_user():
    # user_id: int, preferred_locale: str):
    log.debug(f"get_task_details_for_logged_in_user() unimplemented!")

def is_user_in_the_allowed_list():
    # allowed_users: list, current_user_id: int):
    log.debug(f"is_user_in_the_allowed_list() unimplemented!")

def evaluate_mapping_permission():
    log.debug(f"evaluate_mapping_permission() unimplemented!")

def evaluate_validation_permission():
    log.debug(f"evaluate_validation_permission() unimplemented!")

def is_user_permitted_to_validate():
    # project_id, user_id):
    log.debug(f") unimplemented!")

def is_user_permitted_to_map():
    # project_id, user_id):
    log.debug(f"is_user_permitted_to_map() unimplemented!")

def get_cached_project_summary():
    log.debug(f"get_cached_project_summary() unimplemented!")

def get_project_summary():
    log.debug(f") unimplemented!")

def set_project_as_featured():
    # project_id: int):
    log.debug(f"set_project_as_featured() unimplemented!")

def unset_project_as_featured():
    # project_id: int):
    log.debug(f"unset_project_as_featured() unimplemented!")

def get_featured_projects():
    # preferred_locale):
    log.debug(f"get_featured_projects() unimplemented!")

def is_favorited():
    # project_id: int, user_id: int) -> bool:
    log.debug(f"is_favorited() unimplemented!")

def favorite():
    # project_id: int, user_id: int):
    log.debug(f"favorite() unimplemented!")

def unfavorite():
    # project_id: int, user_id: int):
    log.debug(f"unfavorite() unimplemented!")

def get_project_title():
    # project_id: int, preferred_locale: str = "en") -> str:
    log.debug(f"get_project_title() unimplemented!")

def get_project_stats():
    # project_id: int) -> ProjectStatsDTO:
    log.debug(f"get_project_stats() unimplemented!")

def get_project_user_stats():
    # project_id: int, username: str) -> ProjectUserStatsDTO:
    log.debug(f"get_project_user_stats() unimplemented!")

def get_project_teams():
    # project_id: int):
    log.debug(f"get_project_teams() unimplemented!")

def get_project_organisation():
    # project_id: int) -> Organisation:
    log.debug(f"get_project_organisation() unimplemented!")

def send_email_on_project_progress():
    # project_id):
    log.debug(f"send_email_on_project_progress() unimplemented!")
            
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

    get_project_by_id()
    exists()
    get_project_by_name()
    auto_unlock_tasks()
    delete_tasks()
    get_contribs_by_day()
    get_project_dto_for_mapper()
    get_project_tasks()
    get_project_aoi()
    get_project_priority_areas()
    get_task_for_logged_in_user()
    get_task_details_for_logged_in_user()
    is_user_in_the_allowed_list()
    evaluate_mapping_permission()
    is_user_permitted_to_map()
    #_is_user_intermediate_or_advanced()
    evaluate_validation_permission()
    is_user_permitted_to_validate()
    get_cached_project_summary()
    get_project_summary()
    set_project_as_featured()
    unset_project_as_featured()
    get_featured_projects()
    is_favorited()
    favorite()
    unfavorite()
    get_project_title()
    get_project_stats()
    get_project_user_stats()
    get_project_teams()
    get_project_organisation()
    send_email_on_project_progress()
