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
from tm_admin.organizations.organizations_class import OrganizationsTable
from tm_admin.users.users_class import UsersTable
from tm_admin.teams.teams_class import TeamsTable
from tm_admin.tasks.tasks_class import TasksTable
from tm_admin.projects.projects_class import ProjectsTable
from tm_admin.campaigns.campaigns_class import CampaignsTable
from tm_admin.messages.messages_class import MessagesTable
from tm_admin.organizations.organizations_class import OrganizationsTable
from osm_rawdata.pgasync import PostgresClient
from shapely.geometry import Polygon, Point, shape
import asyncio
from codetiming import Timer

# Instantiate logger
log = logging.getLogger(__name__)

class DBSupport(object):
    def __init__(self,
                 table: str,
                ):
        """
        A base class since all tables have the same structure for queries.

        Args:
            table (str): The table to use for this connection.

        Returns:
            (DBSupport): An instance of this class
        """
        self.pg = None
        self.table = table
        self.columns = None

    async def connect(self,
                    dburi: str = "localhost/tm_admin",
                    ):
        """
        Args:
            dburi (str): The URI string for the database connection.
        """
        profile = f"{self.table.capitalize()}Table()"
        self.profile = eval(profile)
        if dburi:
            self.pg = PostgresClient()
            await self.pg.connect(dburi)
        self.types = dir(tm_admin.types_tm)
        # self.schema = self.getColumns(table)
        #self.accessors = dict()

    async def createTable(self,
                    obj,
                    ):
        """
        Create a table in a postgres database.

        Args:
            obj: The config data for the table.
        """
        sql = f"INSERT INTO {self.table}(id, "
        for column,value in obj.data.items():
            # print(f"{column} is {type(value)}")
            if type(value) == str:
                # FIXME: for now ignore timestamps, as they're meaningless
                # between projects
                try:
                    if parse(value):
                        continue
                except:
                    # it's a string, but not a date
                    pass
            if value is not None:
                sql += f"{column},"
        sql = sql[:-1]
        sql += f") VALUES("
        for column,value in obj.data.items():
            try:
                if parse(value):
                    continue
            except:
                pass
            if column == 'id':
                sql += f"nextval('public.{self.table}_id_seq'),"
                continue
            if value is None:
                continue
            elif type(value) == datetime:
                continue
            elif type(value) == int:
                sql += f"{value},"
            elif type(value) == bool:
                if value:
                    sql += f"true,"
                else:
                    sql += f"false,"
            elif type(value) == str:
                sql += f"'{value}',"

        #print(sql[:-1])
        result = await self.pg.execute(f"{sql[:-1]});")

    async def updateTable(self,
                    id: int = None,
                    ):
        """
        Updates an existing table in the database

        Args:
            id (int): The ID of the dataset to update
        """
        sql = f"UPDATE {self.table} SET"
        if not id:
            id = profile.data['id']
        for column,value in self.profile.data.items():
            name = column.replace('_', '').capitalize()
            if name in self.types:
                # FIXME: this needs to not be hardcoded!
                tmp = tm_admin.types_tm.Mappinglevel._member_names_
                if type(value) == str:
                    level = value
                else:
                    level = tmp[value-1]
                sql += f" {column}='{level}'"
                continue
            if value:
                try:
                    # FIXME: for now ignore timestamps, as they're meaningless
                    # between projects
                    if parse(value):
                        continue
                except:
                    # it's a string, but not a date
                    pass
                sql += f" {column}='{value}',"
        sql += f" WHERE id='{id}'"
        # print(sql)
        result = await self.pg.execute(f"{sql[:-1]}';")

    async def resetSequence(self):
        """
        Reset the postgres sequence to zero.
        """
        sql = f"ALTER SEQUENCE public.{self.table}_id_seq RESTART;"
        await self.pg.execute(sql)

    async def getByID(self,
                id: int,
                ):
        """
        Return the data for the ID in the table.

        Args:
            id (int): The ID of the dataset to retrieve.

        Returns:
            (dict): The results of the query
        """

        data = await self.getByWhere(f" id={id}")
        if len(data) == 0:
            return dict()
        else:
            return data[0][0]

    async def getByName(self,
                name: str,
                ):
        """
        Return the data for the name in the table.

        Args:
            name (str): The name of the dataset to retrieve.

        Returns:
            (list): The results of the query
        """
        data = await self.getByWhere(f" name='{name}'")

        if len(data) == 0:
            return dict()
        else:
            return data[0][0]

    async def getAll(self):
        """
        Return all the data in the table.

        Returns:
            (list): The results of the query
        """
        sql = f"SELECT row_to_json({self.table}) as row FROM {self.table}"
        # print(sql)
        result = list()
        result = await self.pg.execute(sql)

        return result

    async def getByWhere(self,
                where: str,
                ):
        """
        Return the data for the where clause in the table.

        Args:
            where (str): The where clause of the dataset to retrieve.

        Returns:
            (list): The results of the query
        """
        sql = f"SELECT row_to_json({self.table}) as row FROM {self.table} WHERE {where}"
        # print(sql)
        result = await self.pg.execute(sql)

        return result

    async def getByLocation(self,
                location: Point,
                table: str = 'projects',
                ):
        """
        Return the database records in a table using GPS coordinates.

        Args:
            location (Point): The location to use to find the project or task.

        Returns:
            (list): The results of the query
        """
        data = dict()
        ewkt = shape(location)
        sql = f"SELECT row_to_json({self.table}) as row FROM {table} WHERE ST_CONTAINS(ST_GeomFromEWKT('SRID=4326;{ewkt}') geom)"
        result = await self.pg.execute(sql)

        return result

    async def deleteByID(self,
                id: int,
                ):
        """
        Delete the record for the ID in the table.

        Args:
            id (int): The ID of the dataset to delete.
        """
        sql = f"DELETE FROM {self.table} WHERE id='{id}'"
        result = self.pg.execute(sql)
        return True

    async def getColumn(self,
                 uid: int,
                 column: str,
                 ):
        """
        This gets a single column from the database.

        Args:
            uid (int): The ID to get
            column (str): The column.

        Returns:
            (list): The column values
        """
        sql = f"SELECT {column} FROM {self.table} WHERE id={uid}"
        result = await self.pg.execute(sql)

        if len(result) > 0:
            return result[0][column]
        else:
            return None

    async def updateColumn(self,
                    uid: int,
                    data: dict,
                    ):
        """
        This updates a single column in the database. If you want to update multiple columns,
        use self.updateTable() instead.

        Args:
            uid (int): The ID of the user to update
            data (dict): The column and new value
        """
        [[column, value]] = data.items()
        sql = f"UPDATE {self.table} SET {column}='{value}' WHERE id='{uid}'"
        # print(sql)
        await self.pg.execute(f"{sql};")

        return True

    async def removeColumn(self,
                    uid: int,
                    data: dict,
                    ):
        """
        This updates a single array column in the database.
        If you want to update multiple columns, use self.updateTable()
        instead.

        Args:
            uid (int): The ID of the user to update
            data (dict): The column and new value
        """
        [[column, value]] = data.items()
        aval = "'{" + f"{value}" + "}"
        sql = f"UPDATE {self.table} SET {column}=array_remove({column}, {value}) WHERE id='{uid}'"
        # print(sql)
        result = await self.pg.execute(f"{sql};")

    async def appendColumn(self,
                    uid: int,
                    data: dict,
                    ):
        """
        This updates a single array column in the database.
        If you want to update multiple columns, use self.updateTable()
        instead.

        Args:
            uid (int): The ID of the user to update
            data (dict): The column and new value
        """
        [[column, value]] = data.items()
        aval = "'{" + f"{value}" + "}"
        sql = f"UPDATE {self.table} SET {column}={column}||{aval}' WHERE id='{uid}'"
        #print(sql)
        result = await self.pg.execute(f"{sql};")

    async def renameTable(self,
                        table: str,
                        ):
        """
        """
        sql = f"DROP TABLE IF EXISTS {table}_bak"
        result = await self.pg.execute(sql)
        sql = f"ALTER TABLE {table} RENAME TO {table}_bak;"
        result = await self.pg.execute(sql)
        sql = f"ALTER TABLE new_{table} RENAME TO {table};"
        result = await self.pg.execute(sql)
        sql = f"DROP TABLE IF EXISTS {table}_bak CASCADE"
        result = await self.pg.execute(sql)

        print(f"renameTable{self.pg.dburi}")
        # These are copied for the TM4 database, but have been merged
        # into the local database so JOIN works faster than remote
        # access, or looping through tons of data in Python.
        sql = f"DROP TABLE IF EXISTS user_interests CASCADE"
        result = await self.pg.execute(sql)
        sql = f"DROP TABLE IF EXISTS user_licenses CASCADE"
        result = await self.pg.execute(sql)
        sql = f"DROP TABLE IF EXISTS team_members CASCADE"
        result = await self.pg.execute(sql)

    async def copyTable(self,
                        table: str,
                        remote: PostgresClient,
                        ):
        """
        Use DBLINK to copy a table from the Tasking Manager
        database to a local table so JOINing is much faster.

        Args:
            table (str): The table to copy
        """
        timer = Timer(initial_text=f"Copying {table}...",
                      text="copying {table} took {seconds:.0f}s",
                      logger=log.debug,
                    )
        # Get the columns from the remote database table
        self.columns = await remote.getColumns(table)

        print(f"SELF: {self.pg.dburi}")
        print(f"REMOTE: {remote.dburi}")

        # Do we already have a local copy ?
        sql = f"SELECT FROM pg_tables WHERE schemaname = 'public' AND tablename  = '{table}'"
        result = await self.pg.execute(sql)
        print(result)

        # cleanup old temporary tables in the current database
        # drop = ["DROP TABLE IF EXISTS users_bak",
        #         "DROP TABLE IF EXISTS user_interests",
        #         "DROP TABLE IF EXISTS foo"]
        # result = await pg.pg.executemany(drop)
        sql = f"DROP TABLE IF EXISTS new_{table} CASCADE"
        result = await self.pg.execute(sql)
        sql = f"DROP TABLE IF EXISTS {table}_bak CASCADE"
        result = await self.pg.execute(sql)
        timer.start()
        dbuser = self.pg.dburi["dbuser"]
        dbpass = self.pg.dburi["dbpass"]
        sql = f"CREATE SERVER IF NOT EXISTS pg_rep_db FOREIGN DATA WRAPPER dblink_fdw  OPTIONS (dbname 'tm4');"
        data = await self.pg.execute(sql)

        sql = f"CREATE USER MAPPING IF NOT EXISTS FOR {dbuser} SERVER pg_rep_db OPTIONS ( user '{dbuser}', password '{dbpass}');"
        result = await self.pg.execute(sql)

        # Copy table from remote database so JOIN is faster when it's in the
        # same database
        #columns = await sel.getColumns(table)
        log.warning(f"Copying a remote table is slow, but faster than remote access......")
        sql = f"SELECT * INTO {table} FROM dblink('pg_rep_db','SELECT * FROM {table}') AS {table}({self.columns})"
        print(sql)
        result = await self.pg.execute(sql)

        return True

async def main():
    """This main function lets this class be run standalone by a bash script."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", nargs="?", const="0", help="verbose output")
    parser.add_argument("-u", "--uri", default='localhost/tm_admin',
                            help="Database URI")
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

    org = DBSupport('organizations')
    await org.connect(args.uri)
    # organization.resetSequence()
    all = await org.getAll()

    # Don't pass id, let postgres auto increment
    ut = OrganizationsTable(name='test org', slug="slug", type=1)
#                            orgtype=tm_admin.types_tm.Organizationtype.FREE)
    await org.createTable(ut)
    # print(all)

    all = await org.getByID(1)
    print(all)
            
    all = await org.getByName('fixme')
    print(all)
            
if __name__ == "__main__":
    """This is just a hook so this file can be run standalone during development."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
