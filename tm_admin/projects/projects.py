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
from datetime import datetime
from dateutil.parser import parse
import tm_admin.types_tm
import geojson
from shapely.geometry import shape
from shapely import centroid

from tm_admin.dbsupport import DBSupport
from tm_admin.projects.projects_class import ProjectsTable
from osm_rawdata.postgres import uriParser, PostgresClient

# Instantiate logger
log = logging.getLogger(__name__)

class ProjectsDB(DBSupport):
    def __init__(self,
                 dburi: str = "localhost/tm_admin",
                ):
        self.pg = None
        self.profile = ProjectsTable()
        #if dburi:
        #    self.pg = PostgresClient(dburi)
        self.types = dir(tm_admin.types_tm)
        super().__init__('projects', dburi)

def main():
    """This main function lets this class be run standalone by a bash script."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", nargs="?", const="0", help="verbose output")
    parser.add_argument("-u", "--uri", default='localhost/tm_admin',
                            help="Database URI")
    parser.add_argument("-b", "--boundary", required=True,
                        help="The project AOI")

    # parser.add_argument("-r", "--reset", help="Reset Sequences")
    args = parser.parse_args()

    # if len(argv) <= 1:
    #     parser.print_help()
    #     quit()

    # if verbose, dump to the terminal.
    log_level = os.getenv("LOG_LEVEL", default="INFO")
    if args.verbose is not None:
        log_level = logging.DEBUG

    logging.basicConfig(
        level=log_level,
        format=("%(asctime)s.%(msecs)03d [%(levelname)s] " "%(name)s | %(funcName)s:%(lineno)d | %(message)s"),
        datefmt="%y-%m-%d %H:%M:%S",
        stream=sys.stdout,
    )

    proj = ProjectsDB(args.uri)
    # user.resetSequence()
    all = proj.getAll()

    file = open(args.boundary, 'r')
    boundary = geojson.load(file)
    geom = shape(boundary[0]['geometry'])
    center = centroid(geom)
    # Don't pass id, let postgres auto increment
    ut = ProjectsTable(author_id=1, outline=geom, centroid=center,
                       created='2021-12-15 09:58:02.672236',
                       task_creation_mode='GRID', status='DRAFT',
                       mapper_level='BEGINNER')
    proj.createProject(ut)
    # print(all)

    #all = proj.getByID(1)
    #print(all)
            
    # all = proj.getByName('fixme')
    # print(all)
            

if __name__ == "__main__":
    """This is just a hook so this file can be run standalone during development."""
    main()
