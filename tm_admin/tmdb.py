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
from sys import argv
import os
import time
from shapely import wkb, get_coordinates
from shapely.geometry import MultiPolygon, Polygon, Point, shape
from datetime import datetime
from osm_rawdata.pgasync import PostgresClient
from progress.bar import Bar, PixelBar
from tm_admin.types_tm import Mappinglevel, Organizationtype, Taskcreationmode, Projectstatus, Permissions, Projectpriority, Projectdifficulty, Mappingtypes, Editors, Teamvisibility, Taskstatus
from tm_admin.access import Roles
from tm_admin.yamlfile import YamlFile
import concurrent.futures
from cpuinfo import get_cpu_info
import asyncio

# from asyncpg import create_pool
# from tm_admin.users.users import createSQLValues
# from tm_admin.organizations.organizations import createSQLValues
from tqdm import tqdm
import tqdm.asyncio

# Instantiate logger
log = logging.getLogger(__name__)

import tm_admin as tma
rootdir = tma.__path__[0]

# The number of threads is based on the CPU cores
info = get_cpu_info()
# More threads. Shorter import time, higher CPU load. But this is a
# pretty low CPU load anyway, so more is good.
cores = info["count"] * 2

async def importThread(
        data: list,
        pg: PostgresClient,
        table: str,
        config: dict,
        ):
    """
    Thread to handle importing

    Args:
        data (list): The list of records to import
        outuri (str): The output database
    """
        # await tmi.writeAllData(data, pg)
    # log.debug(f"There are {len(data)} data entries")
    if table == 'organisations':
        table = 'organizations'
    if len(data) > 0:
        builtins = ['int32', 'int64', 'string', 'timestamp', 'bool']
        pbar = tqdm.tqdm(data)
        for record in pbar:
        # for record in data:
            # columns = str(list(record.keys()))[1:-1].replace("'", "")
            null = None
            true = True
            false = False
            columns = list()
            values = ""
            # values += createSQLValues(record, self.config)
            # print(values)
            # bar.next()
            if type(record) == str:
                x = eval(record)
            else:
                x = record
            for key, val in x.items():
                columns.append(key)
                # print(f"FIXME: {key} = {self.config[key]}")
                # Booleans need to set 't' or 'f' for postgres.
                if config[key]['datatype'] == 'bool':
                    if val:
                        values += f"'t', "
                    else:
                        values += f"'f', "
                    continue
                if config[key]['datatype'] == 'timestamp':
                    if val is None:
                        values += f"NULL, "
                    else:
                        values += f"'{val}', "
                    continue
                    
                # If it's not a standard datatype, it's an enum in types_tm.py
                if config[key]['datatype'] not in builtins:
                    if config[key]['datatype'] == 'point':
                        if type(val) == dict:
                            geom = shape(val)
                        else:
                            geom = wkb.loads(val)
                        # values += f"point({geom[0][0]}, {geom[0][1]}), "
                        values += f"'{geom.wkb_hex}', "
                        continue
                    elif config[key]['datatype'] == 'polygon':
                        if type(val) == dict:
                            geom = shape(val)
                        else:
                            geom = wkb.loads(val)
                        values += f"'{geom.geoms[0].wkb_hex}', "
                        # values += f"polygon('({poly[:-2]})'), "
                        continue
                    elif type(val) == list:
                        values += "'{"
                        for entry in val:
                            # The TM database has a bug, since it doesn't use enums,
                            # which have to start with a value of 1.
                            if entry == 0:
                                entry += 1
                            exec = f"{config[key]['datatype']}({entry})"
                            enumval = eval(exec)
                            values += f"{enumval.name}, "
                        if len(val) == 0: # FIXME: is this still valid ?
                            values = values[:-2] + "'{}', "
                        else:
                            values = values[:-2]
                            values += f"}}'::{config[key]['datatype'].lower()}[], "
                        continue
                    elif type(val) == int:
                        if val <= 0:
                            val = 1
                        exec = f"{config[key]['datatype']}({val})"
                        enumval = eval(exec)
                        values += f"'{enumval.name}', "
                        continue
                    else:
                        # The TM database has a bug, a 0 usually means there is no value,
                        # so we bump it up to pick the first entry in the enum.
                        if val is None:
                            values += f"'{{}}', "
                            continue
                        elif type(val) == int and val <= 0:
                            val = 1
                            #values += f"'{{}}', "
                            exec = f"{config[key]['datatype']}({val})"
                            enumval = eval(exec)
                            values += f"'{enumval.name}', "
                            continue
                        elif type(str):
                            values += f"'{val}', "
                else:
                    if config[key]['array']:
                        if val is not None:
                            if len(val) == 0:
                                values += "NULL, "
                                continue
                            values += "ARRAY["
                            for item in val:
                                if type(item) == str:
                                    esc = item.replace("'", "")
                                    values += f"'{esc}', "
                                elif type(item) == int:
                                    values += f"{item}, "
                            values = values[:-2]
                            values += "], "
                            continue
                        else:
                            values += f"NULL, "
                    elif config[key]['datatype'][:3] == 'int':
                        if val is None:
                            if config[key]['required']:
                                values += f"0, "
                            else:
                                values += f"NULL, "
                        else:
                            values += f"{val}, "
                    else:
                        if val is None:
                            if config[key]['required']:
                                values += f"'', "
                            else:
                                values += f"NULL, "
                        else:
                            esc = val.replace("'", "")
                            values += f"'{esc}', "
                continue

            # This covers the columns in the config file that are considered
            # required in the output database, but aren't in the input database.
            for key, val in config.items():
                if 'required' in val and key not in columns:
                    # log.debug(f"REQUIRED: {key} = {val['required']}")
                    if val['required']:
                        # g.debug(f"Key '{key}' is required")
                        columns.append(key)
                        # FIXME: don't hardcode
                        if config[key]['datatype'] not in builtins:
                            # log.debug(f"Key '{key}' is an Enum")
                            exec = f"{config[key]['datatype']}(1)"
                            enumval = eval(exec)
                            values += f"'{enumval.name}', "
                        else:
                            log.warning(f"No support yet for {key}!")
                    

            # foo = f"str(columns)[1:-1].replace("'", "")
            sql = f"""INSERT INTO {table}({str(columns)[1:-1].replace("'", "")}) VALUES({values[:-2]})"""
            #print(sql)
            results = await pg.execute(sql)

    return True

class TMImport(object):
    def __init__(self):
        """
        This class contains support to accessing a Tasking Manager database, and
        importing it in the TM Admin database. This works because the TM Admin
        database schema is based on the ones used by FMTM and TM. The schemas
        have been merged into a single one, and all of the column names are
        the same across the two schemas except in a few rare cases.

        The other change is in TM many columns are enums, but the database type
        is in. The integer values from TM are converted to the proper TM Admin enum value.

        Args:
            config (str): The YAML config file for this table
        Returns:
            (TMImport): An instance of this class
        """
        self.tmdb = None
        self.admindb = None
        self.table = None
        self.columns = list()
        self.data = list()
        self.config = dict()

    async def loadConfig(self,
                        config: str,
                        ):
        """
        Load the YAML based config file for this table.

        Args:
            config: the name of the table.
        """
        self.table = config
        if config.find("/") <= 0:
            yaml = YamlFile(f"{rootdir}/{config}/{config}.yaml")
        else:
            yaml = YamlFile(f"{rootdir}/{config}.yaml")
        # yaml.dump()
        self.config = yaml.getEntries()

    async def connect(self,
                inuri: str,
                outuri: str,
                ):
        """
        This class contains support to accessing a Tasking Manager database, and
        importing it in the TM Admin database. This works because the TM Admin
        database schema is based on the ones used by FMTM and TM. The schemas
        have been merged into a single one, and all of the column names are
        the same across the two schemas except in a few rare cases.

        The other change is in TM many columns are enums, but the database type
        is in. The integer values from TM are converted to the proper TM Admin enum value.
        Args:
            inuri (str): The URI for the TM database
            outuri (str): The URI for the TM Admin database
        """
        # The Tasking Manager database
        self.tmdb = PostgresClient()
        await self.tmdb.connect(inuri)

        self.admindb = PostgresClient()
        await self.admindb.connect(outuri)
        self.outuri = outuri

        # The TMAdmin database
        # self.columns = list()
        # self.data = list()

    async def getColumns(self,
                    table: str,
                    ):
        """
        Create the data structure for the database table with default values.

        Args:
            table str(): The table to get the columns for.

        Returns:
            (dict): The table definition.
        """
        sql = f"SELECT column_name, data_type,column_default  FROM information_schema.columns WHERE table_name = '{table}' ORDER BY dtd_identifier;"
        results = await self.tmdb.execute(sql)
        # log.info(f"There are {len(results)} columns in the TM '{table}' table")
        table = dict()
        for column in results:
            # print(f"FIXME: {column}")
            # if column[2] and column[2][:7] == 'nextval':
            # log.debug(f"Dropping SEQUENCE variable '{column[2]}'")
            #  continue
            if column[1][:9] == 'timestamp':
                table[column[0]] = None
                #self.accessor[column[0]] = f" WHERE {column[0]}='{test}'"
            elif column[1][:5] == 'ARRAY':
                table[column[0]] = None
                # self.accessor[column[0]] = f" WHERE {column[0]}={test}"
            elif column[1] == 'boolean':
                table[column[0]] = False
            elif column[1] == 'bigint' or column[1] == 'integer':
                table[column[0]] = 0
                #self.accessor[column[0]] = f" WHERE {column[0]}={test}"
            else:
                # it's character varying or one of the Enums in types_tm.py
                table[column[0]] = ''
                #self.accessor[column[0]] = f" WHERE {column[0]}='XXXX'"

        if len(results) > 0:
            self.columns = list(table.keys())

        return table

    async def getAllData(self,
                   table: str,
                ):
        """
        Read all the data for a table in the Tasking Manager. The TM database is
        relatively small, so load the entire table.

        Args:
            table str(): The table to get the columns for.

        Returns:
            (list): All the data from the table.
        """
        columns = await self.getColumns(table)
        keys = self.columns

        columns = str(keys)[1:-1].replace("'", "")
        sql = f"SELECT {columns} FROM {table}"
        # sql = f"SELECT row_to_json({table}) as row FROM {table}"
        results = await self.tmdb.execute(sql)
        log.info(f"There are {len(results)} records in the TM '{table}' table")
        data = list()
        # this is actually faster than using row_to_json(), and the
        # data is a little easier to navigate.
        for record in results:
            table = dict(zip(keys, record))
            data.append(table)
        return data

    async def importDB(self,
                       table: str,
                       ):

        """
        Import a table from the Tasking Manager into TM Admin

        Args:
            table (str): The table to import
        """
        # Some tables in the input database are huge, and can either core
        # dump python, or have performance issues. Past a certain threshold
        # the data needs to be queried in pages instead of the entire table.
        # There seems to be issues with data corruption
        if table == 'organizations':
            table = 'organisations'

        sql = f"SELECT * FROM {table}"
        # print(sql)
        # print(self.tmdb.dburi)

        log.warning(f"This operation may be slow for large datasets.")
        data = await self.tmdb.execute(sql)

        entries = len(data)
        chunk = round(entries / cores)

        async with asyncio.TaskGroup() as tg:
            # dsn = f"postgres://rob:fu=br@localhost/tm_admin"
            # async with create_pool(min_size=2, max_size=cores, dsn=dsn) as pool:
            #     async with pool.acquire() as con:
            for block in range(0, entries, chunk):
                outpg = PostgresClient()
                await outpg.connect(self.outuri)
                # data = await inpg.getPage(start, chunk, args.table)
                # log.debug(f"Dispatching thread {index} {start}:{start + chunk}")
                log.debug(f"Dispatching thread {block}:{block + chunk - 1}")
                # This changes from multi-threaded to single threaded for debugging
                # await importThread(data[block:block + chunk - 1], outpg, table, self.config)
                task = tg.create_task(importThread(data[block:block + chunk - 1], outpg, table, self.config))

async def main():
    """This main function lets this class be run standalone by a bash script."""
    parser = argparse.ArgumentParser(
        prog="tmclient",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="organizationimport",
        epilog="""
        Program to import from a TM database into the TMAdmin schema..
        """,
    )
    parser.add_argument("-v", "--verbose", nargs="?", const="0", help="verbose output")
    parser.add_argument("-i", "--inuri", default='localhost/tm4', help="The URI string for the TM database")
    parser.add_argument("-o", "--outuri", default='localhost/tm_admin', help="The URI string for the TM Admin database")
    parser.add_argument("-t", "--table", required=True, help="The table to import into")
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

    tmi = TMImport()
    await tmi.loadConfig(args.table)
    await tmi.connect(args.inuri, args.outuri)
    if len(args.table) == 1:
        await tmi.importDB(args.table)
    else:
        await tmi.importDB(args.table)

if __name__ == "__main__":
    """This is just a hook so this file can be run standalone during development."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
