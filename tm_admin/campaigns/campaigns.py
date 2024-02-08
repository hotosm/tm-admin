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
from tm_admin.types_tm import Userrole, Mappinglevel, Teammemberfunctions
import concurrent.futures
from cpuinfo import get_cpu_info
from tm_admin.dbsupport import DBSupport
from tm_admin.users.users_class import UsersTable
from osm_rawdata.postgres import uriParser, PostgresClient
from tm_admin.types_tm import Userrole
from tqdm import tqdm
from codetiming import Timer
import threading

# Instantiate logger
log = logging.getLogger(__name__)

# The number of threads is based on the CPU cores
info = get_cpu_info()
cores = info["count"] * 2

class CampaignsDB(DBSupport):
    def __init__(self,
                 dburi: str = "localhost/tm_admin",
                ):
        """
        A class to access the campaigns table.

        Args:
            dburi (str): The URI string for the database connection

        Returns:
            (UsersDB): An instance of this class
        """
        self.pg = None
        self.profile = UsersTable()
        self.types = dir(tm_admin.types_tm)
        super().__init__('campaigns', dburi)

    def mergeOrganizations(self):
        """
        A method to merge the contents of the TM campaign_organizations into
        the campaigns table as an array.
        """
        table = 'campaign_organisations'
        pg = PostgresClient("localhost/tm4")
        sql = f"SELECT row_to_json({table}) as row FROM {table} ORDER BY campaign_id"
        # print(sql)
        try:
            result = pg.dbcursor.execute(sql)
        except:
            log.error(f"Couldn't execute query! {sql}")
            return False

        result = pg.dbcursor.fetchall()
        index = 0
        data = dict()
        # pbar = tqdm(result)
        for record in result:
            entry = record[0]   # there's only one item in the input data
            if entry['campaign_id'] not in data:
                data[entry['campaign_id']] = list()
            data[entry['campaign_id']].append(entry['organisation_id'])

        # pbar = tqdm(result)
        for cid, value in data.items():
            sql = f" UPDATE campaigns SET organizations = ARRAY{str(value)} WHERE id={cid};"
            # print(sql)
            self.pg.dbcursor.execute(sql)

    def mergeProjects(self):
        """
        A method to merge the contents of the TM campaign_projects into
        the campaigns table as an array.
        """
        table = 'campaign_projects'
        pg = PostgresClient("localhost/tm4")
        sql = f"SELECT row_to_json({table}) as row FROM {table} ORDER BY campaign_id"
        # print(sql)
        try:
            result = pg.dbcursor.execute(sql)
        except:
            log.error(f"Couldn't execute query! {sql}")
            return False

        result = pg.dbcursor.fetchall()
        index = 0
        data = dict()
        pbar = tqdm(result)
        for record in pbar:
            entry = record[0]   # there's only one item in the input data
            if entry['campaign_id'] not in data:
                data[entry['campaign_id']] = list()
            data[entry['campaign_id']].append(entry['project_id'])

        # pbar = tqdm(result)
        for cid, value in data.items():
            sql = f" UPDATE campaigns SET projects = ARRAY{str(value)} WHERE id={cid};"
            # print(sql)
            self.pg.dbcursor.execute(sql)
    
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

    camp = CampaignsDB(args.uri)
    camp.mergeProjects()
    camp.mergeOrganizations()
    
if __name__ == "__main__":
    """This is just a hook so this file can be run standalone during development."""
    main()
