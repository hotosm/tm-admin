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
from pathlib import Path
from sys import argv
from osm_rawdata.postgres import uriParser, PostgresClient
from tm_admin.proto import ProtoBuf


# Instantiate logger
log = logging.getLogger("tm-admin")

import tm_admin as tma
rootdir = tma.__path__[0]

class TmAdminManage(object):
    def __init__(self,
                 dburi: str = "localhost/tm_admin"
                 ):
        # this is for processing an SQL diff
        self.columns = {'drop': list(), 'add': list()}
        self.dburi = dict()
        self.pg = None
        if dburi:
            self.dburi = uriParser(dburi)
            self.pg = PostgresClient(dburi)
            # self.pg.createDB(self.dburi)

    def applyDiff(self,
                  difffile: str,
                  table: str,
                ):
        """
        Modify a postgres database table schema

        Args:
            difffile (str): The filespec of the SQL diff

        Returns:
            (bool): The status on applying the SQL diff
        """
        self.readDiff(difffile)
        if len(self.columns['drop']) > 0 or len(self.columns['add']) > 0:
            return True

        drop = f"ALTER TABLE {table} DROP COLUMN"
        add = f"ALTER TABLE {table} ADD COLUMN"
        return False

    def dump(self):
        """Dump the internal data structures, for debugging only"""
        if len(self.columns['drop']) > 0 or len(self.columns['add']) > 0:
            print("Changes to the table schema")
            for column in self.columns['drop']:
                print(f"\tDropping column {column}")
            for column in self.columns['add']:
                for k, v in column.items():
                    print(f"\tAdding column {k} as {v}")
        print("Database parameters")
        for k, v in self.dburi.items():
            if v is not None:
                print(f"\t{k} = {v}")

    def createDB(self,
                dburi: str = None,
                ):
        """
        Create a postgres database.

        Args:

        Returns:

        """
        # sql = "CREATE EXTENSION IF NOT EXISTS postgis; CREATE EXTENSION IF NOT EXISTS hstore"
        if dburi:
            self.dburi = uriParser(dburi)
        self.pg(createDB(self.uri))

    def createTable(self,
                    sqlfile: str,
                    ):
        """
        Create a table in the database

        Args:
            sqlfile (str):
            dburi (str): The URI string for the database connection

        Returns:
            (bool): The table creation status
        """
        with open(sqlfile, 'r') as file:
            sql = file.read()
            return self.pg.createTable(sql)
        return sql

    def readDiff(self,
                 diff: str,
                 ):
        """
        Read in a diff produced by git diff into a data structure
        that can be used to updgrade a table's schema.

        Args:
            diff (str): the name of the SQL diff file

        Returns:
            (dict): The columns to drop or add from a table
        """
        with open(diff, 'r') as file:
            for line in file.readlines():
                # it's the header
                if line[:3] == '---' or line[:3] == '+++' or  line[:2] == '@@':
                    continue
                # Ignore code block
                if line[0] == ' ':
                    continue
                tmp = ' '.join(line.split()).split()
                if tmp[0] == '-':
                    self.columns['drop'].append(tmp[1])
                if tmp[0] == '+':
                    if tmp[1] in self.columns['drop']:
                        self.columns['drop'].remove(tmp[1])
                        continue
                    if len(tmp) == 3:
                        self.columns['add'].append({tmp[1]: tmp[2][:-1]})
                    elif len(tmp) == 4:
                        self.columns['add'].append({tmp[1]: f"{tmp[2]} {tmp[3][:-1]}"})
        return self.columns

def main():
    """This main function lets this class be run standalone by a bash script."""
    parser = argparse.ArgumentParser(
        prog="config",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Manage the postgres database for the tm-admin project",
        epilog="""
        This should only be run standalone for debugging purposes.
        """,
    )
    choices = ['create', 'migrate']
    parser.add_argument("-v", "--verbose", nargs="?", const="0", help="verbose output")
    parser.add_argument("-d", "--diff", help="SQL file diff for migrations")
    parser.add_argument("-p", "--proto", help="Generate the .proto file from the SQL file")
    parser.add_argument("-u", "--uri", default='localhost/tm_admin',
                            help="Database URI")
    parser.add_argument("-c", "--cmd", choices=choices, default='create',
                            help="Command")
    args, sqlfiles = parser.parse_known_args()

    if len(argv) <= 1:
        parser.print_help()
        quit()

    # if verbose, dump to the terminal.
    if args.verbose is not None:
        log.setLevel(logging.DEBUG)
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(threadName)10s - %(name)s - %(levelname)s - %(message)s")
        ch.setFormatter(formatter)
        log.addHandler(ch)

    # The base class that does all the work
    tm = TmAdminManage(args.uri)

    # modules to generatihng proto files
    pb = ProtoBuf()

    # The default is the current directory in the source tree, so find all
    # the SQL files.
    result = tm.createTable("schemas.sql")
    # This defines all the enums needed to compile the proto files
    types = pb.createProto("types.sql")
    with open('types.proto', 'w') as file:
        file.writelines(str(i)+'\n' for i in types[0])
        file.close()

    for sqlfile in sqlfiles:
        sql = tm.createTable(sqlfile)
        out1, out2 = pb.createProto(sqlfile)
        name = sqlfile.replace('.sql', '.proto')
        if len(out1) > 0:
            with open(name, 'w') as file:
                file.writelines([str(i)+'\n' for i in out1])
                file.close()
        if len(out2) > 0:
            with open(name, 'w') as file:
                file.writelines([str(i)+'\n' for i in out2])
                file.close()
        log.info(f"Wrote {name} to disk")
    tm.dump()

if __name__ == "__main__":
    """This is just a hook so this file can be run standalone during development."""
    main()
