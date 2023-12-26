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
import psycopg2.extensions
from datetime import datetime
from dateutil.parser import parse
import tm_admin.types_tm
from tm_admin.organizations.organizations_class import OrganizationsTable
from tm_admin.users.users_class import UsersTable
from tm_admin.teams.teams_class import TeamsTable
from tm_admin.tasks.tasks_class import TasksTable
from tm_admin.projects.projects_class import ProjectsTable
from tm_admin.organizations.organizations_class import OrganizationsTable
from osm_rawdata.postgres import uriParser, PostgresClient
from shapely.geometry import Polygon, Point, shape

# Instantiate logger
log = logging.getLogger(__name__)

class DBSupport(object):
    def __init__(self,
                 table: str,
                 dburi: str = "localhost/tm_admin",
                ):
        """
        A base class since all tables have the same structure for queries.

        Args:
            table (str): The table to use for this connection.
            dburi (str): The URI string for the database connection.

        Returns:
            (DBSupport): An instance of this class
        """
        self.pg = None
        self.table = table
        profile = f"{table.capitalize()}Table()"
        self.profile = eval(profile)
        if dburi:
            self.pg = PostgresClient(dburi)
        self.types = dir(tm_admin.types_tm)
        # self.schema = self.getColumns(table)
        #self.accessors = dict()

    def createTable(self,
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
        result = self.pg.dbcursor.execute(f"{sql[:-1]});")

    def updateTable(self,
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
        result = self.pg.dbcursor.execute(f"{sql[:-1]}';")

    def resetSequence(self):
        """
        Reset the postgres sequence to zero.
        """
        sql = f"ALTER SEQUENCE public.{self.table}_id_seq RESTART;"
        self.pg.dbcursor.execute(sql)

    def getByID(self,
                id: int,
                ):
        """
        Return the data for the ID in the table.

        Args:
            id (int): The ID of the dataset to retrieve.

        Returns:
            (dict): The results of the query
        """

        data = self.getByWhere(f" id={id}")
        if len(data) == 0:
            return dict()
        else:
            return data[0][0]

    def getByName(self,
                name: str,
                ):
        """
        Return the data for the name in the table.

        Args:
            name (str): The name of the dataset to retrieve.

        Returns:
            (list): The results of the query
        """
        data = self.getByWhere(f" name='{name}'")

        if len(data) == 0:
            return dict()
        else:
            return data[0][0]

    def getAll(self):
        """
        Return all the data in the table.

        Returns:
            (list): The results of the query
        """
        sql = f"SELECT row_to_json({self.table}) as row FROM {self.table}"
        self.pg.dbcursor.execute(sql)
        result = self.pg.dbcursor.fetchall()

        return result

    def getByWhere(self,
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
        self.pg.dbcursor.execute(sql)
        result = self.pg.dbcursor.fetchall()

        return result

    def getByLocation(self,
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
        self.pg.dbcursor.execute(sql)
        result = self.pg.dbcursor.fetchall()

        return result

    def deleteByID(self,
                id: int,
                ):
        """
        Delete the record for the ID in the table.

        Args:
            id (int): The ID of the dataset to delete.
        """
        sql = f"DELETE FROM {self.table} WHERE id='{id}'"
        result = self.pg.dbcursor.execute(sql)
        return True

    def getColumn(self,
                 uid: int,
                 column: str,
                 ):
        """
        This gets a single column from the database.

        Args:
            uid (int): The ID of the user to update.
            column (str): The column.

        Returns:
            (list): The column values
        """
        sql = f"SELECT {column} FROM {self.table} WHERE id={uid}"
        try:
            self.pg.dbcursor.execute(sql)
        except:
            log.error(f"Couldn't execute query {sql}")

        result = self.pg.dbcursor.fetchall()

        if len(result) == 1 and len(result[0]) == 1:
            if result[0][0] is None:
                return list()

        return result

    def updateColumn(self,
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
        try:
            result = self.pg.dbcursor.execute(f"{sql};")
            return True
        except:
            return False

    def appendColumn(self,
                    uid: int,
                    data: dict,
                    ):
        """
        This updates a single array column in the database. If you want to update
        multiple columns, use self.updateTable() instead.

        Args:
            uid (int): The ID of the user to update
            data (dict): The column and new value
        """
        [[column, value]] = data.items()
        aval = "'{" + f"{value}" + "}"
        sql = f"UPDATE {self.table} SET {column}={column}||{aval}' WHERE id='{uid}'"
        print(sql)
        try:
            result = self.pg.dbcursor.execute(f"{sql};")
            return True
        except:
            return False

def main():
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

    org = DBSupport('organizations', args.uri)
    # organization.resetSequence()
    all = org.getAll()

    # Don't pass id, let postgres auto increment
    ut = OrganizationsTable(name='test org', slug="slug", orgtype=1)
#                            orgtype=tm_admin.types_tm.Organizationtype.FREE)
    org.createTable(ut)
    # print(all)

    all = org.getByID(1)
    print(all)
            
    all = org.getByName('fixme')
    print(all)
            
if __name__ == "__main__":
    """This is just a hook so this file can be run standalone during development."""
    main()
