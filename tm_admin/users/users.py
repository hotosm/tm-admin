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
from tm_admin.types_tm import Userrole, Mappinglevel

from tm_admin.dbsupport import DBSupport
from tm_admin.users.users_class import UsersTable
from osm_rawdata.postgres import uriParser, PostgresClient
from tm_admin.types_tm import Userrole

# Instantiate logger
log = logging.getLogger(__name__)


class UsersDB(DBSupport):
    def __init__(self,
                 dburi: str = "localhost/tm_admin",
                ):
        """
        A class to access the users table.

        Args:
            dburi (str): The URI string for the database connection

        Returns:
            (UsersDB): An instance of this class
        """
        self.pg = None
        self.profile = UsersTable()
        self.types = dir(tm_admin.types_tm)
        super().__init__('users', dburi)

    def mergeInterests(self):
        table = 'user_interests'
        # FIXME: this shouldn't be hardcoded
        pg = PostgresClient('localhost/tm4')
        sql = f"SELECT row_to_json({table}) as row FROM {table}"
        print(sql)
        try:
            result = pg.dbcursor.execute(sql)
        except:
            log.error(f"Couldn't execute query! {sql}")
            return False

        result = pg.dbcursor.fetchall()

        data = dict()
        for record in result:
            entry = record[0]   # there's only one item in the input data
            if entry['user_id'] not in data:
                data[entry['user_id']] = list()
            data[entry['user_id']].append(entry['interest_id'])

        for uid, value in data.items():
            sql = f" UPDATE users SET interests = ARRAY{str(value)} WHERE id={uid}"
            print(sql)
            try:
                result = self.pg.dbcursor.execute(f"{sql};")
            except:
                return False

        return True

    def mergeLicenses(self):
        table = 'user_licenses'
        # FIXME: this shouldn't be hardcoded!
        pg = PostgresClient('localhost/tm4')
        sql = f"SELECT row_to_json({table}) as row FROM {table}"
        # print(sql)
        try:
            result = pg.dbcursor.execute(sql)
        except:
            log.error(f"Couldn't execute query! {sql}")
            return False

        result = pg.dbcursor.fetchall()

        for record in result:
            sql = f" UPDATE users SET licenses = ARRAY[{record[0]['license']}] WHERE id={record[0]['user']}"
            print(sql)
            try:
                result = self.pg.dbcursor.execute(f"{sql};")
            except:
                return False

        return True

    def mergeFavorites(self):
        table = 'project_favorites'
        pg = PostgresClient(inuri)
        sql = f"SELECT row_to_json({table}) as row FROM {table}"
        # print(sql)
        try:
            result = pg.dbcursor.execute(sql)
        except:
            log.error(f"Couldn't execute query! {sql}")
            return False

    # These are just convience wrappers to support the REST API.
    def updateRole(self,
                   id: int,
                   role: Userrole,
                   ):
        """
        Update the role for a user.

        Args:
            id (int): The users ID
            role (Userrole): The new role.
        """
        role = Userrole(role)
        return self.updateColumn(id, {'role': role.name})

    def updateMappingLevel(self,
                   id: int,
                   level: Mappinglevel,
                   ):
        """
        Update the mapping level for a user.

        Args:
            id (int): The users ID.
            level (Mappinglevel): The new level.
        """
        mlevel = Mappinglevel(level)
        return self.updateColumn(id, {'mapping_level': mlevel.name})

    def updateExpert(self,
                   id: int,
                   mode: bool,
                   ):
        """
        Toggle the expert mode for a user.

        Args:
            id (int): The users ID.
            mode (bool): The new mode..
        """
        return self.updateColumn(id, {'expert_mode': mode})

    def getRegistered(self,
                      start: datetime,
                      end: datetime,
                      ):
        """
        Get all users registered in this timeframe.

        Args:
            start (datetime): The starting timestamp
            end (datetime): The starting timestamp

        Returns:
            (list): The users registered in this timeframe.
        """

        where = f" date_registered > '{start}' and date_registered < '{end}'"
        return self.getByWhere(where)

def main():
    """This main function lets this class be run standalone by a bash script."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", nargs="?", const="0", help="verbose output")
    parser.add_argument("-u", "--uri", default='localhost/tm_admin', help="Database URI")
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

    user = UsersDB(args.uri)

    if user.mergeInterests():
        log.info("UserDB.mergeInterests worked!")

    if user.mergeLicenses():
        log.info("UserDB.mergeLicenses worked!")

    # user.resetSequence()
    # all = user.getAll()
    # # Don't pass id, let postgres auto increment
    # ut = UsersTable(name='test', mapping_level='BEGINNER',
    #                 email_address='foo@bar.com')
    # user.createTable(ut)
    # # print(all)

    # all = user.getByID(1)
    # print(all)
            
    # all = user.getByName('test')
    # print(all)

    # ut = UsersTable(name='foobar', email_address="bar@foo.com", mapping_level='INTERMEDIATE')
    # This is obviously only for manual testing
    #user.updateTable(ut, 17)

if __name__ == "__main__":
    """This is just a hook so this file can be run standalone during development."""
    main()
