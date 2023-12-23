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

# Instantiate logger
log = logging.getLogger(__name__)

import tm_admin as tma
rootdir = tma.__path__[0]

# FIXME: For now these tests assume you have a local postgres installed. One has the TM
# database, the other for tm_admin.

user = UsersDB('localhost/testdata')
project = ProjectsDB('localhost/testdata')

# def get_all_users(query: UserSearchQuery):
def test_all():
    log.debug("--- test_all() ---")
    all = user.getAll()
    # assert len(all) > 0
    
#def get_user_by_id(user_id: int):
def test_by_id():
    log.debug("--- test_by_id() ---")
    id = 4606673
    # all = user.getByID(id)
    result = user.getByWhere(f" id='{id}'")
    assert len(result) > 0
    
# def get_user_by_username(username: str):
def test_by_name():
    log.debug("--- test_by_name() ---")
    name = 'rsavoye'
    # all = user.getByName(name)
    # assert len(all) > 0

# def add_role_to_user(admin_user_id: int, username: str, role: str):
def test_role():
    log.debug("--- test_role() ---")
    id = 4606673
    role = Userrole(Userrole.ADMIN)
    #result = user.updateRole(id, role)
    return user.updateColumn(id, {'role': role.name})
    assert result
    
def get_mapping_level():
    log.debug("--- get_mapping_level() ---")
    id = 4606673        
    result = user.getByID(id)
    log.debug(f"mapping_level {result['mapping_level']}")
    assert len(result) > 0

# def refresh_mapper_level() -> int:
def set_user_mapping_level():
    log.debug("--- test_level() ---")
    id = 4606673
    level = Mappinglevel(1)
    # result = user.updateMappingLevel(id, level)
    result = user.updateColumn(id, {'mapping_level': level.name})
    assert result

def check_and_update_mapper_level():
    id = 4606673
    result = user.getByID(id)
    index = 0
    level = 0
    for entry in Mappinglevel._member_names_:
        if entry == result['mapping_level']:
            level = index + 1
        else:
            index += 1

    newlevel = Mappinglevel(level + 1)
    result = user.updateColumn(id, {'mapping_level': newlevel.name})
    result = user.getByID(id)
    # CHeck to make sure it actually incremented
    assert len(result) > 0 and result['mapping_level'] == Mappinglevel.INTERMEDIATE.name

# def set_user_is_expert(user_id: int, is_expert: bool):
def test_expert():
    log.debug("--- test_expert() ---")
    id = 4606673
    mode = True
    result = user.updateColumn(id, {'is_expert': mode})
    assert result
    
def test_registered():
    log.debug("--- test_registered() ---")
    start = '2020-11-20 08:36:55'
    stime = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
    end = '2023-02-07 12:28:30'
    etime =  datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
    result = user.getRegistered(stime, etime)
    assert result
    
def get_project_managers():
    log.debug("--- get_project_managers() ---")
    role = Userrole(Userrole.ADMIN)
    result = user.getByWhere(f" role='{role.name}'")
    # assert len(result) == 1

def is_user_an_admin():
    log.debug("--- get_project_managers() ---")
    id = 4606673
    role = Userrole(Userrole.ADMIN)
    result = user.getByWhere(f" role='{role.name}' AND id={id}")
    # assert len(result) == 1 # FIXME: There are ADMIN in the test data yet
    assert len(result) == 1
        
def is_user_validator():
    log.debug("--- is_user_validator() ---")
    id = 4606673
    role = Userrole(Userrole.VALIDATOR)
    result = user.getByWhere(f" role='{role.name}' AND id={id}")
    #assert len(result) == 1 # FIXME: There are VALIDATORS in the test data yet
    assert len(result) == 0

def get_projects_mapped():
    id = 4606673
    result = user.getByID(id)
    mapped = result['projects_mapped']
    hits = 0
    if type(mapped) == int:
        hits += 1
    elif type(mapped) == list:
        hits += 1
    assert hits == 1

def is_user_blocked():
    id = 4606673
    result = user.getByID(id)
    assert result['role'] != Userrole.USER_READ_ONLY
        
def get_contributions_by_day():
    # user_id: int
    pass

def get_general_admins():
    pass
    
def update_user():
    # user_id: int, osm_username: str, picture_url: str):
    pass

def get_projects_favorited():
    # user_id: int
    pass

def register_user():
    # osm_id, username, changeset_count, picture_url, email
    pass

#def get_user_dto_by_username():
#        pass
        
#def get_user_dto_by_id(user: int, request_user: int):
#        pass
        
def get_interests_stats():
    # user_id
        pass
        
def get_detailed_stats():
    # username: str
        pass
        
def update_user_details():
    # user_id: int, db: UsersDB
        pass
        
def filter_users():
    # username: str, project_id: int, page: int
        pass
        
def is_user_the_project_author():
    # user_id: int, author_id: int
        pass
        
def get_countries_contributed():
    # user_id: int
        pass
        
def upsert_mapped_projects():
    # user_id: int, project_id: int
        pass
        
def get_mapped_projects():
    # user_name: str, preferred_locale: str
    id = 4606673
    result = user.getByID(id)
    # mapped = result['projects_mapped']
    mapped = [1090, 173]
    data = list()
    for proj in mapped:
        record = project.getByID(proj)
        data.append(record)

    assert len(data) == 2
        
def get_recommended_projects():
    # user_name: str, preferred_locale: str
    # Get all projects that the user has contributed
    # Get all campaigns for all contributed projects.
    # Get projects with given campaign tags but without user contributions.
    # Get only user mapping level projects.
    pass
        
def accept_license_terms():
    # user_id: int, license_id: int
        pass
        
def has_user_accepted_license():
    # user_id: int, license_id: int
        pass
        
# def get_osm_details_for_user():
#     # username: str
#         pass
        
def notify_level_upgrade():
    # user_id: int, username: str, level: str
        pass
        
def register_user_with_email():
    # db: UsersDB
        pass
        
def get_interests():
        pass        

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
    
    # get_user_dto_by_username()
    # get_user_dto_by_id()
    test_by_id()

    test_by_name()

    test_role()

    set_user_mapping_level()

    test_expert()

    # test_registered()

    get_project_managers()

    get_mapping_level()

    is_user_an_admin()

    is_user_validator()

    get_contributions_by_day()
    get_project_managers()
    get_general_admins()
    update_user(),
    get_projects_favorited()
    get_projects_mapped()
    register_user(),
    get_interests_stats()
    get_detailed_stats()
    update_user_details()
    filter_users()
    is_user_the_project_author()
    is_user_blocked()
    get_countries_contributed()
    upsert_mapped_projects()
    get_mapped_projects()
    get_recommended_projects()
    set_user_mapping_level()
    accept_license_terms()
    has_user_accepted_license()
    # get_osm_details_for_user() # Not part of this API
    check_and_update_mapper_level()
    notify_level_upgrade(),
    register_user_with_email()
    get_interests()

    test_all()
    
