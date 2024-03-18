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

"""
Test users API
"""

import tm_admin as tma
rootdir = tma.__path__[0]

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

# FIXME: For now these tests assume you have a local postgres installed.

users = UsersAPI()
projects = ProjectsAPI()

async def create_users(uapi):
    await uapi.deleteRecords([1, 2, 3, 4, 5])
    await uapi.resetSequence()
    user = UsersTable(id = 1, username = "foobar", name = "foo",
                  city = "Someplace", email_address = "fubr@gmail.com",
                  is_email_verified = False, is_expert = False,
                  tasks_notifications = True, role = "USER_READ_ONLY",
                  mapping_level = "BEGINNER", tasks_mapped = 0,
                  tasks_validated = 0, tasks_invalidated = 0,
                  date_registered = "2024-01-29T22:19:35.587016",
                  last_validation_date = "2024-01-29T22:19:35.587018",
                  slack_id = "barfoo", default_editor = "ID",
                  gender = 1, mentions_notifications = True,
                  projects_notifications = True,
                  projects_comments_notifications = False,
                  tasks_comments_notifications = False,
                  teams_announcement_notifications = True,
                  )
    result = await uapi.insertRecords([user])

    user = UsersTable(id = 2, username = "barfoo", name = "foobar",
                  city = "Someplace", email_address = "barfood@gmail.com",
                  is_email_verified = False, is_expert = False,
                  tasks_notifications = True, role = "PROJECT_MANAGER",
                  mapping_level = "ADVANCED", tasks_mapped = 0,
                  tasks_validated = 0, tasks_invalidated = 0,
                  date_registered = "2024-01-29T22:19:35.587016",
                  last_validation_date = "2024-01-29T22:19:35.587018",
                  slack_id = "foobared", default_editor = "ID",
                  gender = 1, mentions_notifications = True,
                  projects_notifications = True,
                  projects_comments_notifications = False,
                  tasks_comments_notifications = False,
                  teams_announcement_notifications = True,
                  )
    result = await uapi.insertRecords([user])

    user = UsersTable(id = 3, username = "barfood", name = "bar",
                  city = "Someplace", email_address = "oops@gmail.com",
                  is_email_verified = False, is_expert = False,
                  tasks_notifications = True, role = "ORGANIZATION_ADMIN",
                  mapping_level = "INTERMEDIATE", tasks_mapped = 0,
                  tasks_validated = 0, tasks_invalidated = 0,
                  date_registered = "2024-01-29T22:19:35.587016",
                  last_validation_date = "2024-01-29T22:19:35.587018",
                  slack_id = "mistake", default_editor = "ID",
                  gender = 1, mentions_notifications = True,
                  projects_notifications = True,
                  projects_comments_notifications = False,
                  tasks_comments_notifications = False,
                  teams_announcement_notifications = True,
                  )
    result = await uapi.insertRecords([user])

    user = UsersTable(id = 4, username = "test", name = "tester",
                  city = "Someplace", email_address = "nogood@gmail.com",
                  is_email_verified = False, is_expert = False,
                  tasks_notifications = True, role = "VALIDATOR",
                  mapping_level = "ADVANCED", tasks_mapped = 0,
                  tasks_validated = 0, tasks_invalidated = 0,
                  date_registered = "2024-01-29T22:19:35.587016",
                  last_validation_date = "2024-01-29T22:19:35.587018",
                  default_editor = "ID", gender = 1,
                  mentions_notifications = True,
                  projects_notifications = True,
                  projects_comments_notifications = False,
                  tasks_comments_notifications = False,
                  teams_announcement_notifications = True,
                  )
    result = await uapi.insertRecords([user])

    user = UsersTable(id = 5, username = "superbeing", name = "god",
                  city = "Someplace", email_address = "nogood@gmail.com",
                  is_email_verified = False, is_expert = False,
                  tasks_notifications = True, role = "SUPER_ADMIN",
                  mapping_level = "ADVANCED", tasks_mapped = 0,
                  tasks_validated = 0, tasks_invalidated = 0,
                  date_registered = "2024-01-29T22:19:35.587016",
                  last_validation_date = "2024-01-29T22:19:35.587018",
                  default_editor = "ID", gender = 1,
                  mentions_notifications = True,
                  projects_notifications = True,
                  projects_comments_notifications = False,
                  tasks_comments_notifications = False,
                  teams_announcement_notifications = True,
                  )
    result = await uapi.insertRecords([user])

    user_id = 1
    # We need mapped projects
    result = await uapi.updateColumns({"projects_mapped": [1]}, {"id": user_id})

    # We need favorite projects
    user_id = 1
    result = await uapi.updateColumns({"favorite_projects": [1, 2]}, {"id": user_id})
    user_id = 2
    result = await uapi.updateColumns({"favorite_projects": [2, 3]}, {"id": user_id})
    user_id = 3
    result = await uapi.updateColumns({"favorite_projects": [3, 4]}, {"id": user_id})

#
# These endpoints are for the REST API
#

async def UsersRestAPI():
    "Get user information by id"
    log.debug("--- UsersRestAPI() ---")
    user_id = 1
    result = await users.getByID(user_id)
    assert len(result) > 0

async def UsersAllAPI():
    "Get paged list of all usernames"
    log.debug("--- UsersAllAPI() unimplemented! ---")
    paged = False
    count = 20
    username = "foo"
    role = Userrole(Userrole.MAPPER)
    level = Mappinglevel(Mappinglevel.BEGINNER)
    result = await users.getPagedUsers(paged, count, username, role, level)

async def UsersQueriesUsernameAPI():
    "Get user information by OpenStreetMap username"
    log.debug("--- UsersQueriesUsernameAPI() ---")
    username = "foobar"
    result = await users.getByName(username)
    assert len(result) > 0

async def UsersQueriesUsernameFilterAPI():
    "Get paged lists of users matching OpenStreetMap username filter"
    username = "foobar"
    log.debug("--- UsersQueriesUsernameFilterAPI() Unimplemented! ---")
    page = 2
    username= "rob"
    # FIXME: this works fine with real data, but not with the small
    # testdata we create.
    # result = await users.getFilterUsers(username, page)
    # print(result)
    # result = await users.getFilterUsers(username, page)
    # print(result)
    project_id = 1
    # result = await users.getFilterUsers(username, page, project_id, True)
    # print(result)
    # result = await users.getFilterUsers(username, page, project_id)
    # print(result)

async def UsersQueriesOwnLockedAPI():
    "Gets any locked task on the project for the logged in user"
    user_id = 1
    log.debug("--- UsersQueriesOwnLockedAPI() unimplemented! ---")

async def UsersQueriesOwnLockedDetailsAPI():
    "Gets details of any locked task for the logged in user"
    log.debug("--- UsersQueriesOwnLockedDetailsAPI() unimplemented! ---")

async def UsersQueriesFavoritesAPI():
    "Get projects favorited by a user"
    log.debug("--- UsersQueriesFavoritesAPI() ---")
    user_id = 1
    result = await users.getFavoriteProjects(user_id)
    assert len(result) > 0

async def UsersQueriesInterestsAPI():
    "Get interests by username"
    log.debug("--- UsersQueriesInterestsAPI()  ---")
    username = "foobar"
    user_id = 2
    result = await users.getColumns({"interests"}, {"id": user_id})
    # FIXME: It is not clear if this returns interests IDs or the
    # interests data.
    assert len(result) > 0

async def UsersRecommendedProjectsAPI():
    "Get recommended projects for a user"
    log.debug("--- UsersRecommendedProjectsAPI() unimplemented! ---")
    username = "foobar"
    # FIXME: It is not clear if this returns project IDs or the
    # project data.

async def UsersStatisticsAPI():
    "Get detailed stats about a user by OpenStreetMap username"
    log.debug("--- UsersStatisticsAPI() unimplemented! ---")
    username = "bar"
    # result = await users.getStats(username

async def UsersStatisticsInterestsAPI():
    "Get rate of contributions from a user given their interests"
    log.debug("--- UsersStatisticsInterestsAPI() unimplemented! ---")
    username = "oob"
    # result = await getInterestsStats(username)

async def UsersStatisticsAllAPI():
    "Get stats about users registered within a period of time"
    log.debug("--- UsersStatisticsAllAPI() unimplemented! ---")
    start = '2015-11-20 08:36:55'
    stime = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
    end = '2023-02-07 12:28:30'
    etime =  datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
    # result = await getAllStats(stime, etime)

async def UsersTasksAPI():
    """
    Get a list of tasks a user has interacted with.

    criteria to sort by. The supported options are action_date,
    The default value is action_date.
    """
    log.debug("--- UsersTasksAPI() unimplemented! ---")

#
# These endpoints come from the TM backend/services directory.
#

# def get_all_users(query: UserSearchQuery):
async def test_all():
    log.debug("--- test_all() Unimplemented ---")
    # result = await users.getColumns(['*'])
    # assert len(result) > 0

#def get_user_by_id(user_id: int):
async def test_by_id():
    log.debug("--- test_by_id() ---")
    user_id = 1
    result = await users.getByID(user_id)
    assert len(result) > 0

# def get_user_by_username(username: str):
async def test_by_name():
    log.debug("--- test_by_name() unimplemented! ---")
    name = 'foobar'
    result = await users.getByName(name)
    assert len(result) > 0

async def get_mapping_level():
    log.debug("--- get_mapping_level() ---")
    user_id = 3
    result = await users.getColumns(['mapping_level'], {"id": user_id})
    assert len(result) > 0

# def refresh_mapper_level() -> int:
async def set_user_mapping_level():
    log.debug("--- test_level() ---")
    user_id = 1
    level = Mappinglevel(1)
    result = await users.updateColumns({'mapping_level': level}, {"id": user_id})
    assert result

# def set_user_is_expert(user_id: int, is_expert: bool):
async def test_expert():
    log.debug("--- test_expert() ---")
    user_id = 3
    result = await users.getColumns(['is_expert'], {"id": user_id})
    assert len(result) > 0

async def get_project_managers():
    log.debug("--- get_project_managers() ---")
    role = Userrole(Userrole.PROJECT_MANAGER)
    result = await users.getColumns(['id'], {"role": role})
    assert len(result) > 0

async def is_user_an_admin():
    log.debug("--- is_user_an_admin() ---")
    # first user is not an admin
    user_id = 1
    noresult = await users.getRole(user_id)
    user_id = 5
    result = await users.getRole(user_id)
    assert noresult == Userrole.USER_READ_ONLY and result == Userrole.SUPER_ADMIN

async def is_user_validator():
    log.debug("--- is_user_validator() ---")
    # first user is not a validator
    user_id = 2
    noresult = await users.getRole(user_id)
    user_id = 4
    # but this user is a validator
    result = await users.getRole(user_id)
    assert noresult == Userrole.PROJECT_MANAGER and result == Userrole.VALIDATOR

async def is_user_blocked():
    log.debug("--- is_user_blocked() ---")
    user_id = 1
    result = await users.getBlocked(user_id)
    assert result

async def get_interests():
    log.debug("--- get_interests() ---")
    user_id = 2
    result = await users.getColumns({"interests"}, {"id": user_id})
    assert len(result) > 0

async def get_projects_favorited():
    # user_id: int
    log.debug("--- get_projects_favorited() ---")
    user_id = 3
    result = await users.getColumns({"favorite_projects"}, {"id": user_id})
    assert len(result) > 0

async def get_projects_mapped():
    log.debug("--- get_projects_mapped() ---")
    user_id = 3
    result = await users.getColumns({"projects_mapped"}, {"id": user_id})
    assert len(result) > 0

async def get_mapped_projects():
    """Gets all projects a user has mapped or validated on"""
    log.debug("--- get_mapped_projects() ---")
    # user_name: str, preferred_locale: str
    # FIXME: this appears to be the same as get_projects_mapped(). The current
    # TM code doesn't check validation, which can be done by quering the
    # validated_by column in the tasks table.

async def get_recommended_projects():
    """Gets all projects a user has mapped or validated on"""
    log.debug(f"get_recommended_projects() unimplemented!")
    # FIXME: this appears to be the same as get_projects_mapped(). The current
    # TM code doesn't check validation, which can be done by quering the
    # validated_by column in the tasks table.

async def update_user():
    log.debug("--- update_user() unimplemented")
    # user_id: int, osm_username: str, picture_url: str):
    id = 3

# FIXME: I'm not really sure of the difference of these two internal API functions.
async def register_user():
    """Creates user in DB"""
    log.debug("--- update_user() ---")
    user_id = 1
    # osm_id, username, changeset_count, picture_url, email
    # The id is generated by postgres, so we don't supply it.
    ut = UsersTable(username='foobar', name='barfoo', picture_url='URI',
                    email_address="bar@foo.com",
                    mapping_level='INTERMEDIATE', role='VALIDATOR')
    #await users.updateColumns(ut, {"id": user_id})
    result = await users.getByName('foobar')
    # print(result)

async def register_user_with_email():
    """Validate that user is not within the general users table."""
    log.debug("--- register_user_with_email() ---")
    # osm_id, username, changeset_count, picture_url, email
    # The id is generated by postgres, so we don't supply it.
    ut = UsersTable(username='foobar', name='barfoo', picture_url='URI',
                    email_address="bar@foo.com",
                    mapping_level='INTERMEDIATE', role='VALIDATOR')
    # new = await users.createTable(ut)
    # entry = await users.getByName(ut.data['name'])
    # assert entry['id'] > 0

async def test_registered():
    log.debug("--- test_registered() ---")
    start = '2015-11-20 08:36:55'
    stime = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
    end = '2023-02-07 12:28:30'
    etime =  datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
    result = await users.getRegistered(stime, etime)
    # assert result

async def has_user_accepted_license():
    """Checks if user has accepted specified license"""
    # user_id: int, license_id: int
    log.debug("--- has_user_accepted_license() ---")
    user_id = 1
    license_id = 1
    result = await users.getColumns({"licenses"}, {"id": user_id})
    assert license_id in result[0]['licenses']

async def accept_license_terms():
    """Saves the fact user has accepted license terms"""
    # user_id: int, license_id: int
    log.debug(f"--- accept_license_terms() ---")
    user_id = 1
    license_id = 1
    result = await users.updateColumns({'licenses': [license_id]}, {"id": user_id})
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
    uid = 3
    pid = 135
    # FIXME: for now appendColumn adds a single entry to an existing array
    # result = await users.appendColumn(uid, {'projects_mapped': pid})
    # assert result

async def check_and_update_mapper_level():
    log.debug(f"check_and_update_mapper_level() unimplemented!")

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

# This one seems silly, and needs no database access
# def is_user_the_project_author(user_id: int, author_id: int)

# These both require accessing the OSM server, which we're not going to do yet.
# def get_osm_details_for_user(username: str)
# def notify_level_upgrade(user_id: int, username: str, level: str)

# We don't need to test these they are for sqlachemy, which we're not using. Instead
# we use the UsersTable() to represent the table schema
# def get_user_dto_by_username():
# def get_user_dto_by_id(user: int, request_user: int):

#
# FMTM API tests
#
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

    await users.initialize(args.uri, projects)
    await projects.initialize(args.uri, users)

    # Populate the table with test data
    await create_users(users)

    # These tests are from the TM backend
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

    # These tests are from the TM REST API
    await UsersQueriesUsernameFilterAPI()
    await UsersRestAPI()
    await UsersAllAPI()
    await UsersQueriesUsernameAPI()
    await UsersQueriesOwnLockedAPI()
    await UsersQueriesFavoritesAPI()
    await UsersQueriesInterestsAPI()
    await UsersRecommendedProjectsAPI()
    await UsersStatisticsAPI()
    await UsersStatisticsInterestsAPI()
    await UsersStatisticsAllAPI()
    await UsersTasksAPI()
    
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
