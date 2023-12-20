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
from tm_admin.types_tm import Userrole, Mappinglevel, Organizationtype, Taskcreationmode, Projectstatus, Permissions, Projectpriority, Projectdifficulty, Mappingtypes, Editors
from tm_admin.yamlfile import YamlFile
# from tm_admin.users.users import createSQLValues
# from tm_admin.organizations.organizations import createSQLValues

# Instantiate logger
log = logging.getLogger(__name__)

import tm_admin as tma
rootdir = tma.__path__[0]


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

        yaml = YamlFile(f"{rootdir}/{table}/{table}.yaml")
        # yaml.dump()
        self.config = yaml.getEntries()

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
        log.info(f"There are {len(results)} columns in the TM '{table}' table")
        table = dict()
        for column in results:
            # print(f"FIXME: {column}")
            # if column[2] and column[2][:7] == 'nextval':
            # log.debug(f"Dropping SEQUENCE variable '{column[2]}'")
            #  continue
            if column[1][:9] == 'timestamp':
                table[column[0]] = None
            elif column[1][:5] == 'ARRAY':
                table[column[0]] = None
            elif column[1] == 'boolean':
                table[column[0]] = False
            elif column[1] == 'bigint' or column[1] == 'integer':
                table[column[0]] = 0
            else:
                # it's character varying
                table[column[0]] = ''

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
        results = self.tmdb.queryLocal(sql)
        log.info(f"There are {len(results)} records in the TM '{table}' table")
        data = list()
        for record in results:
            table = dict(zip(keys, record))
            data.append(table)
        return data

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
        builtins = ['int32', 'int64', 'string', 'timestamp', 'bool']
        #bar = Bar('Importing into TMAdmin', max=len(data))
        for record in data:
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
                        geom = get_coordinates(wkb.loads(val))
                        values += f"point({geom[0][0]}, {geom[0][1]}), "
                        continue
                    elif self.config[key]['datatype'] == 'polygon':
                        geom = get_coordinates(wkb.loads(val))
                        poly = ''
                        for x, y in geom:
                            poly += f"({x},{y}), "
                        values += f"polygon('({poly[:-2]})'), "
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
                        if len(val) == 0:
                            values = values[:-2] + "'{}', "
                        else:
                            values = values[:-2]
                            values += f"}}'::{self.config[key]['datatype'].lower()}[], "
                        continue
                    else:
                        # The TM database has a bug, a 0 usually means there is no value,
                        # so we bump it up to pick the first entry in the enum.
                        if val is None:
                            values += f"'{{}}', "
                            continue
                        elif val == 0:
                            val += 1
                            #values += f"'{{}}', "
                        exec = f"{self.config[key]['datatype']}({val})"
                        enumval = eval(exec)
                        values += f"'{enumval.name}', "
                        continue
                else:
                    if self.config[key]['array']:
                        if val is not None:
                            if len(val) == 0:
                                values += "NULL, "
                                continue
                            values += "ARRAY["
                            for item in val:
                                esc = item.replace("'", "")
                                values += f"'{esc}', "
                            values = values[:-2]
                            values += "], "
                            continue
                        else:
                            values += f"NULL, "
                    elif self.config[key]['datatype'][:3] == 'int':
                        if val is None:
                            values += f"NULL, "
                        else:
                            values += f"{val}, "
                    else:
                        if val is None:
                            values += f"NULL, "
                        else:
                            esc = val.replace("'", "")
                            values += f"'{esc}', "
                continue

                # In TM, role is an integer, but it's also an enum, so use the
                # correct enum instead of the integer. Python Enums start with
                # a 1 instead of 0, but in the TM database it starts at 0, so
                # we have to adjust it.
                if table == 'users':
                    if key == 'role':
                        try:
                            # The role column occasionally has a bad value that
                            # doesn't map to the enum
                            if val < 0:
                                val = 0
                            role = Userrole(val + 1)
                            values += f"'{role.name}', "
                            continue
                        except Exception as e:
                            log.error(f"{val} {e}")
                            values += f"'USER_READ_ONLY', "
                            continue
                    # Mapping level is another column that's an int in TM, but also is
                    # an enum in TM, so use the correct enum instead of the integer.
                    # Unlike role, this starts with 1.
                    if key == 'mapping_level':
                        level = Mappinglevel(val)
                        values += f"'{level.name}', "
                        continue
                elif table == 'organizations':
                    if key == 'type':
                        org = Organizationtype(val)
                        values += f"'{org.name}', "
                        continue
                    if key == 'subscription_tier':
                        if val is None:
                            values += f"0, "
                        else:
                            values += f"{val}, "                            
                        continue
                elif table == 'projects':
                    if key == 'id' and val == 409 and key == 'created':
                        pass
                    # continue
                    # # Sometimes there is no value for these booleans
                    # if key == 'progress_email_sent' or key == 'enforce_random_task_selection' or key == 'rapid_power_user' or key == 'private' or key == 'featured':
                    #     if val is None:
                    #         values += f"'f', "
                    #     elif val:
                    #         values += f"'t', "
                    #     else:
                    #         values += f"'f', "
                    #     continue
                    # #
                    # if key == 'created':
                    #     pass
                    # if key == 'task_creation_mode':
                    #     task = Taskcreationmode(val + 1)
                    #     values += f"'{task.name}', "
                    #     continue
                    # elif key == 'status':
                    #     proj = Projectstatus(val + 1)
                    #     values += f"'{proj.name}', "
                    #     continue
                    # elif key == 'mapping_permission':
                    #     perm = Permissions(val + 1)
                    #     values += f"'{perm.name}', "
                    #     continue
                    # elif key == 'validation_permission':
                    #     perm = Permissions(val + 1)
                    #     values += f"'{perm.name}', "
                    #     continue
                    # elif key == 'id_presets':
                    #     if val is not None:
                    #         values += "ARRAY["
                    #         for entry in val:                            
                    #             values += f"'{entry}', "
                    #         values = values[:-2]
                    #         values += "], "
                    #         continue
                    # elif key == 'country':
                    #     values += "ARRAY["
                    #     for entry in val:                            
                    #         values += f"'{entry}', "
                    #     values = values[:-2]
                    #     values += "], "
                    #     continue
                    # elif key == 'mapping_types':
                    #     if val is not None:
                    #         values += "'{"
                    #         for entry in val:
                    #             perm = Mappingtypes(entry)
                    #             values += f"{perm.name}, "
                    #         values = values[:-2]
                    #         values += "}'::mappingtypes[], "
                    #         continue
                    # elif key == 'mapper_level':
                    #     level = Mappinglevel(val)
                    #     values += f"'{level.name}', "
                    #     continue
                    # elif key == 'priority':
                    #     priority = Projectpriority(val)
                    #     values += f"'{priority.name}', "
                    #     continue
                    # elif key == 'mapping_permissions':
                    #     perm = Permissions(perm + 1)
                    #     values += f"'{org.name}', "
                    #     continue
                    # elif key == 'difficulty':
                    #     diff = Projectdifficulty(val)
                    #     values += f"'{diff.name}', "
                    #     continue
                    # elif key == 'mapping_editors':
                    #     values += "'{"
                    #     for ed in val:
                    #         med = Editors(ed + 1)
                    #         values += f"{med.name}, "
                    #     values = values[:-2]
                    #     values += "}'::editors[], "
                    #     continue
                    # elif key == 'validation_editors':
                    #     values += "'{"
                    #     for ed in val:
                    #         ved = Editors(ed + 1)
                    #         values += f"{ved.name}, "
                    #     values = values[:-2]
                    #     values += "}'::editors[], "
                    #     continue
                    # elif key == 'geometry':
                    #     geom = get_coordinates(wkb.loads(val))
                    #     poly = ''
                    #     for x, y in geom:
                    #         poly += f"({x},{y}), "
                    #     values += f"polygon('({poly[:-2]})'), "
                    #     # values += f"ST_MakePolygon(ST_GeomFromText('{wkb.loads(val)}')), "
                    #     continue
                    # elif key == key == 'centroid':
                    #     geom = get_coordinates(wkb.loads(val))
                    #     values += f"point({geom[0][0]}, {geom[0][1]}), "
                    #     continue

                # # All tables
                # if type(val) == str:
                #     tmp = val.replace("'", "&apos;")
                #     values += f"'{tmp}', "
                #     continue
                # elif type(val) == datetime:
                #     values += f"'{val}', "
                #     continue
                # elif type(val) == int:
                #     values += f"{val}, "
                #     continue
                # elif type(val) == bool:
                #     if val:
                #         values += f"'t', "
                #     else:
                #         values += f"'f', "
                #     continue
                # elif type(val) == list:
                #     tmp = str(val)[1:-1]
                #     values += f"'{{{tmp}}}', "
                #     continue
                # elif val is None:
                #     if key == 'projects_mapped':
                #         values += f"'{{}}', "
                #     elif key == 'name':
                #         values += f"'{{}}', "
                #     else:
                #         values += f"NULL, "
                # else:
                #     values += f"'{val}', "

            sql = f"INSERT INTO {table}({str(columns)[1:-1].replace("'", "")}) VALUES({values[:-2]})"
            # sql = f"INSERT INTO organizations VALUES({values[:-2]})"
            print(sql)
            results = self.admindb.queryLocal(sql)

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
    
    table = args.table
    # You have to love subtle culture spelling differences.
    if table == 'organizations':
        data = doit.getAllData('organisations')
    else:
        data = doit.getAllData(table)
    doit.writeAllData(data, table)

if __name__ == "__main__":
    """This is just a hook so this file can be run standalone during development."""
    main()
