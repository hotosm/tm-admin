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
from pathlib import Path
from sys import argv
from osm_rawdata.postgres import uriParser, PostgresClient
from tm_admin.proto import ProtoBuf
from tm_admin.yamlfile import YamlFile
from tm_admin.generator import Generator


# Instantiate logger
log = logging.getLogger(__name__)

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
                files: list = list(),
                ):
        """
        Create a postgres database.

        Args:

        Returns:

        """
        # sql = "CREATE EXTENSION IF NOT EXISTS postgis; CREATE EXTENSION IF NOT EXISTS hstore"
        # FIXME: CREATE DATABASE cannot run inside a transaction block
        # self.pg.createDB(self.dburi)
        # The types file must be imported first
        with open(f"{rootdir}/types_tm.sql", 'r') as file:
            self.pg.dbcursor.execute(file.read())
            file.close()

        # This requires all the generated files have been installed
        for sql in files:
            log.info(f"Creating table {sql} in database")
            with open(f"{rootdir}/{sql}", 'r') as file:
                self.pg.dbcursor.execute(file.read())
                file.close()

    def createTable(self,
                    sqlfile: str,
                    ):
        """
        Create a table in the database.

        Args:
            sqlfile (str): The SQL schema for this table
            dburi (str): The URI string for the database connection.

        Returns:
            (bool): The table creation status
        """
        sql = ""
        with open(sqlfile, 'r') as file:
            # cleanup the file before submitting
            for line in file.readlines():
                if line[:2] != '--' and len(line) > 0:
                    sql += line
            file.close()
            return self.pg.createTable(sql)

        path = Path(sqlfile)
        version = f"INSERT INTO schemas(schema, version) VALUES('{sqlfile.stem}', 1.0)"
        result = self.pg.dbcursor.execute(version)

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
    choices = ['generate', 'create', 'migrate', 'load']
    parser.add_argument("-v", "--verbose", nargs="?", const="0", help="verbose output")
    # parser.add_argument("-d", "--diff", help="SQL file diff for migrations")
    # parser.add_argument("-p", "--proto", help="Generate the .proto file from the YAML file")
    parser.add_argument("-u", "--uri", default='localhost/tm_admin',
                            help="Database URI")
    parser.add_argument("-c", "--cmd", choices=choices, default='generate',
                            help="Command")
    args, known = parser.parse_known_args()

    if len(argv) <= 1:
        parser.print_help()
        quit()

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

    # The base class that does all the work
    tm = TmAdminManage(args.uri)
    # tm.createDB()

    # This database tables stores the versions of the table schemas,
    # and is only used for updating the table schemas.
    result = tm.createTable(f"{rootdir}/schemas.sql")

    # This class generates all the output files.
    if args.cmd == 'generate':
        gen = Generator()
        # Generate all the output file
        for yamlfile in known:
            gen.readConfig(yamlfile)
            out = gen.createSQLTable()
            name = yamlfile.replace('.yaml', '.sql')
            with open(name, 'w') as file:
                file.write(out)
                log.info(f"Wrote {name} to disk")
                file.close()
            tm.createTable(name)
            name = yamlfile.replace('.yaml', '.proto')
            out = gen.createProtoMessage()
            with open(name, 'w') as file:
                file.writelines([str(i)+'\n' for i in out])
                log.info(f"Wrote {name} to disk")
                file.close()
            out = gen.createPyClass()
            py = yamlfile.replace('.yaml', '_class.py')
            with open(py, 'w') as file:
                file.write(out)
                log.info(f"Wrote {py} to disk")
                file.close()
            out = gen.createPyMessage()
            py = yamlfile.replace('.yaml', '_proto.py')
            with open(py, 'w') as file:
                file.write(out)
                log.info(f"Wrote {py} to disk")
                file.close()
    elif args.cmd == 'create':
        tm.createDB(known)
    elif args.cmd == 'migrate':
        # tm.migrateDB(known)
        pass
    elif args.cmd == 'load':
        # tm.migrateDB(known)
        pass
    # tm.dump()

if __name__ == "__main__":
    """This is just a hook so this file can be run standalone during development."""
    main()
