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
from tm_admin.dbsupport import DBSupport
from tm_admin.organizations.organizations_class import OrganizationsTable
from osm_rawdata.postgres import uriParser, PostgresClient

# Instantiate logger
log = logging.getLogger(__name__)

class OrganizationsDB(object):
    def __init__(self,
                 dburi: str = "localhost/tm_admin",
                ):
        self.pg = None
        self.profile = OrganizationsTable()
        if dburi:
            self.pg = PostgresClient(dburi)
        self.types = dir(tm_admin.types_tm)
        self.queries = DBSupport('organizations')

    def createOrganization(self,
                    profile: OrganizationsTable,
                    ):
        self.profile = profile
        self.queries.createTable(profile)

    def updateOrganization(self,
                    profile: OrganizationsTable,
                    id: int = None,
                    ):
        self.profile = profile
        sql = f"UPDATE organizations SET"
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
        sql = "ALTER SEQUENCE public.organizations_id_seq RESTART;"
        self.pg.dbcursor.execute(sql)

    def getByID(self,
                id: int,
                ):
        data = self.queries.getByID(id)
        return data

    def getByName(self,
                name: str,
                ):
        data = self.queries.getByName(name)
        return data

    def getAllOrganizations(self):
        data = self.queries.getAll()
        return data

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

    organization = OrganizationsDB(args.uri)
    # organization.resetSequence()
    all = organization.getAllOrganizations()
    # Don't pass id, let postgres auto increment
    ut = OrganizationsTable(name='fixme', slug='slug', orgtype='FREE')
    organization.createOrganization(ut)
    # print(all)

    all = organization.getByID(1)
    print(all)
            
    all = organization.getByName('fixme')
    print(all)
            
if __name__ == "__main__":
    """This is just a hook so this file can be run standalone during development."""
    main()
