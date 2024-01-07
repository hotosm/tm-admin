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
from shapely import wkb, get_coordinates
from shapely.geometry import Polygon, Point, shape
from datetime import datetime
from osm_rawdata.postgres import uriParser, PostgresClient
from progress.bar import Bar, PixelBar
from tm_admin.types_tm import Userrole, Mappinglevel, Organizationtype, Taskcreationmode, Projectstatus, Permissions, Projectpriority, Projectdifficulty, Mappingtypes, Editors, Teamvisibility, Taskstatus
from tm_admin.yamlfile import YamlFile
import concurrent.futures
from cpuinfo import get_cpu_info
# from tm_admin.users.users import createSQLValues
# from tm_admin.organizations.organizations import createSQLValues
from tqdm import tqdm

# Instantiate logger
log = logging.getLogger(__name__)

import tm_admin as tma
rootdir = tma.__path__[0]

# The number of threads is based on the CPU cores
info = get_cpu_info()
# More threads. Shorter import time, higher CPU load. But this is a
# pretty low CPU load proces anyway, so more is good.
cores = info["count"]

def importThread(
    data: list,
    db: PostgresClient,
    tm,
):
    """Thread to handle importing

    Args:
        data (list): The list of records to import
        db (PostgresClient): A database connection
        tm (TMImport): the input handle
    """
    # log.debug(f"There are {len(data)} data entries")
    tm.writeAllData(data, tm.table)

    return True

class TMImport(object):
    def __init__(self,
                inuri: str,
                outuri: str,
                table: str,
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
            table (str): The table in the TM Admin database

        Returns:
            (TMImport): An instance of this class
        """
        # The Tasking Manager database
        self.tmdb = PostgresClient(inuri)
        # The TMAdmin database
        self.admindb = PostgresClient(outuri)
        self.columns = list()
        self.data = list()
        self.table = table

        yaml = YamlFile(f"{rootdir}/{table}/{table}.yaml")
        # yaml.dump()
        self.config = yaml.getEntries()

    def getPage(self,
                offset: int,
                count: int,
                ):
        """
        Return all the data in the table.

        Returns:
            (list): The results of the query
        """
        columns = self.getColumns(self.table)
        keys = self.columns

        columns = str(keys)[1:-1].replace("'", "")
        # sql = f"SELECT row_to_json({self.table}) as row FROM {self.table} ORDER BY id LIMIT {count} OFFSET {offset}"
        sql = f"SELECT {columns} FROM {self.table} ORDER BY id LIMIT {count} OFFSET {offset}"
        # print(sql)
        self.tmdb.dbcursor.execute(sql)
        result = self.tmdb.dbcursor.fetchall()
        data = list()
        for record in result:
            table = dict(zip(keys, record))
            data.append(table)

        return data

    def getColumns(self,
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
        results = self.tmdb.queryLocal(sql)
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
        
    def getAllData(self,
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
        columns = self.getColumns(table)
        keys = self.columns

        columns = str(keys)[1:-1].replace("'", "")
        sql = f"SELECT {columns} FROM {table}"
        # sql = f"SELECT row_to_json({table}) as row FROM {table}"
        results = self.tmdb.queryLocal(sql)
        log.info(f"There are {len(results)} records in the TM '{table}' table")
        data = list()
        # this is actually faster than using row_to_json(), and the
        # data is a little easier to navigate.
        for record in results:
            table = dict(zip(keys, record))
            data.append(table)
        return data

    def getRecordCount(self):
        sql = f"SELECT COUNT(id) FROM {self.table}"
        # print(sql)
        try:
            result = self.tmdb.dbcursor.execute(sql)
        except:
            log.error(f"Couldn't execute query! {sql}")
            return False
        result = self.tmdb.dbcursor.fetchone()[0]
        log.debug(f"There are {result} records in {self.table}")

        return result

    def writeAllData(self,
                    data: list,
                    table: str,
                    ):
        """
        Write the data into table in TM Admin.

        Args:
            data (list): The table data from TM
            table str(): The table to get the columns for.
        """
        # log.debug(f"Writing block {len(data)} to the database")
        if len(data) == 0:
            return True

        builtins = ['int32', 'int64', 'string', 'timestamp', 'bool']
        pbar = tqdm(data)
        for record in pbar:
        # for record in data:
            # columns = str(list(record.keys()))[1:-1].replace("'", "")
            columns = list()
            values = ""
            # values += createSQLValues(record, self.config)
            # print(values)
            # bar.next()
            for key, val in record.items():
                columns.append(key)
                # print(f"FIXME: {key} = {self.config[key]}")
                # Booleans need to set 't' or 'f' for postgres.
                if self.config[key]['datatype'] == 'bool':
                    if val:
                        values += f"'t', "
                    else:
                        values += f"'f', "
                    continue
                if self.config[key]['datatype'] == 'timestamp':
                    if val is None:
                        values += f"NULL, "
                    else:
                        values += f"'{val}', "
                    continue
                    
                # If it's not a standard datatype, it's an enum in types_tm.py
                if self.config[key]['datatype'] not in builtins:
                    if self.config[key]['datatype'] == 'point':
                        geom = wkb.loads(val)
                        # values += f"point({geom[0][0]}, {geom[0][1]}), "
                        values += f"'{geom.wkb_hex}', "
                        continue
                    elif self.config[key]['datatype'] == 'polygon':
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
                            exec = f"{self.config[key]['datatype']}({entry})"
                            enumval = eval(exec)
                            values += f"{enumval.name}, "
                        if len(val) == 0: # FIXME: is this still valid ?
                            values = values[:-2] + "'{}', "
                        else:
                            values = values[:-2]
                            values += f"}}'::{self.config[key]['datatype'].lower()}[], "
                        continue
                    elif type(val) == int:
                        if val <= 0:
                            val = 1
                        exec = f"{self.config[key]['datatype']}({val})"
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
                            exec = f"{self.config[key]['datatype']}({val})"
                            enumval = eval(exec)
                            values += f"'{enumval.name}', "
                            continue
                        elif type(str):
                            values += f"'{val}', "
                else:
                    if self.config[key]['array']:
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
                    elif self.config[key]['datatype'][:3] == 'int':
                        if val is None:
                            if self.config[key]['required']:
                                values += f"0, "
                            else:
                                values += f"NULL, "
                        else:
                            values += f"{val}, "
                    else:
                        if val is None:
                            if self.config[key]['required']:
                                values += f"'', "
                            else:
                                values += f"NULL, "
                        else:
                            esc = val.replace("'", "")
                            values += f"'{esc}', "
                continue

            # This covers the columns in the config file that are considered
            # required in the output database, but aren't in the input database.
            for key, val in self.config.items():
                if 'required' in val and key not in columns:
                    # log.debug(f"REQUIRED: {key} = {val['required']}")
                    if val['required']:
                        # g.debug(f"Key '{key}' is required")
                        columns.append(key)
                        # FIXME: don't hardcode
                        if self.config[key]['datatype'] not in builtins:
                            # log.debug(f"Key '{key}' is an Enum")
                            exec = f"{self.config[key]['datatype']}(1)"
                            enumval = eval(exec)
                            values += f"'{enumval.name}', "
                        else:
                            log.warning(f"No support yet for {key}!")
                    

            # foo = f"str(columns)[1:-1].replace("'", "")
            sql = f"""INSERT INTO {table}({str(columns)[1:-1].replace("'", "")}) VALUES({values[:-2]})"""
            # print(sql)
            results = self.admindb.dbcursor.execute(sql)

        #bar.finish()
            
def main():
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

    doit = TMImport(args.inuri, args.outuri, args.table)
    entries = doit.getRecordCount()
    block = 0
    chunk = round(entries / cores)

    # this is the size of the pages in records
    threshold = 10000
    data = list()
    tmpg = list()

    tmpg = list()
    for i in range(0, cores + 1):
        # FIXME: this shouldn't be hardcoded
        tmpg.append(PostgresClient('localhost/tm4'))
    # Some tables in the input database are huge, and can either core
    # dump python, or have performance issues. Past a certain threshold
    # the data needs to be queried in pages instead of the entire table.
    if entries > threshold:
        with concurrent.futures.ThreadPoolExecutor(max_workers=cores) as executor:
            index = 0
            for block in range(0, entries, chunk):
                data = doit.getPage(block, chunk)
                page = round(len(data) / cores)
                # log.debug(f"Dispatching Block {index}")
                # importThread(data, tmpg[0], doit)
                result = executor.submit(importThread, data, tmpg[index], doit)
                index += 1
            executor.shutdown()
    else:
        data = list
        # You have to love subtle cultural spelling differences.
        if args.table == 'organizations':
            data = doit.getAllData('organisations')
        else:
            data = doit.getAllData(args.table)

        # entries = len(data)
        # log.debug(f"There are {entries} entries in {args.table}")
        # chunk = round(entries / cores)

        if entries < threshold:
            importThread(data, tmpg[0], doit)
            quit()

        index = 0
        with concurrent.futures.ThreadPoolExecutor(max_workers=cores) as executor:
            block = 0
            while block <= entries:
                log.debug("Dispatching Block %d:%d" % (block, block + chunk))
                #importThread(data, tmpg[0], doit)
                result = executor.submit(importThread, data[block : block + chunk], tmpg[index], doit)
                block += chunk
                index += 1
            executor.shutdown()

    # cleanup the connections
    for conn in tmpg:
        conn.dbshell.close()

if __name__ == "__main__":
    """This is just a hook so this file can be run standalone during development."""
    main()
