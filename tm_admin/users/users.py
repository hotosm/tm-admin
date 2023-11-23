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
from datetime import datetime
from dateutil.parser import parse


from tm_admin.users.users_class import UsersTable
from osm_rawdata.postgres import uriParser, PostgresClient

# Instantiate logger
log = logging.getLogger("tm-admin")

class UsersDB(object):
    def __init__(self,
                 dburi: str,
                ):
        self.pg = None
        self.profile = UsersTable()
        if dburi:
            self.pg = PostgresClient(dburi)        

    def createUser(self,
                    profile: UsersTable,
                    ):
        self.profile = profile
        sql = f"INSERT INTO users(id, "
        for column,value in self.profile.data.items():
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
        for column,value in self.profile.data.items():
            try:
                if parse(value):
                    continue
            except:
                pass
            if column == 'id':
                sql += f"nextval('public.users_id_seq'),"
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

        result = self.pg.dbcursor.execute(f"{sql[:-1]});")

    def updateUser(self,
                    profile: UsersTable,
                   ):
        pass

    def resetSequence(self):
        sql = "ALTER SEQUENCE public.users_id_seq RESTART;"
        self.pg.dbcursor.execute(sql)

    def getByID(self,
                id: int,
                ):
        sql = f"SELECT * FROM users WHERE id='{id}'"
        result = self.pg.dbcursor.execute(sql)
        data = dict()
        entry = self.pg.dbcursor.fetchone()
        if entry:
            for column in self.profile.data.keys():
                index = 0
                for column in self.profile.data.keys():
                    data[column] = entry[index]
                    index += 1

        return data

    def getByName(self,
                name: str,
                ):
        sql = f"SELECT * FROM users WHERE name='{name}' LIMIT 1"
        self.pg.dbcursor.execute(sql)
        data = dict()
        entry = self.pg.dbcursor.fetchone()
        for column in self.profile.data.keys():
            index = 0
            for column in self.profile.data.keys():
                data[column] = entry[index]
                index += 1

        return data

    def getAllUsers(self):
        # sql = f"SELECT json_build_object("
        # for column in self.profile.data.keys():
        #     sql += f"'{column}', json_agg(users.{column}),"
        # sql = f"{sql[:-1]}) FROM users;"
        # print(sql)
        sql = f"SELECT * FROM users;"
        self.pg.dbcursor.execute(sql)
        result = self.pg.dbcursor.fetchall()
        out = list()
        if result:
            for entry in result:
                data = dict()
                for column in self.profile.data.keys():
                    index = 0
                    for column in self.profile.data.keys():
                        data[column] = entry[index]
                        index += 1
                out.append(data)
        else:
            log.debug(f"No data returned from query")

        return out

def main():
    """This main function lets this class be run standalone by a bash script."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", nargs="?", const="0", help="verbose output")
    parser.add_argument("-u", "--uri", default='localhost/tm_admin',
                            help="Database URI")
    args = parser.parse_args()

    # if len(argv) <= 1:
    #     parser.print_help()
    #     quit()

    # if verbose, dump to the terminal.
    if args.verbose is not None:
        log.setLevel(logging.DEBUG)
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(threadName)10s - %(name)s - %(levelname)s - %(message)s")
        ch.setFormatter(formatter)
        log.addHandler(ch)

    user = UsersDB(args.uri)
    # user.resetSequence()
    all = user.getAllUsers()
    # Don't pass id, let postgres auto increment
    ut = UsersTable(name='fixme', mapping_level='BEGINNER')
    user.createUser(ut)
    # print(all)

    all = user.getByID(1)
    print(all)
            
    all = user.getByName('fixme')
    print(all)
            
if __name__ == "__main__":
    """This is just a hook so this file can be run standalone during development."""
    main()
