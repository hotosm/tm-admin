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
from tm_admin.projects.projects_teams_class import Projects_teamsTable
# from tm_admin.teams.teams_members_class import Teams_membersTable

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
            self.yaml = YamlFile(f"{rootdir}/{table}/{table}.yaml")
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

    async def getTypes(self,
#                      uri: str,
                      table: str = None,
                      ):
        """
        Get all the columns and datatypes from the config file.

        Args:
            uri (str): The URI for the TM Admin database
            table (str): The table this class is supporting
        """
        # await self.connect(uri)
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

    async def deleteRecords(self,
                           record_ids: list,
                           ):
        """
        Delete a record from a database table.

        Args:
            record_id (list): The record IDs to delete

        Returns:
            (bool): Whether the record got deleted from the database
        """
        # log.warning(f"--- deleteRecord(): ---")
        if not self.table:
            log.error(f"Not connected to the database!")
            return False

        for id in record_ids:
            sql = f"DELETE FROM {self.table} WHERE id={id}"

        result = await self.execute(sql)

        return True

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
        # log.warning(f"--- insertRecords(): ---")
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
        sql = f"INSERT INTO {self.table}({keys}) VALUES({values}) RETURNING id"
        # print(sql)
        result = await self.execute(sql)

        if len(result) > 0:
            return result[0]['id']
        else:
            return list()

    async def updateColumns(self,
                           columns: dict,
                           where: dict = None,
                           ):
        """
        Update a column in a database table.

        Args:
            columns (dict): The column and it's new value
            where (str): The condition to limit the records

        Returns:
            (bool): Whether the column got updated.
        """
        # log.warning(f"updateColumn(): unimplemented!")
        if not self.table:
            log.error(f"Not connected to the database!")
            return False

        check = str()
        if where:
            check = " WHERE "
            for k, v in where.items():
                # if k in self.types:
                #     if self.types[k] == 'jsonb':
                #         breakpoint()
                if v == 'null':
                    check += f"{k} IS NOT NULL OR "
                else:
                    check += f"{k}={v} OR "

        sql = f"UPDATE {self.table} SET "
        for key, value in columns.items():
            val = self.types[key]
            if val[:7] == "public.":
                # It's an enum
                tmtype = val[7:].capitalize()
                obj = eval(f"tm_admin.types_tm.{tmtype}({value})")
                sql += f" {key} = '{obj.name}', "
            elif val[-2:] == "[]" or val == "jsonb":
                sql += f" {key} = {key}||{value}, "
            else:
                sql += f" {key} = {value}, "
        query = sql[:-2] + f" {check[:-3]} RETURNING id"
        # print(query)
        result = await self.execute(query)
        if len(result) > 0:
            return result[0]['id']
        else:
            return 0

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
                         where: dict = None,
                         ):
        """
        Get columns from a database table.

        Args:
            column (list): The column names to include in the output
            where (list): The conditions to limit the records, might return
                         more than one
            jsonb (bool): Whether to loop through and convert the jsonb to a dict

        Returns:
            (list): The data for this column
        """
        get = str(columns)[1:-1].replace("'", "")

        check = str()
        for k, v in where.items():
            if type(v) == dict:
                # It's a query including a jsonb column
                for k1, v1 in v.items():
                    # teams->'teams' @? '$[*] ? (@.role == 1)
                    # FIXME: is it an internal Enum ?
                    check = f"{k}->'{k}' @? '$[*] ? (@.{k1} == {v1})'"
                    continue
                # if k in self.types:
                #     if self.types[k] == 'jsonb':
                #         breakpoint()
            elif v == 'null':
                check = f"{k} IS NOT NULL"
            elif len(check) == 0:
                check = f"{k}={v}"

        if where:
            sql = f"SELECT {get} FROM {self.table} WHERE {check}"
        else:
            sql = f"SELECT {get} FROM {self.table}"
        # print(sql)
        results = await self.execute(sql)

        data = list()
        for record in results:
            # print(record)
            entry = dict()
            for key, value in record.items():
                if type(value) == str and value[0] == "{":
                    entry[key] = eval(value)
                else:
                    entry[key] = value
            data.append(entry)

        return data

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
    await pgs.connect(args.uri)
    await pgs.getTypes(args.table)

    geom = Polygon()
    center = Point()
    # results = await pgs.getColumns(["id", "name"])
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
    id = await pgs.insertRecords([pt2])
    # print(f"ID: {id}")
    # await pgs.updateProject(pt2)

    # await pgs.deleteRecord([id])
    # log.info(f"Deleted {id} from the database")

    data = await pgs.getColumns(['id', 'teams'])
    print(f"{len(data)} records returned from simple")

    foo = {'id': 12315}
    data = await pgs.getColumns(['id', 'teams'], [foo])
    print(f"{len(data)} records returned from foo")

    foo = {'teams': {"role": tm_admin.types_tm.Teamroles.TEAM_READ_ONLY, "team_id": 144}}
    data = await pgs.getColumns(['id', 'teams'], [foo])
    print(f"{len(data)} records returned from getColumns()")
    # print(data)

    foo = {"featured": "true"}
    data = await pgs.updateColumns([foo])
    print(f"Updated {foo} for all records")

    foo = {"featured": "true", "difficulty": tm_admin.types_tm.Projectdifficulty.CHALLENGING}
    data = await pgs.updateColumns([foo])
    # print(f"{len(data)} records returned from updateColumns()")
    # print(data)

    
    # user = UsersTable(username='foobar', name='barfoo', picture_url='URI', email_address="bar@foo.com", mapping_level='INTERMEDIATE', role='VALIDATOR')
    # await pgs.insertRecords([user])

    #results = await pgs.updateColumns(["id", "username"], )
    #print(results)
    
if __name__ == "__main__":
    """This is just a hook so this file can be run standalone during development."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
