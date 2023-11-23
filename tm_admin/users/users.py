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

from tm_admin.users.users_class import UsersTable
from osm_rawdata.postgres import uriParser, PostgresClient


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

    def updateUser(self,
                    profile: UsersTable,
                   ):
        pass

    def getByID(self,
                id: int,
                ):
        # SELECT json_agg(tags)::jsonb FROM nodes LIMIT 1;
        pass
    
    def getByName(self,
                  name: str,
                ):
        pass
    
    def getAllUsers(self):
        sql = f"SELECT json_build_object("
        for column in self.profile.data.keys():
            sql += f"'{column}', json_agg(users.{column}),"
        sql = sql[:-1]
        sql += ") FROM users;"
        result = self.pg.dbcursor.execute(sql)

        return result

def main():
    """This main function lets this class be run standalone by a bash script."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", nargs="?", const="0", help="verbose output")
    parser.add_argument("-u", "--uri", default='localhost/tm_admin',
                            help="Database URI")
    args = parser.parse_args()

    if len(argv) <= 1:
        parser.print_help()
        # quit()

    # if verbose, dump to the terminal.
    if args.verbose is not None:
        log.setLevel(logging.DEBUG)
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(threadName)10s - %(name)s - %(levelname)s - %(message)s")
        ch.setFormatter(formatter)
        log.addHandler(ch)

    user = UsersDB(args.uri)
    all = user.getAllUsers()
    print(all)
            
if __name__ == "__main__":
    """This is just a hook so this file can be run standalone during development."""
    main()
