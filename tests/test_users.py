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

# Instantiate logger
log = logging.getLogger(__name__)

import tm_admin as tma
rootdir = tma.__path__[0]

# FIXME: For now these tests assume you have a local postgres installed. One has the TM
# database, the other for tm_admin.


#UPDATE users SET favorite_projects = ARRAY[1,2,16,5];

user = None
project = None

# def get_all_users(query: UserSearchQuery):
def test_all():
    log.debug("--- test_all() ---")
    result = user.getAll()
    assert len(result) > 0
    
#def get_user_by_id(user_id: int):
def test_by_id():
    log.debug("--- test_by_id() ---")
    id = 4606673
    # all = user.getByID(id)
    result = user.getByWhere(f" id='{id}'")
    assert len(result) > 0
    
# def get_user_by_username(username: str):
def test_by_name():
    log.debug("--- test_by_name() unimplemented! ---")
    name = 'Rob Savoye'
    result = user.getByName(name)
    assert len(result) > 0

# def add_role_to_user(admin_user_id: int, username: str, role: str):
def test_role():
    log.debug("--- test_role() ---")
    id = 4606673
    role = Userrole(Userrole.USER_READ_ONLY)
    result = user.updateColumn(id, {'role': role.name})
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
    start = '2015-11-20 08:36:55'
    stime = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
    end = '2023-02-07 12:28:30'
    etime =  datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
    result = user.getRegistered(stime, etime)
    assert result
    
def get_project_managers():
    log.debug("--- get_project_managers() ---")
    role = Userrole(Userrole.PROJECT_MANAGER)
    result = user.getByWhere(f" role='{role.name}'")
    # assert len(result) == 1

def is_user_an_admin():
    log.debug("--- get_project_managers() ---")
    id = 4606673
    # Get the entire user record
    result = user.getByID(id)
    hits = 0
    if result['role'] == Userrole.SUPER_ADMIN or result['role'] == Userrole.ORGANIZATION_ADMIN :
        hits += 1
    assert hits == 0
    # assert len(result) == 1 # FIXME: There are ADMIN in the test data yet
        
def is_user_validator():
    log.debug("--- is_user_validator() ---")
    id = 4606673
    role = Userrole(Userrole.VALIDATOR)
    result = user.getByWhere(f" role='{role.name}' AND id={id}")
    #assert len(result) == 1 # FIXME: There are VALIDATORS in the test data yet
    assert len(result) == 0

def get_projects_mapped():
    log.debug("--- get_projects_mapped() ---")
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
    log.debug("--- is_user_blocked() ---")
    id = 4606673
    result = user.getByID(id)
    assert result['role'] != Userrole.USER_READ_ONLY
        
def get_mapped_projects():
    """Gets all projects a user has mapped or validated on"""
    log.debug("--- get_mapped_projects() ---")
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
        
def update_user():
    log.debug("--- update_user() ---")
    # user_id: int, osm_username: str, picture_url: str):
    id = 4606673
    user.updateColumn(id, {'osm_username': 'osmfoo'})
    user.updateColumn(id, {'picture_url': 'no pic'})
    result = user.getByID(id)
    assert result['picture_url'] == 'no pic'

# FIXME: I'm not really sure of the difference of these two internal API functions.
def register_user():
    """Creates user in DB"""
    log.debug("--- update_user() ---")
    # osm_id, username, changeset_count, picture_url, email
    # The id is generated by postgres, so we don't supply it.    
    ut = UsersTable(username='foobar', name='barfoo', picture_url='URI', email_address="bar@foo.com", mapping_level='INTERMEDIATE', role='VALIDATOR')
    new = user.createTable(ut)
    entry = user.getByName(ut.data['name'])
    assert entry['id'] > 0

def register_user_with_email():
    """Validate that user is not within the general users table."""
    log.debug("--- register_user_with_email() ---")
    # osm_id, username, changeset_count, picture_url, email
    # The id is generated by postgres, so we don't supply it.    
    ut = UsersTable(username='foobar', name='barfoo', picture_url='URI', email_address="bar@foo.com", mapping_level='INTERMEDIATE', role='VALIDATOR')
    new = user.createTable(ut)
    entry = user.getByName(ut.data['name'])
    assert entry['id'] > 0

def has_user_accepted_license():
    """Checks if user has accepted specified license"""
    # user_id: int, license_id: int
    log.debug("--- has_user_accepted_license() ---")
    id = 4606673
    result = user.getByID(id)
    assert result['id'] == id
        
def get_interests():
    log.debug(f"--- get_interests() ---")
    id = 4606673
    result = user.getColumn(id, 'interests')
    assert len(result) > 0

def get_projects_favorited():
    # user_id: int
    log.debug(f"--- get_projects_favorited() ---")
    id = 4606673
    result = user.getColumn(id, 'favorite_projects')
    # assert len(result) > 0
        
def accept_license_terms():
    """Saves the fact user has accepted license terms"""
    # user_id: int, license_id: int
    log.debug(f"--- accept_license_terms() ---")
    id = 4606673
    result = user.updateColumn(id, {'licenses': {1}})
    assert result

def get_general_admins():
    """Get all users that are ADMIN"""
    log.debug(f"--- get_general_admins() ---")
    result = user.getByWhere(f" role='WEB_ADMIN'")
    # FIXME: there are no ADMINs yet in the test data
    # assert len(result) > 0

def filter_users():
    """Gets paginated list of users, filtered by username, for autocomplete"""
    # FIXME: this should probably be in test_projects.py
    log.debug(f"--- filter_users() ---")
    # username: str, project_id: int, page: int
    pid = 135
    result = project.getByWhere(f" id={pid}")
    assert len(result) > 0

def upsert_mapped_projects():
    """Add project to mapped projects if it doesn't exist, otherwise return"""
    # user_id: int, project_id: int
    log.debug(f"--- upsert_mapped_projects() ---")
    uid = 4606673
    pid = 135
    # FIXME: for now appendColumn adds a single entry to an existing array
    result = user.appendColumn(uid, {'projects_mapped': pid})
    assert result

def update_user_details():
    # user_id: int, db: UsersDB
    log.debug(f"update_user_details() unimplemented!")

def get_interests_stats():
    """Get all projects that the user has contributed."""
    # FIXME: this uses task history
    # user_id
    log.debug(f"get_interests_stats() unimplemented!")

def get_detailed_stats():
    # FIXME: this uses task history
    # username: str
    log.debug(f"get_detailed_stats() unimplemented!")

def get_countries_contributed():
    # FIXME: this uses task history
    # user_id: int
    log.debug(f"get_countries_contributed() unimplemented!")
        
def get_contributions_by_day():
    # The TM source says "Validate that user exists",
    # FIXME: this uses task history
    # user_id: int
    log.debug(f"get_contributions_by_day() unimplemented!")

def get_recommended_projects():
    """Gets all projects a user has mapped or validated on"""
    # user_name: str, preferred_locale: str
    # Get all projects that the user has contributed
    # Get all campaigns for all contributed projects.
    # Get projects with given campaign tags but without user contributions.
    # Get only user mapping level projects.
    log.debug(f"get_recommended_projects() unimplemented!")

# This one seems silly, and needs no database access
# def is_user_the_project_author(user_id: int, author_id: int)

# These both require accessing the OSM server, which we're not going to do yet.
# def get_osm_details_for_user(username: str)
# def notify_level_upgrade(user_id: int, username: str, level: str)

# We don't need to test these they are for sqlachemy, which we're not using. Instead
# we use the UsersTable() to represent the table schema
# def get_user_dto_by_username():
# def get_user_dto_by_id(user: int, request_user: int):

# test FMTM API    
def get_users():
    # db: Session, skip: int = 0, limit: int = 100):
    log.debug(f"--- get_users() unimplemented!")

def get_user():
    # db: Session, user_id: int, db_obj: bool = False):
    log.debug(f"--- get_user() unimplemented!")

def get_user_by_username():
    # db: Session, username: str):
    log.debug(f"--- get_user_by_username() unimplemented!")

def convert_to_app_user():
    # db_user: db_models.DbUser):
    log.debug(f"--- convert_to_app_user() unimplemented!")

def convert_to_app_users():
    # db_users: List[db_models.DbUser]):
    log.debug(f"--- convert_to_app_users() unimplemented!")

def get_user_role_by_user_id():
    # db: Session, user_id: int):
    log.debug(f"--- get_user_role_by_user_id() unimplemented!")
    
def create_user_roles():
    # user_role: user_schemas.UserRoles, db: Session):
    log.debug(f"--- create_user_roles() unimplemented!")

def get_user_by_id():
    # db: Session, user_id: int):
    log.debug(f"--- get_user_by_id() unimplemented!")

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

    # Test TM API
    # get_user_dto_by_username()
    # get_user_dto_by_id()
    test_by_id()
    test_by_name()
    test_role()
    set_user_mapping_level()
    test_expert()
    test_registered()
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
    is_user_blocked()
    get_countries_contributed()
    upsert_mapped_projects()
    get_mapped_projects()
    get_recommended_projects()
    set_user_mapping_level()
    accept_license_terms()
    has_user_accepted_license()
    check_and_update_mapper_level()
    register_user_with_email()
    get_interests()
    # is_user_the_project_author()
    # get_osm_details_for_user() # Not part of this API
    # notify_level_upgrade() # Not part of this API
    test_all()

    # FMTM API tests
    get_user()
    get_user_by_username()
    convert_to_app_user()
    convert_to_app_users()
    get_user_role_by_user_id()
    create_user_roles()
    get_user_by_id()
