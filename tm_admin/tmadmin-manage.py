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

    def createProto(self,
                    sqlfile: str,
                    ):
        """
        Read an SQL file and produce data to create protobuf .proto files.

        Args:
            sqlfile (str): The SQL file to process.

        Returns:
            (dict): The list of enums and types
            (dict): The list of tables
        """
        tables = dict()
        enums = dict()
        table = dict()
        log.info(f"Processing {sqlfile}...")
        with open(sqlfile, 'r') as file:
            inblock = False
            inenum = True
            nume = list()
            name = None
            for line in file.readlines():
                optional = ""
                repeated = ""
                # We don't care about the NOT NULL parameter
                loc = line.find('NOT')
                tmp = ' '.join(line[:loc].split()).split()
                # optional is for anything that is NOT NULL
                if loc > 0:
                    optional = "optional "
                if line[:2] == ");":
                    if inblock:
                        inblock = False
                        tables[name] = table
                        print(f"Done table {name}...")
                    elif inenum:
                        inenum = False
                        enums[name] = nume
                        print(f"Done enum {name}...")
                    continue
                if line[:12] == 'CREATE TABLE':
                    name = tmp[2].replace("public.", "")
                    inblock = True
                    continue
                if line[:11] == 'CREATE TYPE' and tmp[4] == 'ENUM':
                    name = tmp[2].replace("public.", "")
                    nume = list()
                    inenum = True
                    continue
                if len(tmp) == 2 and inblock:
                    table[tmp[0]] = tmp[1]
                    continue
                if len(tmp) == 3 and inblock:
                    if tmp[2][-1:] == ',':
                        table[tmp[0]] = f"{tmp[1]}_{tmp[2][:-1]}"
                    else:
                        table[tmp[0]] = f"{tmp[1]}_{tmp[2]}"
                    continue
                if len(tmp) == 1 and inenum:
                    if  tmp[0][-1:] == ',':
                        nume.append(f"{tmp[0][1:-2]}")
                    else:
                        nume.append(f"{tmp[0][1:-1]}")
                # Repeated is for arrays
                if line[:2] == "[]":
                    repeated = "repeated"

        out1 = self.createEnumProto(enums)
        out2 = self.createTableProto(tables)

        return out1, out2

    def createEnumProto(self,
                    enums: dict,
                    ):
        """
        Process a list of enums into the protobuf version.

        Args:
            enums (dict): The list of tables to generate a protobuf for.

        Returns:
            (list): The list of enums in protobuf format
        """
        out = list()
        out.append(f"syntax = 'proto3';")
        for name, value in enums.items():
            index = 0
            out.append(f"enum {name.capitalize()} {{")
            for entry in value:
                out.append(f"\t{entry} = {index};")
                index += 1
            out.append('};')

        return out

    def createTableProto(self,
                    tables: dict,
                    ):
        """
        Process a list of tables into the protobuf version.

        Args:
            table (dict): The list of tables to generate a protobuf for.

        Returns:
            (list): The list of tables in protobuf format
        """
        out = list()
        convert = {'integer': 'int32',
                   'bigint': 'int64',
                   'boolean': 'bool',
                   'character_varying': 'string',
                   'bytea': 'bytes',
                   }
        out.append(f"syntax = 'proto3';")
        out.append("import 'types.proto';")

        for name, value in tables.items():
            out.append(f"message {name} {{")
            index = 1
            for table, data in tables.items():
                optional = ""
                repeated = ""
                for k1, v1 in data.items():
                    # Remove any embedded commas
                    v1 = v1.replace(',', '')
                    # print(f"DATA: {k1} = {v1}")
                    if v1[:7] == 'public.':
                        # log.debug(f"Got enum '{k1}' from types.proto")
                        v1 = v1[7:].capitalize()
                        # out.append(f"\t{optional}  {v1} {k1} = {index};")
                    # FIXME: Sometimes this has a number for a fixed length string
                    elif v1[:17] == 'character_varying':
                        v1 = v1[:17]
                    # It's an array, ie.. repeated field
                    elif v1[-2:] == '[]':
                        # log.debug(f"Got an array for {k1}")
                        v1 = v1[:-2]
                        repeated = 'repeated'
                    # it's an enum defined in types.proto
                    if v1 not in convert:
                        if v1[:8] == 'Geometry':
                            # log.debug(f"Got a geometry for {k1}")
                            out.append(f"\t{optional}  bytes {k1} = {index};")
                    else:
                        out.append(f"\t{optional} {repeated} {convert[v1]} {k1} = {index};")
                    index += 1
            out += f"}}";

        return out

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
    parser.add_argument("-i", "--infile", default='.', help="Input SQL file")
    parser.add_argument("-d", "--diff", help="SQL file diff for migrations")
    parser.add_argument("-p", "--proto", help="Generate the .proto file from the SQL file")
    parser.add_argument("-u", "--uri", default='localhost/tm_admin',
                            help="Database URI")
    parser.add_argument("-c", "--cmd", choices=choices, default='create',
                            help="Command")
    args = parser.parse_args()

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

    sqlfiles = list()
    path = Path(args.infile)
    if path.is_dir():
        sqlfiles = path.glob('*/*.sql')
    else:
        sqlfiles = [path]

    tm = TmAdminManage(args.uri)

    # The default is the current directory in the source tree, so find all
    # the SQL files.
    result = tm.createTable("schemas.sql")
    types = tm.createProto("types.sql")
    with open('types.proto', 'w') as file:
        file.writelines(str(i)+'\n' for i in types[0])
        file.close()

    for table in sqlfiles:
        # table = tm.createTable(table)
        out1, out2 = tm.createProto(table)
        name = f"{table.parts[0]}/{table.stem}.proto"
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
