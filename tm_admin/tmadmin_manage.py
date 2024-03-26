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
from osm_rawdata.pgasync import PostgresClient
from tm_admin.proto import ProtoBuf
from tm_admin.yamlfile import YamlFile
from tm_admin.generator import Generator
from tm_admin.tmdb import TMImport
from tm_admin.users.users import UsersDB
from tm_admin.projects.projects import ProjectsDB
from tm_admin.tasks.tasks import TasksDB
from tqdm import tqdm
import tqdm.asyncio
import asyncio

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

    async def connect(self,
                inuri: str,
                ):
        """
        This class contains support to accessing a Tasking Manager database, and
        importing it in the TM Admin database. This works because the TM Admin
        database schema is based on the ones used by FMTM and TM. The schemas
        have been merged into a single one, and all of the column names are
        the same across the two schemas except in a few rare cases.

        The other change is in TM many columns are enums, but the database type
        is in. The integer values from TM are converted to the proper TM Admin
        enum value.

        Args:
            inuri (str): The URI for the TM database
        """
        # The Tasking Manager database
        self.pg = PostgresClient()
        await self.pg.connect(inuri)

    async def applyDiff(self,
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

    async def dump(self):
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

    async def updateDB(self,
                progs: list = list(),
                ):
        """
        Create a postgres database.

        Args:
            progs (str): The programs to run
        """
        # This requires all the generated files have been installed
        for sql in progs:
            log.info(f"Updating table {sql} in database")

    async def mergeAuxTables(self,
                tables: list,
                inuri: str,
                outuri: str,
                ):
        """
        Merge the data from a TM table into TM Admin one. These are tables
        that get merged into arrays or nested tables.

        Args:
            tables (list): The tables to import data from and to
            inuri (str): The input database
            outuri (str): The output database
        """
        # This requires all the generated files have been installed
        for table in tables:
            log.info(f"Importing the '{table}' table")
            # Instantiate the class
            obj = eval(f"{table.capitalize()}DB")
            func = obj()
            await func.mergeAuxTables(inuri, outuri)

    async def importTables(self,
                tables: list,
                tmi: TMImport,
                ):
        """
        Import the data from a TM table into TM Admin one.

        Args:
            tables (list): The tables to import data from and to
            tmi (TMImport): An instantiation of the class that imports data
        """
        # This requires all the generated files have been installed
        for table in tables:
            log.info(f"Importing the '{table}' table")
            # Each table has it's own config file
            await tmi.loadConfig(table)
            await tmi.importDB(table)

    async def createDB(self,
                files: list,
                tmi: TMImport,
                ):
        """
        Create a postgres database.

        Args:
            files (list): the tables to create from their SQL files
            tmi (TMImport): An instantiation of the class that imports data
        """
        sql = "CREATE EXTENSION IF NOT EXISTS postgis"
        await self.pg.execute(sql)

        # The types file must be imported first
        log.info(f"Importing Types into {self.pg.dburi['dbname']}")
        result = await self.createTable(f"{rootdir}/types_tm.sql")
        # await self.pg.execute(query)

        # These are all nested tables, so need to be defined first.
        nested = ["projects/project_chat", "projects/projects_teams", "teams/team_members", "tasks/task_history", "tasks/task_invalidation_history", "tasks/task_annotations"]
        for table in nested:
            await tmi.loadConfig(table)
            path = Path(table)
            result = await self.createTable(f"{rootdir}/{table}.sql")
            #await tmi.importDB(path.name)

        # This requires all the generated files have been installed
        for sql in files:
            log.info(f"Creating table {sql} in database")
            result = await self.createTable(f"{rootdir}/{sql}")
            # await self.pg.execute(query)

    async def createTable(self,
                    sqlfile: str,
                    ):
        """
        Create a table in the database.

        Args:
            sqlfile (str): The SQL schema for this table

        Returns:
            (bool): The table creation status
        """
        sql = ""
        with open(sqlfile, 'r') as file:
            # cleanup the file before submitting
            for line in file.readlines():
                if line[:2] != '--' and len(line) > 0:
                    sql += line[:-1].replace("\t", " ")
            file.close()
        # FIXME:  asyncpg only allows one SQL statement per execute(), so we
        # break up the compound statement into indivigual commands. psysopg2
        # does allow this, but for ascypg, this needs to use prepared
        # statements.
        for cmd in sql.split(";"):
            # print(cmd)
            result = await self.pg.execute(cmd)

        # path = Path(sqlfile)
        # version = f"INSERT INTO schemas(schema, version) VALUES('{sqlfile.stem}', 1.0)"
        # result = await self.pg.execute(version)

        return sql

    async def readDiff(self,
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

async def main():
    """This main function lets this class be run standalone by a bash script."""
    parser = argparse.ArgumentParser(
        prog="config",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Manage the postgres database for the tm-admin project",
        epilog="""
        An example data flow is:

        # Generate all language binding files
        tmadmin_manage.py -v -c generate */*.yaml

        # Create the database tables
        tmadmin_manage.py -v -c create */*.sql

        # Import the data for the all primary tables.
        tmadmin_manage.py -v -c import

        # Import the data for just the users table
        tmadmin_manage.py -v -c import users
        """,
    )
    choices = ['generate', 'create', 'import', 'merge', 'update', 'migrate']
    parser.add_argument("-v", "--verbose", nargs="?", const="0",
                        help="verbose output")
    # parser.add_argument("-d", "--diff", help="SQL file diff for migrations")
    # parser.add_argument("-p", "--proto", default='types.yaml', help="Generate the .proto file from the YAML file")
    parser.add_argument("-i", "--inuri", default='localhost/tm4',
                        help="Input Database URI")
    parser.add_argument("-o", "--outuri", default='localhost/tm_admin',
                        help="Output Database URI")
    parser.add_argument("-c", "--cmd", choices=choices, default='generate',
                            help="Command")
    # parser.add_argument("-t", "--table", choices=choices, help="The table to import")
    args, known = parser.parse_known_args()

    if len(argv) <= 1:
        parser.print_help()
        quit()

    if len(known) == 0:
        known = ["users", "projects", "campaigns", "organizations", "messages", "teams", "tasks"]

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
    tm = TmAdminManage()
    await tm.connect(args.outuri)
    # tm.createDB()

    # This database tables stores the versions of the table schemas,
    # and is only used for updating the table schemas.
    result = await tm.createTable(f"{rootdir}/schemas.sql")
    # await tm.pg.execute(result)

    result = await tm.createTable(f"{rootdir}/types_tm.sql")
    await tm.pg.execute(result)

    # This class generates all the output files.
    if args.cmd == 'generate':
        gen = Generator()
        # Generate all the output files
        log.info(f"Generating all output files.")
        for yamlfile in known:
            gen.readConfig(yamlfile)
            out = gen.createSQLTable()
            name = yamlfile.replace('.yaml', '.sql')
            with open(name, 'w') as file:
                file.write(out)
                log.info(f"Wrote {name} to disk")
                file.close()
            # await tm.createTable(name)
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
        # FIXME: teams won't load unless this nested table is there first.
        # files = ['teams/team_members.sql']
        # files += known
        tmi = TMImport()
        await tmi.connect(args.inuri, args.outuri)
        await tm.createDB(known, tmi)
    elif args.cmd == 'import':
        tmi = TMImport()
        await tmi.connect(args.inuri, args.outuri)
        await tm.importTables(known, tmi)
    elif args.cmd == 'merge':
        aux = ["projects", "users", "tasks"]
        await tm.mergeAuxTables(aux, args.inuri, args.outuri)
    elif args.cmd == 'update':
        tm.updateDB(known)
    elif args.cmd == 'migrate':
        # tm.migrateDB(known)
        pass

    # tm.dump()

if __name__ == "__main__":
    """This is just a hook so this file can be run standalone during development."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
