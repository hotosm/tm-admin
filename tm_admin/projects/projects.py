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
import concurrent.futures
from cpuinfo import get_cpu_info
from shapely.geometry import shape
from shapely import centroid
from tm_admin.types_tm import Mappingtypes, Projectstatus, Taskcreationmode, Editors, Permissions, Projectpriority, Projectdifficulty
from tm_admin.projects.projects_class import ProjectsTable
from shapely import wkb, get_coordinates
from tm_admin.dbsupport import DBSupport
from tm_admin.generator import Generator
from osm_rawdata.postgres import uriParser, PostgresClient
import re
# from progress import Bar, PixelBar
from tqdm import tqdm

# The number of threads is based on the CPU cores
info = get_cpu_info()
cores = info["count"]

# Instantiate logger
log = logging.getLogger(__name__)

def updateThread(
    data: list,
    db: PostgresClient,
):
    """Thread to handle importing

    Args:
        data (list): The list of records to import
        db (PostgresClient): A database connection
    """
    for record in data:
        sql = f" UPDATE projects SET licenses = ARRAY[{record[0]['license']}] WHERE id={record[0]['user']}"
        # print(sql)
        # try:
        #     result = db.dbcursor.execute(f"{sql};")
        # except:
        #     return False

    return True

class ProjectsDB(DBSupport):
    def __init__(self,
                 dburi: str = "localhost/tm_admin",
                ):
        """
        A class to access the projects table.

        Args:
            dburi (str): The URI string for the database connection

        Returns:
            (ProjectsDB): An instance of this class
        """
        self.pg = None
        self.profile = ProjectsTable()
        self.types = dir(tm_admin.types_tm)
        super().__init__('projects', dburi)

    def mergeProjectInfo(self,
                         inuri: str,
                         ):
        table = 'project_info'
        pg = PostgresClient(inuri)
        sql = f"SELECT row_to_json({table}) as row FROM {table}"
        # print(sql)
        try:
            result = pg.dbcursor.execute(sql)
        except:
            log.error(f"Couldn't execute query! {sql}")
            return False

        ignore = ['project_id', 'project_id_str', 'text_searchable', 'per_task_instructions']
        result = pg.dbcursor.fetchall()
        index = 0
        pbar = tqdm(result)
        for record in pbar:
            index += 1
            settings = ""
            column = list()
            for key, val in record[0].items():
                if key in ignore:
                    continue
                if key == "project_id":
                    key = "id"
                elif key == "locale":
                    key = "default_locale"
                else:
                    if val is None:
                        continue
                    key = f"{key}"
                if type(val) == int:
                    entry = f"{key}={val}"
                else:
                    val = val.replace("'", "")
                    entry = f"{key}='{val}'"
                settings += f"{entry}, "

            sql = f"UPDATE projects SET {settings[:-2]} WHERE id={record[0]['project_id']};"
            # print(sql)
            self.pg.dbcursor.execute(sql[:-2])

def main():
    """This main function lets this class be run standalone by a bash script."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", nargs="?", const="0", help="verbose output")
    parser.add_argument("-i", "--inuri", default='localhost/tm4',
                            help="Database URI")
    parser.add_argument("-o", "--outuri", default='localhost/tm_admin',
                            help="Database URI")
    parser.add_argument("-b", "--boundary", help="The project AOI")

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

    proj = ProjectsDB(args.outuri)
    # user.resetSequence()
    #all = proj.getAll()

    proj.mergeProjectInfo(args.inuri)

    # file = open(args.boundary, 'r')
    # boundary = geojson.load(file)
    # geom = shape(boundary[0]['geometry'])
    # center = centroid(geom)

    # Don't pass id, let postgres auto increment
    # ut = ProjectsTable(author_id=1, outline=geom, centroid=center,
    #                    created='2021-12-15 09:58:02.672236',
    #                    task_creation_mode='GRID', status='DRAFT',
    #                    mapping_level='BEGINNER')
    # proj.createTable(ut)
    # print(all)

    #all = proj.getByID(1)
    #print(all)
            
    # all = proj.getByName('fixme')
    # print(all)
            

if __name__ == "__main__":
    """This is just a hook so this file can be run standalone during development."""
    main()
