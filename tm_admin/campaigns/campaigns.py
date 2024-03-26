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
from tm_admin.types_tm import Roles, Mappinglevel, Teammemberfunctions
import concurrent.futures
from cpuinfo import get_cpu_info
from tm_admin.dbsupport import DBSupport
from tm_admin.users.users_class import UsersTable
from osm_rawdata.pgasync import PostgresClient
from tqdm import tqdm
import tqdm.asyncio
from codetiming import Timer
import asyncio

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
        super().__init__('campaigns')

    async def mergeOrganizations(self,
                        inpg: PostgresClient,
                        ):
        """
        A method to merge the contents of the TM campaign_organizations into
        the campaigns table as an array.

        Args:
            inpg (PostgresClient): The input database
        """
        # FIXME: this is a weird table, and only has 4 entries, none of which appear
        # to be in the other tables, so nothing updates.
        table = 'campaign_organisations'
        sql = f"SELECT * FROM {table} ORDER BY campaign_id"
        # print(sql)
        result = await inpg.execute(sql)

        data = dict()
        pbar = tqdm.tqdm(result)
        for record in result:
            sql = f" UPDATE campaigns SET organizations = organizations||{record['organisation_id']} WHERE id={record['campaign_id']};"
            # print(sql)
            await self.pg.execute(sql)

    async def mergeProjects(self,
                        inpg: PostgresClient,
                        ):
        """
        A method to merge the contents of the TM campaign_projects into
        the campaigns table as an array.

        Args:
            inpg (PostgresClient): The input database
        """
        table = 'campaign_projects'
        sql = f"SELECT * FROM {table} ORDER BY campaign_id"
        # print(sql)
        result = await inpg.execute(sql)

        index = 0
        data = dict()
        pbar = tqdm.tqdm(result)

        for record in pbar:
            sql = f" UPDATE campaigns SET projects = projects||{record['project_id']} WHERE id={record['campaign_id']};"
            # print(sql)
            await self.pg.execute(sql)
    
async def main():
    """This main function lets this class be run standalone by a bash script."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", nargs="?", const="0", help="verbose output")
    parser.add_argument("-i", "--inuri", default='localhost/tm4',
                            help="Input database URI")
    parser.add_argument("-o", "--outuri", default='localhost/tm_admin',
                            help="Output database URI")
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

    inpg = PostgresClient()
    await inpg.connect(args.inuri)

    camp = camp = CampaignsDB(args.inuri)
    await camp.connect(args.outuri)

    await camp.mergeProjects(inpg)
    await camp.mergeOrganizations(inpg)
    
if __name__ == "__main__":
    """This is just a hook so this file can be run standalone during development."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
