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

"""
This class is used to import the auxilary tables into the primary table
"""

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
from tm_admin.users.users_class import UsersTable
from osm_rawdata.pgasync import PostgresClient
from tm_admin.types_tm import Userrole
from tqdm import tqdm
import tqdm.asyncio
import asyncio
from codetiming import Timer
from tm_admin.dbsupport import DBSupport

# Instantiate logger
log = logging.getLogger(__name__)

# The number of threads is based on the CPU cores
info = get_cpu_info()
cores = info["count"] * 2

async def licensesThread(
        licenses: list,
        db: PostgresClient,
        ):
    pbar = tqdm.tqdm(licenses)
    for record in pbar:
        sql = f" UPDATE users SET licenses = licenses||ARRAY[{record[1]}] WHERE id={record[0]}"
        # print(sql)
        result = await db.execute(sql)

    return True

async def interestsThread(
    interests: list,
    db: PostgresClient,
):
    """Thread to handle importing

    Args:
        interests (list): The list of records to import
        db (PostgresClient): A database connection
    """
    pbar = tqdm.tqdm(interests)
    for record in pbar:
        for id, array in record.items():
            sql = f" UPDATE users SET interests = interests||ARRAY{array} WHERE id={id}"
            # print(sql)
            result = await db.execute(sql)

    return True

async def favoritesThread(
    favorites: list,
    db: PostgresClient,
):
    """Thread to handle importing favorites

    Args:
        favorites (list): The list of records to import
        db (PostgresClient): A database connection
    """
    data = dict()
    pbar = tqdm(favorites)
    for record in pbar:
        for id, array in record.items():
            sql = f" UPDATE users SET favorite_projects = ARRAY{projects} WHERE id={uid}"
            # print(sql)
            result = await db.execute(f"{sql};")

    return True

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
        # super().__init__('users', dburi)
        super().__init__('users')

    async def fixRoles(self,
                       inpg: PostgresClient,
                       outpg: PostgresClient,
                       ):

        """
        Fix the roles after importing from TM.

        Args:
            inpg (PostgresClient): The input database
            outpg (PostgresClient): The output database
        """
        # For some reason the user role doesn't import
        # correctly, but it barely matters as this is
        # now in the members column of the projects
        # table. But we might as well fix this in the user
        # table. Most are MAPPERS, so set that as the default.
        sql = f"UPDATE users SET role = 'MAPPER'"
        result = await outpg.execute(sql)
        # Get the few users that are a project manager
        sql = f"SELECT json_agg(tmp) FROM (SELECT id,role FROM users WHERE role>0) AS tmp;"
        # print(sql)
        result = await inpg.execute(sql)
        admins = dict()
        for entry in eval(result[0]['json_agg']):
            sql = f"UPDATE users SET role = 'PROJECT_MANAGER' WHERE id={entry['id']}"
            result = await outpg.execute(sql)

    async def mergeInterests(self,
                             inpg: PostgresClient,
                             ):
        """
        Merge the user_interests table from the Tasking Manager

        Args:
            inpg (PostgresClient): The input database
        """
        table = 'user_interests'
        timer = Timer(initial_text="Merging user_interests table...",
                      text="merging liceneses table took {seconds:.0f}s",
                      logger=log.debug,
                    )
        log.info(f"Merging interests table...")
        timer.start()
        sql = "SELECT * FROM user_interests ORDER BY user_id"
        result = await inpg.execute(sql)

        # FIXME: this SQL turns out to be painfully slow, and we can create the array
        # in python faster.
        # await self.copyTable(table, remote)
        # await self.renameTable(table)
        # sql = f"SELECT row_to_json({table}) as row FROM {table}"
        # Not all records in this table have data
        # sql = f"SELECT u.user_id,ARRAY(SELECT ARRAY(SELECT c.interest_id FROM {table} c WHERE c.user_id = u.user_id)) AS user_id FROM {table} u;"
        data = list()
        entry = dict()
        prev = None
        # Restructure the data into a list, so we can more easily chop the data
        # into multiple smaller pieces, one for each thread.
        for record in result:
            if prev == record['user_id']:
                entry[record['user_id']].append(record['interest_id'])
            else:
                if len(entry) != 0:
                    data.append(entry)
                prev = record['user_id']
                entry = {record['user_id']: [record['interest_id']]}
        timer.stop()

        # await remote.pg.close()
        #pg = PostgresClient()
        entries = len(data)
        chunk = round(entries / cores)

        start = 0
        async with asyncio.TaskGroup() as tg:
            for block in range(0, entries, chunk):
                # for index in range(0, cores):
                outpg = PostgresClient()
                await outpg.connect('localhost/tm_admin')
                log.debug(f"Dispatching thread {block}:{block + chunk}")
                # await interestsThread(data, outpg)
                task = tg.create_task(interestsThread(data[block:block + chunk], outpg))
        
        return True

    async def mergeLicenses(self,
                             inpg: PostgresClient,
                             ):
        """
        Merge data from the TM user_licenses table into TM Admin. The
        fastest way to do a bulk update of a table is by copying the
        remote database table into the local database, and then merging
        into a new temporary table and then renaming it.

        Args:
            inpg (PostgresClient): The input database
        """
        table = 'user_licenses'
        # log.info(f"Merging licenses table...")
        timer = Timer(initial_text="Merging user_licenses table...",
                      text="merging user_liceneses table took {seconds:.0f}s",
                      logger=log.debug,
                    )
        timer.start()
        sql = "SELECT * FROM user_licenses ORDER BY user"
        data = await inpg.execute(sql)

        entries = len(data)
        chunk = round(entries / cores)

        start = 0
        async with asyncio.TaskGroup() as tg:
            for block in range(0, entries, chunk):
                # for index in range(0, cores):
                outpg = PostgresClient()
                await outpg.connect('localhost/tm_admin')
                log.debug(f"Dispatching thread {block}:{block + chunk}")
                # await licensesThread(data, outpg)
                task = tg.create_task(licensesThread(data[block:block + chunk], outpg))

        # self.columns = await inpg.getColumns(table)
        # print(f"COLUMNS: {self.columns}")

        # await self.copyTable(table, self.pg)
        # # log.warning(f"Merging tables can take considerable time...")

        # # cleanup old temporary tables
        # drop = ["DROP TABLE IF EXISTS users_bak",
        #         "DROP TABLE IF EXISTS foo"]
        # # result = await pg.pg.executemany(drop)
        # sql = f"DROP TABLE IF EXISTS users_bak"
        # result = await self.pg.execute(sql)
        # sql = f"DROP TABLE IF EXISTS user_licenses"
        # result = await self.pg.execute(sql)
        # sql = f"DROP TABLE IF EXISTS new_users"
        # result = await self.pg.execute(sql)

        # # We need to use DBLINK
        # sql = f"CREATE EXTENSION IF NOT EXISTS dblink;"
        # data = await self.pg.execute(sql)

        # dbuser = self.pg.dburi["dbuser"]
        # dbpass = self.pg.dburi["dbpass"]
        # sql = f"CREATE SERVER IF NOT EXISTS pg_rep_db FOREIGN DATA WRAPPER dblink_fdw  OPTIONS (dbname 'tm4');"
        # data = await self.pg.execute(sql)

        # sql = f"CREATE USER MAPPING IF NOT EXISTS FOR {dbuser} SERVER pg_rep_db OPTIONS ( user '{dbuser}', password '{dbpass}');"
        # result = await self.pg.execute(sql)

        # # Copy table from remote database so JOIN is faster when it's in the
        # # same database
        # log.warning(f"Copying a remote table is slow, but faster than remote access......")
        # # sql = f"SELECT * INTO user_licenses FROM dblink('pg_rep_db','SELECT * FROM user_licenses') AS user_licenses(user_id bigint, license int)"
        # # print(pg.dburi)
        # # print(sql)
        # # result = await pg.execute(sql)

        # # JOINing into a new table is much faster than doing an UPDATE
        # sql = f"SELECT users.*,ARRAY[user_licenses.license] INTO new_users FROM users JOIN user_licenses ON users.id=user_licenses.user_id"
        # result = await self.pg.execute(sql)

        # # self.renameTable(table, pg)
        # # sql = f"ALTER TABLE users RENAME TO users_bak;"
        # # result = await pg.execute(sql)
        # # sql = f"ALTER TABLE new_users RENAME TO users;"
        # # result = await pg.execute(sql)
        # # sql = f"DROP TABLE IF EXISTS user_licenses"
        # # result = await pg.execute(sql)
        timer.stop()

    async def mergeFavorites(self,
                            inpg: PostgresClient,
                            ):
        table = 'project_favorites'
        timer = Timer(initial_text=f"Merging {table} table...",
                      text="merging table took {seconds:.0f}s",
                      logger=log.debug,
                    )
        log.info(f"Merging {table} table...")

        timer.start()
        sql = f"SELECT u.user_id,(SELECT ARRAY(SELECT c.project_id FROM {table} c WHERE c.user_id = u.user_id)) AS projects FROM {table} u;"
        #sql = f"SELECT row_to_json({table}) as row FROM {table} ORDER BY user_id"
        print(sql)
        result = await inpg.execute(sql)

        entries = len(result)
        log.debug(f"There are {entries} entries in {table}")
        chunk = round(entries / cores)
        pbar = tqdm.tqdm(result)

        # This table has a small amount of data, so threading would be overkill.
        for record in pbar:
            uid = record.get('user_id')
            array = record.get('projects')
            sql = f" UPDATE users SET favorite_projects = ARRAY{array} WHERE id={uid}"
            #print(sql)
            result = await self.pg.execute(sql)

        timer.stop()
        return True

    async def mergeAuxTables(self,
                             inuri: str,
                             outuri: str,
                             ):
        """
        Merge more tables from TM into the unified users table.

        Args:
            inuri (str): The input database
            outuri (str): The output database        
        """
        await self.connect(outuri)

        inpg = PostgresClient()
        await inpg.connect(inuri)

        outpg = PostgresClient()
        await outpg.connect(outuri)

        await self.fixRoles(inpg, outpg)

        await self.mergeFavorites(inpg)

        await self.mergeInterests(inpg)

        result = await self.mergeLicenses(inpg)

async def main():
    """This main function lets this class be run standalone by a bash script."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", nargs="?", const="0",
                        help="verbose output")
    parser.add_argument("-i", "--inuri", default='localhost/tm4',
                        help="Input Database URI")
    parser.add_argument("-o", "--outuri", default='localhost/tm_admin',
                        help="Output Database URI")
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

    user = UsersDB()
    # user.connect(args.uri)
    await user.mergeAuxTables(args.inuri, args.outuri)
    
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
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
