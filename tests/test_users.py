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
from tm_admin.users.api import UsersAPI
from tm_admin.projects.projects import ProjectsDB
from tm_admin.projects.api import ProjectsAPI
from tm_admin.types_tm import Userrole, Mappinglevel
from datetime import datetime
from tm_admin.users.users_class import UsersTable
import asyncio
from codetiming import Timer

# Instantiate logger
log = logging.getLogger(__name__)

import tm_admin as tma
rootdir = tma.__path__[0]

# FIXME: For now these tests assume you have a local postgres installed.

users = UsersAPI()
# project = ProjectsAPI()

# def get_all_users(query: UserSearchQuery):
async def test_all():
    log.debug("--- test_all() ---")
    # result = await users.getAll()
    # assert len(result) > 0
    
#def get_user_by_id(user_id: int):
async def test_by_id():
    log.debug("--- test_by_id() ---")
    id = 4606673
    # all = users.getByID(id)
    result = await users.getByID(id)
    # assert len(result) > 0
    
# def get_user_by_username(username: str):
async def test_by_name():
    log.debug("--- test_by_name() unimplemented! ---")
    name = 'Rob Savoye'
    result = await users.getByName(name)
    # assert len(result) > 0

# def add_role_to_user(admin_user_id: int, username: str, role: str):
async def test_role():
    log.debug("--- test_role() ---")
    user_id = 4606673
    role = Userrole(Userrole.USER_READ_ONLY)
    # result = await users.updateColumns({'role': role.name}, {"id": user_id})
    # assert result
    
async def get_mapping_level():
    log.debug("--- get_mapping_level() ---")
    id = 4606673        
    result = await users.getByID(id)
    # log.debug(f"mapping_level {result['mapping_level']}")
    # assert len(result) > 0

# def refresh_mapper_level() -> int:
async def set_user_mapping_level():
    log.debug("--- test_level() ---")
    user_id = 4606673
    level = Mappinglevel(1)
    result = await users.updateColumns({'mapping_level': level}, {"id": user_id})
    assert result

async def check_and_update_mapper_level():
    id = 4606673
    result = await users.getByID(id)
    index = 0
    level = 0
    # for entry in Mappinglevel._member_names_:
    #     if entry == result['mapping_level']:
    #         level = index + 1
    #     else:
    #         index += 1

    # newlevel = Mappinglevel(level + 1)
    # result = await users.updateColumn(id, {'mapping_level': newlevel.name})
    # result = await users.getByID(id)
    # # CHeck to make sure it actually incremented
    # assert len(result) > 0 and result['mapping_level'] == Mappinglevel.INTERMEDIATE.name

# def set_user_is_expert(user_id: int, is_expert: bool):
async def test_expert():
    log.debug("--- test_expert() ---")
    user_id = 4606673
    mode = True
    # result = await users.updateColumns({'is_expert': mode}, {"id": user_id})
    # assert result
    
async def test_registered():
    log.debug("--- test_registered() ---")
    start = '2015-11-20 08:36:55'
    stime = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
    end = '2023-02-07 12:28:30'
    etime =  datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
    result = await users.getRegistered(stime, etime)
    # assert result
    
async def get_project_managers():
    log.debug("--- get_project_managers() ---")
    role = Userrole(Userrole.PROJECT_MANAGER)
    # result = await users.getByWhere(f" role='{role.name}'")
    # assert len(result) == 1

async def is_user_an_admin():
    log.debug("--- get_project_managers() ---")
    id = 4606673
    # Get the entire user record
    result = await users.getByID(id)
    hits = 0
    # if result['role'] == Userrole.SUPER_ADMIN or result['role'] == Userrole.ORGANIZATION_ADMIN :
    #     hits += 1
    # assert hits == 0
    # assert len(result) == 1 # FIXME: There are ADMIN in the test data yet
        
async def is_user_validator():
    log.debug("--- is_user_validator() ---")
    id = 4606673
    role = Userrole(Userrole.VALIDATOR)
    # result = await users.getByWhere(f" role='{role.name}' AND id={id}")
    #assert len(result) == 1 # FIXME: There are VALIDATORS in the test data yet
    # assert len(result) == 0

async def get_projects_mapped():
    log.debug("--- get_projects_mapped() ---")
    id = 4606673
    result = await users.getByID(id)
    # mapped = result['projects_mapped']
    # hits = 0
    # if type(mapped) == int:
    #     hits += 1
    # elif type(mapped) == list:
    #     hits += 1
    # assert hits == 1

async def is_user_blocked():
    log.debug("--- is_user_blocked() ---")
    id = 4606673
    result = await users.getByID(id)
    # assert result['role'] != Userrole.USER_READ_ONLY
        
async def get_mapped_projects():
    """Gets all projects a user has mapped or validated on"""
    log.debug("--- get_mapped_projects() ---")
    # user_name: str, preferred_locale: str
    id = 4606673
    result = await users.getByID(id)
    # mapped = result['projects_mapped']
    mapped = [1090, 173]
    data = list()
    # for proj in mapped:
    #     record = await project.getByID(proj)
    #     data.append(record)

    # assert len(data) == 2
        
async def update_user():
    log.debug("--- update_user() ---")
    # user_id: int, osm_username: str, picture_url: str):
    id = 4606673
    # await users.updateColumn(id, {'username': 'osmfoo'})
    # await users.updateColumn(id, {'picture_url': 'no pic'})
    result = await users.getByID(id)
    # assert result['picture_url'] == 'no pic'

# FIXME: I'm not really sure of the difference of these two internal API functions.
async def register_user():
    """Creates user in DB"""
    log.debug("--- update_user() ---")
    # osm_id, username, changeset_count, picture_url, email
    # The id is generated by postgres, so we don't supply it.    
    ut = UsersTable(username='foobar', name='barfoo', picture_url='URI', email_address="bar@foo.com", mapping_level='INTERMEDIATE', role='VALIDATOR')
    # new = users.createTable(ut)
    entry = await users.getByName(ut.data['name'])
    # assert entry['id'] > 0

async def register_user_with_email():
    """Validate that user is not within the general users table."""
    log.debug("--- register_user_with_email() ---")
    # osm_id, username, changeset_count, picture_url, email
    # The id is generated by postgres, so we don't supply it.    
    ut = UsersTable(username='foobar', name='barfoo', picture_url='URI', email_address="bar@foo.com", mapping_level='INTERMEDIATE', role='VALIDATOR')
    # new = await users.createTable(ut)
    # entry = await users.getByName(ut.data['name'])
    # assert entry['id'] > 0

async def has_user_accepted_license():
    """Checks if user has accepted specified license"""
    # user_id: int, license_id: int
    log.debug("--- has_user_accepted_license() ---")
    id = 4606673
    # result = await users.getByID(id)
    # assert result['id'] == id
        
async def get_interests():
    log.debug(f"--- get_interests() ---")
    id = 4606673
    # result = await users.getColumn(id, 'interests')
    # assert len(result) > 0

async def get_projects_favorited():
    # user_id: int
    log.debug(f"--- get_projects_favorited() ---")
    id = 4606673
    # result = await users.getColumn(id, 'favorite_projects')
    # assert len(result) > 0
        
async def accept_license_terms():
    """Saves the fact user has accepted license terms"""
    # user_id: int, license_id: int
    log.debug(f"--- accept_license_terms() ---")
    user_id = 4606673
    result = await users.updateColumns({'licenses': 1}, {"id": user_id})
    assert result

async def get_general_admins():
    """Get all users that are ADMIN"""
    log.debug(f"--- get_general_admins() ---")
    # result = await users.getByWhere(f" role='WEB_ADMIN'")
    # FIXME: there are no ADMINs yet in the test data
    # assert len(result) > 0

async def filter_users():
    """Gets paginated list of users, filtered by username, for autocomplete"""
    # FIXME: this should probably be in test_projects.py
    log.debug(f"--- filter_users() ---")
    # username: str, project_id: int, page: int
    pid = 135
    # result = project.getByWhere(f" id={pid}")
    # assert len(result) > 0

async def upsert_mapped_projects():
    """Add project to mapped projects if it doesn't exist, otherwise return"""
    # user_id: int, project_id: int
    log.debug(f"--- upsert_mapped_projects() ---")
    uid = 4606673
    pid = 135
    # FIXME: for now appendColumn adds a single entry to an existing array
    # result = await users.appendColumn(uid, {'projects_mapped': pid})
    # assert result

async def update_user_details():
    # user_id: int, db: UsersDB
    log.debug(f"update_user_details() unimplemented!")

async def get_interests_stats():
    """Get all projects that the user has contributed."""
    # FIXME: this uses task history
    # user_id
    log.debug(f"get_interests_stats() unimplemented!")

async def get_detailed_stats():
    # FIXME: this uses task history
    # username: str
    log.debug(f"get_detailed_stats() unimplemented!")

async def get_countries_contributed():
    # FIXME: this uses task history
    # user_id: int
    log.debug(f"get_countries_contributed() unimplemented!")
        
async def get_contributions_by_day():
    # The TM source says "Validate that user exists",
    # FIXME: this uses task history
    # user_id: int
    log.debug(f"get_contributions_by_day() unimplemented!")

async def get_recommended_projects():
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
async def get_users():
    # db: Session, skip: int = 0, limit: int = 100):
    log.debug(f"--- get_users() unimplemented!")

async def get_user():
    # db: Session, user_id: int, db_obj: bool = False):
    log.debug(f"--- get_user() unimplemented!")

async def get_user_by_username():
    # db: Session, username: str):
    log.debug(f"--- get_user_by_username() unimplemented!")

async def convert_to_app_user():
    # db_user: db_models.DbUser):
    log.debug(f"--- convert_to_app_user() unimplemented!")

async def convert_to_app_users():
    # db_users: List[db_models.DbUser]):
    log.debug(f"--- convert_to_app_users() unimplemented!")

async def get_user_role_by_user_id():
    # db: Session, user_id: int):
    log.debug(f"--- get_user_role_by_user_id() unimplemented!")
    
async def create_user_roles():
    # user_role: user_schemas.UserRoles, db: Session):
    log.debug(f"--- create_user_roles() unimplemented!")

async def get_user_by_id():
    # db: Session, user_id: int):
    log.debug(f"--- get_user_by_id() unimplemented!")

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

    await users.initialize(args.uri)
    # project.connect("localhost/tm_admin")

    # Test TM API
    # get_user_dto_by_username()
    # get_user_dto_by_id()
    await test_by_id()
    await test_by_name()
    await test_role()
    await set_user_mapping_level()
    await test_expert()
    await test_registered()
    await get_project_managers()
    await get_mapping_level()
    await is_user_an_admin()
    await is_user_validator()
    await get_contributions_by_day()
    await get_project_managers()
    await get_general_admins()
    await update_user(),
    await get_projects_favorited()
    await get_projects_mapped()
    await register_user(),
    await get_interests_stats()
    await get_detailed_stats()
    await update_user_details()
    await filter_users()
    await is_user_blocked()
    await get_countries_contributed()
    await upsert_mapped_projects()
    await get_mapped_projects()
    await get_recommended_projects()
    await set_user_mapping_level()
    await accept_license_terms()
    await has_user_accepted_license()
    await check_and_update_mapper_level()
    await register_user_with_email()
    await get_interests()
    # is_user_the_project_author()
    # get_osm_details_for_user() # Not part of this API
    # notify_level_upgrade() # Not part of this API
    await test_all()

    # FMTM API tests
    await get_user()
    await get_user_by_username()
    await convert_to_app_user()
    await convert_to_app_users()
    await get_user_role_by_user_id()
    await create_user_roles()
    await get_user_by_id()

if __name__ == "__main__":
    """This is just a hook so this file can be run standalone during development."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
