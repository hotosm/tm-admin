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
from tm_admin.teams.teams_class import TeamsTable
from osm_rawdata.postgres import uriParser, PostgresClient

# Instantiate logger
log = logging.getLogger(__name__)

class TeamsDB(DBSupport):
    def __init__(self,
                 dburi: str = "localhost/tm_admin",
                ):
        """
        A class to access the teams table.

        Args:
            dburi (str): The URI string for the database connection

        Returns:
            (TeamsDB): An instance of this class
        """
        self.pg = None
        self.profile = TeamsTable()
        self.types = dir(tm_admin.types_tm)
        super().__init__('teams', dburi)

    async def mergeTeams(self,
                        inpg: PostgresClient,
                        ):
        table = 'team_members'
        log.info(f"Merging team members table...")
        timer = Timer(text="merging team members table took {seconds:.0f}s")
        timer.start()
        sql = f"SELECT * FROM {table} ORDER BY user_id"
        #print(sql)
        result = await inpg.execute(sql)

        pbar = tqdm.tqdm(result)
        for record in pbar:
            func = record['function']
            tmfunc = Teammemberfunctions(func)
            sql = f"UPDATE {self.table} SET team_members.team={record['team_id']}, team_members.active={record['active']}, team_members.function='{tmfunc.name}' WHERE id={record['user_id']}"
            print(sql)
            result = await inpg.execute(sql)

        timer.stop()
        return True

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

    team = TeamsDB(args.uri)

    await self.mergeTeams(inpg)
    log.info("UserDB.mergeTeams worked!")
    
    # user.resetSequence()
    all = team.getAll()
    # Don't pass id, let postgres auto increment
    ut = TeamsTable(name='test', organisation_id=1,
                    visibility='PUBLIC')
    team.createTable(ut)
    # print(all)

    all = team.getByID(1)
    print(all)
            
    all = team.getByName('test')
    print(all)

    ut = TeamsTable(name='foobar', organisation_id=1, visibility='PUBLIC')
    # This is obviously only for manual testing
    # team.updateTable(ut, 17)

if __name__ == "__main__":
    """This is just a hook so this file can be run standalone during development."""
    main()
