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
from tm_admin.users.users import UsersDB
from tm_admin.tasks.tasks import TasksDB
from tm_admin.teams.teams import TeamsDB
from tm_admin.projects.projects import ProjectsDB
from tm_admin.types_tm import Userrole, Mappinglevel, Teamroles, Permissions, Teamroles
from datetime import datetime
from tm_admin.users.users_class import UsersTable
from tm_admin.projects.projects_class import ProjectsTable
import asyncio
from codetiming import Timer
from tm_admin.teams.api import TeamsAPI
from tm_admin.tasks.api import TasksAPI
from tm_admin.users.api import UsersAPI
from tm_admin.projects.api import ProjectsAPI
# from tm_admin.users.api import UsersAPI
from shapely.geometry import Polygon, Point, shape

# Instantiate logger
log = logging.getLogger(__name__)

import tm_admin as tma
rootdir = tma.__path__[0]

# FIXME: For now these tests assume you have a local postgres installed.

users = UsersAPI()
#users.connect("localhost/tm_admin")
# projects = ProjectsAPI()
tasks = TasksAPI()
teams = TeamsAPI()

# These tests are for the API endpoints
async def create_projects(api):
    """
    Create a project. We don't need any valid geometries for this test.

    The id column defaults to auto-increment. TM doesn't have any ids below
    100, so we can use the 0-100 range for testing on a live database.
    """
    coords = ((0., 0.), (0., 1.), (1., 1.), (1., 0.), (0., 0.))
    geom = Polygon(coords)
    center = Point(1.0, -1.0)
    pt = ProjectsTable(id = 1, name = "Hello", author_id = 1, geometry = geom, centroid = center,
                        created = '2021-12-15 09:58:02.672236', organisation_id = 1,
                        task_creation_mode = 'GRID', status = 'DRAFT', featured = "false",
                        mapping_level = 'BEGINNER', priority_areas = [1, 2, 3])
    # returns True or False
    result = await api.create(pt)

    pt = ProjectsTable(id=2, name="World!", author_id = 1, geometry = geom, centroid = center,
                        created = '2022-12-15 09:58:02.672236', featured = "true",
                        task_creation_mode = 'CREATE_ROADS', status = 'PUBLISHED',
                        mapping_level = 'ADVANCED', priority_areas = [1],
                       organisation_id = 1)
    # returns True or False
    result = await api.create(pt)

    role =  Teamroles(Teamroles.TEAM_MAPPER)
    teams = {"team_id": 1, "role": role}
    project_id = 1
    result = await api.updateColumns({"teams": teams}, {"id": project_id})
