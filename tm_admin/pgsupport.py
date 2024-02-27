#!/usr/bin/python3

# Copyright (c) 2023, 2024 Humanitarian OpenStreetMap Team
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
import os
import sys
import time
from io import BytesIO
from pathlib import Path
from urllib.parse import urlparse
import asyncpg
import asyncio
import geojson
import tm_admin.types_tm
from osm_rawdata.pgasync import PostgresClient
from tm_admin.yamlfile import YamlFile
from tm_admin.projects.projects_class import ProjectsTable
from shapely.geometry import Polygon, Point, shape


# Find the other files for this project
import tm_admin as tma
rootdir = tma.__path__[0]

# Instantiate logger
log = logging.getLogger(__name__)


class PGSupport(PostgresClient):
    def __init__(self,
                 table: str = None,
                 ):
        super().__init__()
        self.table = None
        self.yaml = None
        if table:
            filespec = Path(f"{rootdir}/{table}/{table}.yaml")
            self.yaml = YamlFile(filespec)
            self.table = table
        self.yaml2py = {'int32': 'int',
                    'int64': 'int',
                    'bool': 'bool',
                    'string': 'str',
                    'bytes': 'bytes',
                    'timestamp': 'timestamp without time zone',
                    'polygon': 'Polygon',
                    'point': 'Point',
                    'json': 'dict',
                    }
        self.types = dict()

    async def setup(self,
                      uri: str,
                      table: str = None,
                      ):
        """
        Connect to the TM Admin database.

        Args:
            uri (str): The URI for the TM Admin database
            table (str): The table this class is supporting
        """
        await self.connect(uri)
        if table:
            self.table = table
        filespec = Path(f"{rootdir}/{self.table}/{self.table}.yaml")
        self.yaml = YamlFile(filespec)
        self.types = dict()
        for entry in self.yaml.yaml:
            [[table, settings]] = entry.items()
            for item in settings:
                if type(item) == dict:
                    [[k, v]] = item.items()
                    if v[0] in self.yaml2py:
                        datatype = self.yaml2py[v[0]]
                    else:
                        # it's an SQL Enum from types_tm.py
                        datatype = v[0]
                    if type(v) == list:
                        for element in v:
                            if 'array' in element:
                                if element['array']:
                                    datatype += "[]"
                self.types[k] = datatype 

    async def insertRecords(self,
                           records: list,
                           ):
        """
        Insert a record in a database table. All the primary tables auto-increment
        the id column. If id is set in the record, then it uses that value, otherwise
        it increments.

        Args:
            records (dict): The record data

        Returns:
            (bool): Whether the record got inserted into the database
        """
        # log.warning(f"--- insertRecord(): ---")
        if not self.table:
            log.error(f"Not connected to the database!")
            return False

        data = dict()
        for entry in records:
            for key, value in entry.data.items():
                if not value:
                    continue
                if type(value) == dict:
                    # It's for a jsonb column
                    # a dict uses single quotes, postgres wants double quotes.
                    newval = str(value).replace("'", '"')
                    data[key] = f"{newval}"
                    continue
                val = self.types[key]
                if val[:7] == "public.":
                    # FIXME: unfortunately, the supposed enums are a mix of
                    # the string value or the integer value. Ideally this should
                    # all get cleaned up, but till then handle both.
                    # print(f"FIXME: {key}: {type(value)}")
                    tmtype = val[7:].capitalize()
                    if type(value) == str:
                        data[key] = value
                    elif type(value) == int:
                        # All we have is the value, so instantiate the Enum
                        # to get the name. Also check if it's an array.
                        if tmtype[-2:] == "[]":
                            obj = eval("tm_admin.types_tm.%s(%s)" % (tmtype[:-2], value))
                            data[key] = "{%s}" % obj.name
                        else:
                            obj = eval(f"tm_admin.types_tm.{tmtype}({value})")
                            data[key] = obj.name
                else:
                    data[key] = value

        keys = str(list(data.keys())).replace("'", "")[1:-1]
        values = str(list(data.values()))[1:-1]
        sql = f"INSERT INTO {self.table}({keys}) VALUES({values})"
        print(sql)
        result = await self.execute(sql)

        if len(result) == 0:
            return True

        return False

    async def updateColumns(self,
                           where: str,
                           column: dict,
                           table: str,
                           ):
        """
        Update a column in a database table.

        Args:
            where (str): The condition to limit the records
            column (dict): The column and it's new value
            table (str): The table containing the column

        Returns:
            (bool): Whether the column got updated.
        """
        log.warning(f"updateColumn(): unimplemented!")
        # Get the config file for this table
        if not self.table:
            log.error(f"Not connected to the database!")
            return False

        # FIXME: use the config to 
        
        return False

    async def resetSequence(self):
        """
        Reset the ID column sequence to zero.
        """
        sql = f"ALTER SEQUENCE public.{self.table}_id_seq RESTART;"
        await self.execute(sql)

    async def appendColumns(self,
                           where: str,
                           column: dict,
                           ):
        """
        Append to a jsonb or array column in a database table.

        Args:
            where (str): The condition to limit the records
            column (dict): The column and it's new value

        Returns:
            (bool): Whether the column got updated.
        """
        log.warning(f"updateColumn(): unimplemented!")
        # Get the config file for this table

        # FIXME: use the config to 
        
        return False

    async def getColumns(self,
                         columns: list,
                         where: str = None,
                         ):
        """
        Get columns from a database table.

        Args:
            where (str): The condition to limit the records, might return
                         more than one
            column (str): The column name

        Returns:
            (list): The data of this column
        """
        get = str(columns)[1:-1].replace("'", "")

        if where:
            sql = f"SELECT {get} FROM {self.table} {where}"
        else:
            sql = f"SELECT {get} FROM {self.table}"
        results = await self.execute(sql)

        return results

async def main():
    """This main function lets this class be run standalone by a bash script."""
    parser = argparse.ArgumentParser(
        prog="pgsupport",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Support queries to the TM Admin database",
        epilog="""
        This a utility class, and should never be used standalone!
        """,
    )
    parser.add_argument("-v", "--verbose", nargs="?", const="0", help="verbose output")
    parser.add_argument("-u", "--uri", default="localhost/tm_admin", help="Database URI")
    parser.add_argument("-s", "--sql", help="Custom SQL query to execute against the database")
    parser.add_argument("-t", "--table", default="projects", help="The database table")
    args = parser.parse_args()

    # if len(argv) <= 1 or (args.sql is None and args.config is None):
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

    pgs = PGSupport(args.table)
    await pgs.setup(args.uri)

    geom = Polygon()
    center = Point()
    results = await pgs.getColumns(["id", "name"])
    pt = ProjectsTable(author_id=1, geometry=geom, centroid=center,
                        created='2021-12-15 09:58:02.672236',
                        task_creation_mode='GRID', status='DRAFT',
                        mapping_level='BEGINNER')
    await pgs.insertRecords([pt])

    # insert with a dict into a jsonb column
    teams = {"team_id": 2, "role": "TEAM_MAPPER"}
    pt2 = ProjectsTable(author_id=1, geometry=geom, centroid=center,
                        created='2022-10-15 09:58:02.672236',
                        task_creation_mode='GRID', status='DRAFT',
                        mapping_level='INTERMEDIATE', teams=teams)
    await pgs.insertRecords([pt2])
    # await pgs.updateProject(pt2)

    # user = UsersTable(username='foobar', name='barfoo', picture_url='URI', email_address="bar@foo.com", mapping_level='INTERMEDIATE', role='VALIDATOR')
    # await pgs.insertRecords([user])

    #results = await pgs.updateColumns(["id", "username"], )
    #print(results)
    
if __name__ == "__main__":
    """This is just a hook so this file can be run standalone during development."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())