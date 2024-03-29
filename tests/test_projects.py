#!/usr/bin/python3

# Copyright (c) 2022, 2023, 1024 Humanitarian OpenStreetMap Team
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
from tm_admin.types_tm import Roles, Mappinglevel, Permissions
from datetime import datetime
from tm_admin.users.users_class import UsersTable
from tm_admin.projects.projects_class import ProjectsTable
from tm_admin.access import Roles
import asyncio
from codetiming import Timer
from tm_admin.projects.api import ProjectsAPI
import typing
import tm_admin
from shapely.geometry import Polygon, Point, shape
import test_tasks
import test_users

# Instantiate logger
log = logging.getLogger(__name__)

import tm_admin as tma
rootdir = tma.__path__[0]

projects = ProjectsAPI()
users = tm_admin.users.api.UsersAPI()
tasks = tm_admin.tasks.api.TasksAPI()

# FIXME: For now these tests assume you have a local postgres installed.

# These tests are for the API endpoints
async def create_projects(papi):
    """
    Create a project. We don't need any valid geometries for this test.

    The id column defaults to auto-increment. TM doesn't have any ids below
    100, so we can use the 0-100 range for testing on a live database.
    """
    await papi.deleteRecords([1, 2])
    await papi.resetSequence()
    coords = ((0., 0.), (0., 1.), (1., 1.), (1., 0.), (0., 0.))
    geom = Polygon(coords)
    center = Point(1.0, -1.0)
    pt = ProjectsTable(id = 1, name = "Hello", author_id = 1, geometry = geom, centroid = center,
                        created = '2021-12-15 09:58:02.672236', organisation_id = 1,
                        task_creation_mode = 'GRID', status = 'DRAFT', featured = "false",
                        mapping_level = 'BEGINNER', priority_areas = [1, 2, 3])
    result = await papi.insertRecords([pt])

    pt = ProjectsTable(id=2, name="World!", author_id = 1, geometry = geom, centroid = center,
                        created = '2022-12-15 09:58:02.672236', featured = "true",
                        task_creation_mode = 'CREATE_ROADS', status = 'PUBLISHED',
                        mapping_level = 'ADVANCED', priority_areas = [1],
                        organisation_id = 1)
    result = await papi.insertRecords([pt])

    role =  Roles(Roles.MAPPER)
    teams = {"team_id": 1, "role": role}
    project_id = 1
    result = await papi.updateColumns({"members": teams}, {"id": project_id})

    # Add some allowed users
    user_id = 1
    # FIXME: this is now a jsonb column
    #result = await projects.updateColumns({"allowed_users": user_id}, {"id": project_id})

# These tests are for basic table management
async def delete_project():
    """
    Delete a project from the database.

    Returns:
        (bool): True or False
    """
    pt = 1
    result = await projects.delete(pt)
    assert result

async def update_project():
    # Create a project
    # returns True or False
    geom = Polygon()
    center = Point()
    pt = ProjectsTable(id=0, author_id=2, geometry=geom, centroid=center,
                        created='2022-10-15 09:58:02.672236',
                        task_creation_mode='UPLOAD', status='PUBLISHED',
                        mapping_level='BEGINNER', teams={2, 3, 4})
    result = await projects.update(pt)
    assert result

async def get_team_role():
    log.debug(f"--- get_team_role() ---")
    project_id = 1
    team_id = 1
    result = await projects.getTeamRole(project_id, team_id)
    # print(result)
    assert result == Roles.MAPPER

# These endpoint tests come from the TM backend
async def get_project_by_id():
    # project_id: int) -> Project:
    log.debug(f"--- get_project_by_id() ---")
    id = 1
    # all = user.getByID(id)
    result = await projects.getByID(id)
    # print(result)
    assert len(result) > 0

async def exists():
    # project_id: int) -> bool:
    log.debug(f"--- exists() ---")
    id = 2
    # all = user.getByID(id)
    result = await projects.getByID(id)
    assert len(result) > 0

async def get_project_by_name():
    # project_id: int) -> Project:
    log.debug(f"--- get_project_by_name() ---")
    name = 'Hello'
    result = await projects.getByName(name)
    assert len(result) > 0

async def get_project_priority_areas():
    # project_id):
    log.debug(f"--- get_project_priority_areas() ---")
    project_id = 1
    # result = await projects.getPriorityAreas(project_id)
    data = await projects.getColumns(['priority_areas'], {"id": project_id})
    areas =  data[0]['priority_areas']
    # print(result)
    assert len(areas) > 0

async def get_project_organisation():
    # project_id: int) -> Organisation:
    log.debug(f"--- get_project_organisation() ---")
    project_id = 1
    # result = await projects.getOrganization(project_id)
    data = await projects.getColumns(['organisation_id'], {"id": project_id})
    org_id =  data[0]['organisation_id']
    # print(result)
    assert org_id > 0

async def get_project_aoi():
    # project_id):
    log.debug(f"--- get_project_aoi() ---")
    project_id = 1
    result = await projects.getAOI(project_id)
    # print(result)
    assert type(result) == Polygon

async def get_project_title():
    # project_id: int, preferred_locale: str = "en") -> str:
    log.debug(f"--- get_project_title() ---")
    project_id = 2
    data = await projects.getColumns(['name'],  {"id": project_id})
    name = data[0]['name']
    # result = await projects.getName(project_id)
    # print(result)
    assert len(name) > 0

async def get_featured_projects():
    log.debug(f"--- get_featured_projects() ---")
    result = await projects.getColumns(['id'],  {"featured": "true"})
    # FIXME: this always fails because there are no projects with this
    # set to a value, everything is the f=default, false.
    # result = await projects.getByWhere(f" featured IS NOT NULL")
    # assert len(result) > 0

async def get_project_teams():
    # project_id: int):
    log.debug(f"--- get_project_teams() ---")
    project_id = 1
    teams = await projects.getColumns(['members'], {"id": project_id})
    #teams = data[0]['teams']
    assert len(teams) > 0

async def unset_project_as_featured():
    # project_id: int):
    log.debug(f"--- unset_project_as_featured() ---")
    project_id = 2
    result = await projects.updateColumns({'featured': "false"}, {"id": project_id})
    assert result > 0

async def set_project_as_featured():
    # project_id: int):
    log.debug(f"--- set_project_as_featured() ---")
    pid = 2
    result = await projects.updateColumns({'featured': "true"}, {"id": project_id})
    assert result > 0

##########################
# FIXME: Partially implemented
async def get_project_tasks():
    # project_id):
    log.debug(f"--- get_project_tasks() ---")
    pid = 1
    # result = await tasks.getByWhere(f" project_id={pid}")
    # assert len(result) > 0

async def is_user_permitted_to_validate():
    # project_id, user_id):
    log.debug(f"-- is_user_permitted_to_validate() ---")
    id = 1
    # result = await users.getColumn(id, 'role')
    # FIXME: This only works if the user has the right role
    # assert len(result) > 0 and result[0][0] == Userrole.VALIDATOR
    # assert len(result) > 0

async def is_user_permitted_to_map():
    # project_id, user_id):
    log.debug(f"--- is_user_permitted_to_map() ---")
    id = 1
    # result = await user.getColumn(id, 'role')
    # FIXME: This only works if the user has the right role
    # assert len(result) > 0 and result[0][0] != Userrole.USER_READ_ONLY
    # assert len(result) > 0

async def is_favorited():
    # project_id: int, user_id: int) -> bool:
    log.debug(f"--- is_favorited() ---")
    uid = 1               # My TM account ID
    pid = 5
    # result = await user.getColumn(uid, 'favorite_projects')
    # FIXME: this only works with our manually inserted
    # project IDs. The testdata needs to be updated.

    # assert len(result) > 0

async def favorite():
    # project_id: int, user_id: int):
    log.debug(f"--- favorite() ---")
    uid = 1               # My TM account ID
    pid = 5
    # result = await user.appendColumn(uid, {'favorite_projects': pid})
    # assert len(result) > 0

async def unfavorite():
    # project_id: int, user_id: int):
    log.debug(f"--- unfavorite() ---")
    uid = 1               # My TM account ID
    pid = 1
    # result = await user.removeColumn(uid, {'favorite_projects': pid})
    # assert result

async def set_project_as_featured():
    # project_id: int):
    log.debug(f"--- set_project_as_featured() ---")
    pid = 2
    # result = await project.updateColumn(pid, {'featured': True})
    # assert result

async def evaluate_mapping_permission():
    # project_id: int, user_id: int, mapping_permission: int
    log.debug(f"evaluate_mapping_permission()")
    breakpoint()
    uid = 1
    pid = 2
    perm = Permissions.ANY
    # userrole = user.getColumn(uid, 'teams')
    # team = await user.getColumn(uid, 'team_members')
    # mapperms = await project.getColumn(pid, 'mapping_permission')

    #result = team.getByWhere(f" id={uid}")
    #print(result)
    allowed_roles = [
            Teamroles.TEAM_MAPPER,
            Teamroles.TEAM_VALIDATOR,
            Teamroles.PROJECT_MANAGER,
        ]

async def evaluate_validation_permission():
    log.debug(f"evaluate_validation_permission() unimplemented!")

async def auto_unlock_tasks():
    # project_id: int):
    log.debug(f"auto_unlock_tasks() unimplemented!")

async def delete_tasks():
    # project_id: int, tasks_ids):
    # FIXME: this requires the Tasks and Task History tables
    log.debug(f"delete_tasks() unimplemented!")

async def get_contribs_by_day():
    # project_id: int) -> ProjectContribsDTO:
    # FIXME: This needs the Task History Table
    log.debug(f"get_contribs_by_day() unimplemented!")

async def get_task_for_logged_in_user():
    # user_id: int):
    log.debug(f"get_task_for_logged_in_user() unimplemented!")

async def get_task_details_for_logged_in_user():
    # user_id: int, preferred_locale: str):
    log.debug(f"get_task_details_for_logged_in_user() unimplemented!")

async def get_cached_project_summary():
    log.debug(f"get_cached_project_summary() unimplemented!")

async def get_project_summary():
    log.debug(f"get_project_summary() unimplemented!")

async def get_project_stats():
    # project_id: int) -> ProjectStatsDTO:
    log.debug(f"get_project_stats() unimplemented!")

async def get_project_user_stats():
    # project_id: int, username: str) -> ProjectUserStatsDTO:
    log.debug(f"get_project_user_stats() unimplemented!")

async def send_email_on_project_progress():
    # project_id):
    log.debug(f"send_email_on_project_progress() unimplemented!")

# This one seems silly, and needs no database access
# def is_user_in_the_allowed_list():

# we use the UsersTable() to represent the table schema
# def get_project_dto_for_mapper():

# FMTM API tests
async def get_projects():
    log.debug(f"--- FMTM get_projects() unimplemented")
    # result = await user.getAll()
    # assert len(result) > 0

async def get_project():
    # db: Session, project_id: int):
    log.debug(f"--- FMTM get_project() unimplemented")
    id = 150
    # result = await project.getByWhere(f" id='{id}'")
    # assert len(result) > 0

# async def get_project_by_id():
#     # db: Session, project_id: int):
#     log.debug(f"--- FMTM get_project_by_id() unimplemented!")
#     id = 150
#     result = await project.getByWhere(f" id='{id}'")

async def get_project_geometry():
    # db: Session, project_id: int):
    log.debug(f"--- FMTM get_project_geometry() unimplemented")
    pid = 150
    # result = await project.getColumn(pid, 'geometry')
    # FIXME: this should test the geometry to make
    # sure it's valid
    # assert len(result) > 0

async def get_task_geometry():
    # db: Session, project_id: int):
    log.debug(f"--- FMTM get_task_geometry() ---")
    tid = 150
    # result = await task.getColumn(tid, 'geometry')
    # FIXME: this should test the geometry to make
    # sure it's valid
    # assert len(result) > 0

async def get_project_summaries():
    log.debug(f"--- FMTM get_project_summaries() unimplemented!")

async def get_project_by_id_w_all_tasks():
    # db: Session, project_id: int):
    log.debug(f"--- FMTM get_project_by_id_w_all_tasks() unimplemented!")

async def get_project_info_by_id():
    # db: Session, project_id: int):
    log.debug(f"--- FMTM get_project_info_by_id() unimplemented!")

async def delete_project_by_id():
    # db: Session, project_id: int):
    log.debug(f"--- FMTM delete_project_by_id() unimplemented!")

async def partial_update_project_info():
    log.debug(f"--- FMTM partial_update_project_info() unimplemented!")

async def update_project_info():
    log.debug(f"--- FMTM update_project_info() unimplemented!")

async def create_project_with_project_info():
    log.debug(f"--- FMTM create_project_with_project_info() unimplemented!")

async def upload_xlsform():
    log.debug(f"--- FMTM upload_xlsform() unimplemented!")

async def update_multi_polygon_project_boundary():
    log.debug(f"--- FMTM update_multi_polygon_project_boundary() unimplemented!")

async def preview_tasks():
    # boundary: str, dimension: int):
    log.debug(f"--- FMTM preview_tasks() unimplemented!")

async def update_project_boundary():
    log.debug(f"--- FMTM update_project_boundary() unimplemented!")

async def read_xlsforms():
    log.debug(f"--- FMTM read_xlsforms() unimplemented!")

async def get_odk_id_for_project():
    # db: Session, project_id: int):
    log.debug(f"--- FMTM get_odk_id_for_project() unimplemented!")

async def upload_custom_data_extracts():
    log.debug(f"--- FMTM upload_custom_data_extracts() unimplemented!")

async def get_project_features_geojson():
    # db: Session, project_id: int):
    log.debug(f"--- FMTM get_project_features_geojson() unimplemented!")

async def get_project_features():
    # db: Session, project_id: int, task_id: int = None):
    log.debug(f"--- FMTM get_project_features() unimplemented!")

async def add_features_into_database():
    log.debug(f"--- FMTM add_features_into_database() unimplemented!")

async def update_project_form():
    log.debug(f"--- FMTM update_project_form() unimplemented!")

async def update_odk_credentials():
    log.debug(f"--- FMTM update_odk_credentials() unimplemented!")

async def get_extracted_data_from_db():
    # db: Session, project_id: int, outfile: str):
    log.debug(f"--- FMTM get_extracted_data_from_db() unimplemented!")

async def get_project_tiles():
    log.debug(f"--- FMTM get_project_tiles() unimplemented!")

async def get_mbtiles_list():
    # db: Session, project_id: int):
    log.debug(f"--- FMTM get_mbtiles_list() unimplemented!")

async def update_project_location_info():
    log.debug(f"--- FMTM update_project_location_info() unimplemented!")

# def get_extract_completion_count():
# def get_osm_extracts(boundary: str):
# def get_shape_from_json_str(feature: str, error_detail: str):
# def get_dbqrcode_from_file(zip, qr_filename: str, error_detail: str):
# def get_outline_from_geojson_file_in_zip(
# def get_json_from_zip(zip, filename: str, error_detail: str):
# def create_task_grid(db: Session, project_id: int, delta: int):
# def generate_task_files_wrapper(project_id, task, xlsform, form_type, odk_credentials):
# def generate_appuser_files():
# def create_qrcode():
# def insert_background_task_into_database():
# def update_background_task_status_in_database():
# def get_background_task_status(task_id: uuid.UUID, db: Session):
# def convert_geojson_to_osm(geojson_file: str):
# def split_into_tasks():
# def split_polygon_into_tasks():
# def update_project_with_zip():
# def generate_task_files():

# def convert_to_app_project(db_project: db_models.DbProject):
# def convert_to_app_project_info(db_project_info: db_models.DbProjectInfo):
# def convert_to_app_projects(db_projects: List[db_models.DbProject]):
# def convert_to_project_summary(db_project: db_models.DbProject):
# def convert_to_project_summaries(db_projects: List[db_models.DbProject]):
# def convert_to_project_feature(db_project_feature: db_models.DbFeatures):
# def convert_to_project_features(db_project_features: List[db_models.DbFeatures]):

async def main():
    """This is just a hook so this file can be run standalone during development."""
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

    # tasks = TasksDB(args.uri)
    # users = UsersDB(args.uri)
    # projects = ProjectsDB(args.uri)
    # await users.connect(args.uri)
    # await users.getTypes("users")
    # await tasks.connectDBs(args.uri)
    # await tasks.getTypes("tasks")
    # teams = tm_admin.teams.api.TeamsAPI()

    await projects.initialize(args.uri)
    await users.initialize(args.uri)
    await tasks.initialize(args.uri)
    # await teams.initialize(args.uri, projects)

    # The API for this class also requires access to other tables
    await create_projects(projects)
    await test_users.create_users(users)
    await test_tasks.create_tasks(tasks)
    # await create_teams(teams)

    await get_team_role()

    # These endpoint tests come from the TM backend
    await get_project_by_id()
    await exists()
    await get_project_by_name()
    await auto_unlock_tasks()
    await delete_tasks()
    await get_contribs_by_day()
    await get_project_tasks()
    await get_project_aoi()
    await get_project_priority_areas()
    await get_task_for_logged_in_user()
    await get_task_details_for_logged_in_user()
    # FIXME: this needs team_members, which isn't implemented yet.
    # await evaluate_mapping_permission()
    await is_user_permitted_to_map()
    #_is_user_intermediate_or_advanced()
    await evaluate_validation_permission()
    await is_user_permitted_to_validate()
    await get_cached_project_summary()
    await get_project_summary()
    await set_project_as_featured()
    await unset_project_as_featured()
    await get_featured_projects()
    await is_favorited()
    await favorite()
    await unfavorite()
    await get_project_title()
    await get_project_stats()
    await get_project_user_stats()
    await get_project_teams()
    await get_project_organisation()
    await send_email_on_project_progress()
    # is_user_in_the_allowed_list()
    # get_project_dto_for_mapper()

    # FMTM API tests
    await get_projects()
    await get_project_summaries()
    await get_project_by_id_w_all_tasks()
    await get_project()
    await get_project_by_id()
    await get_project_info_by_id()
    await delete_project_by_id()
    await partial_update_project_info()
    await update_project_info()
    await create_project_with_project_info()
    await upload_xlsform()
    await update_multi_polygon_project_boundary()
    await preview_tasks()
    await update_project_boundary()
    await read_xlsforms()
    await get_odk_id_for_project()
    await upload_custom_data_extracts()
    await get_project_geometry()
    await get_task_geometry()
    await get_project_features_geojson()
    await get_project_features()
    await add_features_into_database()
    await update_project_form()
    await update_odk_credentials()
    await get_extracted_data_from_db()
    await get_project_tiles()
    await get_mbtiles_list()
    await update_project_location_info()

if __name__ == "__main__":
    """This is just a hook so this file can be run standalone during development."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
