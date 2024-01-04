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
from atpbar import atpbar
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

def licensesThread(
    data: list,
    db: PostgresClient,
):
    """Thread to handle importing

    Args:
        data (list): The list of records to import
        db (PostgresClient): A database connection
    """
    array = "licenses"
    column = "license"

    pbar = tqdm(data)
    for record in pbar:
        uid = record[0]['user']
        licenses = record[0]['license']
        # sql = f" UPDATE users SET licenses = licenses||{licenses} WHERE id={uid}"
        sql = f" UPDATE users SET licenses = ARRAY[{licenses}] WHERE id={uid}"
        #print(sql)
        try:
            result = db.dbcursor.execute(f"{sql};")
        except:
            log.error(f"Couldn't execute query {sql}")

    return True

def interestsThread(
    interests: list,
    db: PostgresClient,
):
    """Thread to handle importing

    Args:
        data (list): The list of records to import
        db (PostgresClient): A database connection
    """
    data = dict()
    pbar = tqdm(interests)
    for record in pbar:
        uid = record[0]['user_id']
        interests = record[0]['interest_id']
        sql = f" UPDATE users SET interests = interests||{interests} WHERE id={uid}"
        # print(sql)
        try:
            result = db.dbcursor.execute(f"{sql};")
        except:
            log.error(f"Couldn't execute query {sql}")
    return True

def favoritesThread(
    favorites: list,
    db: PostgresClient,
):
    """Thread to handle importing favorites

    Args:
        data (list): The list of records to import
        db (PostgresClient): A database connection
    """
    data = dict()
    pbar = tqdm(favorites)
    for record in pbar:
        uid = record[0]
        projects = record[1][0]
        sql = f" UPDATE users SET favorite_projects = ARRAY{projects} WHERE id={uid}"
        # print(sql)
        try:
            result = db.dbcursor.execute(f"{sql};")
        except:
            log.error(f"Couldn't execute query {sql}")

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
        super().__init__('users', dburi)

    def mergeInterests(self):
        table = 'user_interests'
        log.info(f"Merging interests table...")
        # One database connection per thread
        tmpg = list()
        for i in range(0, cores + 1):
            # FIXME: this shouldn't be hardcoded
            tmpg.append(PostgresClient('localhost/tm_admin'))
        pg = PostgresClient('localhost/tm4')
        sql = f"SELECT row_to_json({table}) as row FROM {table}"
        # sql = f"SELECT u.user_id,ARRAY(SELECT ARRAY(SELECT c.interest_id FROM {table} c WHERE c.user_id = u.user_id)) AS user_id FROM {table} u;"
        print(sql)
        try:
            result = pg.dbcursor.execute(sql)
        except:
            log.error(f"Couldn't execute query! {sql}")
            return False

        result = pg.dbcursor.fetchall()

        entries = len(result)
        log.debug(f"There are {entries} entries in {table}")
        chunk = round(entries / cores)


        index = 0
        with concurrent.futures.ThreadPoolExecutor(max_workers=cores) as executor:
            # futures = list()
            block = 0
            while block <= entries:
                #log.debug(f"Dispatching Block %d:%d" % (block, block + chunk))
                #interestsThread(result, tmpg[0])
                executor.submit(interestsThread, result[block : block + chunk], tmpg[index])
                # futures.append(result)
                block += chunk
                index += 1
                # tqdm(futures, desc=f"Dispatching Block {block}:{block + chunk}", total=chunk):
            #     future.result()
            executor.shutdown()

        # timer.stop
        return True

    def getPage(self,
                offset: int,
                count: int,
                pg: PostgresClient,
                table: str,
                ):
        """
        Return a page of data from the table.

        Args:
            offset (int): The starting record
            count (int): The number of records
            pg (PostgresClient): Database connection for the input data
            table (str): The table to query for data

        Returns:
            (list): The results of the query
        """
        # It turns out to be much faster to use the columns specified in the
        # SELECT statement, and construct our own dictionary than using row_to_json().
        #columns = "user_licenses.user, license"

        sql = f"SELECT row_to_json({table}) as row FROM {table} ORDER BY user LIMIT {count} OFFSET {offset}"
        # sql = f"SELECT {columns} FROM {table} ORDER BY user LIMIT {count} OFFSET {offset}"
        print(sql)
        pg.dbcursor.execute(sql)
        result = pg.dbcursor.fetchall()
        # data = list()
        # Since we're not using row_to_json(), build a data structure
        # for record in result:
        #     table = dict(zip(columns, record))
        #     data.append(table)

        return result

    def mergeLicenses(self):
        """Merge data from the TM user_licenses table into TM Admin."""
        table = 'user_licenses'
        # log.info(f"Merging licenses table...")
        timer = Timer(initial_text="Merging licenses table...",
                      text="merging liceneses table took {seconds:.0f}s",
                      logger=log.debug,
                    )
        timer.start()

        sql = f"SELECT row_to_json({table}) as row FROM {table}"
        # One database connection per thread
        adminpg = list()
        for i in range(0, cores + 1):
            adminpg.append(PostgresClient('localhost/tm_admin'))

        # just one thread to read the data
        tmpg = PostgresClient('localhost/tm4')
        try:
            result = tmpg.dbcursor.execute(sql)
        except:
            log.error(f"Couldn't execute query! {sql}")

        data = tmpg.dbcursor.fetchall()
        entries = len(data)
        log.debug(f"There are {entries} entries in {table}")
        chunk = round(entries / cores)

        index = 0
        with concurrent.futures.ThreadPoolExecutor(max_workers=cores) as executor:
            index = 0
            for block in range(0, entries, chunk):
                data = self.getPage(block, chunk, tmpg, table)
                #result = licensesThread(data, adminpg[0])
                result = executor.submit(licensesThread, data, adminpg[index])
                index += 1
            executor.shutdown()

        timer.stop
        return True

    def mergeTeam(self):
        table = 'team_members'
        # FIXME: this shouldn't be hardcoded!
        log.info(f"Merging team members table...")
        timer = Timer(text="merging team members table took {seconds:.0f}s")
        timer.start()
        pg = PostgresClient('localhost/tm4')
        sql = f"SELECT row_to_json({table}) as row FROM {table}"
        #print(sql)
        try:
            result = pg.dbcursor.execute(sql)
        except:
            log.error(f"Couldn't execute query! {sql}")

        result = pg.dbcursor.fetchall()
        pbar = tqdm(result)
        for record in pbar:
            func = record[0]['function']
            tmfunc = Teammemberfunctions(func)
            sql = f"UPDATE {self.table} SET team_members.team={record[0]['team_id']}, team_members.active={record[0]['active']}, team_members.function='{tmfunc.name}' WHERE id={record[0]['user_id']}"
            # print(f"{sql};")
            try:
                result = self.pg.dbcursor.execute(sql)
            except:
                log.error(f"Couldn't execute query! '{sql}'")

        timer.stop()
        return True

    def mergeFavorites(self):
        table = 'project_favorites'
        log.info(f"Merging favorites table...")
        # FIXME: this shouldn't be hardcoded!
        timer = Timer(text="merging favorites table took {seconds:.0f}s")
        timer.start()
        pg = PostgresClient('localhost/tm4')
        sql = f"SELECT u.user_id,ARRAY(SELECT ARRAY(SELECT c.project_id FROM {table} c WHERE c.user_id = u.user_id)) AS user_id FROM {table} u;"
        #sql = f"SELECT row_to_json({table}) as row FROM {table} ORDER BY user_id"
        # print(sql)
        try:
            result = pg.dbcursor.execute(sql)
        except:
            log.error(f"Couldn't execute query! {sql}")

        result = pg.dbcursor.fetchall()

        entries = len(result)
        log.debug(f"There are {entries} entries in {table}")
        chunk = round(entries / cores)

        tmpg = list()
        for i in range(0, cores + 1):
            # FIXME: this shouldn't be hardcoded
            tmpg.append(PostgresClient('localhost/tm_admin'))

        index = 0
        with concurrent.futures.ThreadPoolExecutor(max_workers=cores) as executor:
            # futures = list()
            block = 0
            while block <= entries:
                #log.debug(f"Dispatching Block %d:%d" % (block, block + chunk))
                #favoritesThread(result, tmpg[0])
                executor.submit(favoritesThread, result[block : block + chunk], tmpg[index])
                # futures.append(result)
                block += chunk
                index += 1
            executor.shutdown()

        timer.stop()
        return True

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

    def mergeAuxTables(self):
        """
        Merge more tables from TM into the unified users table.
        """
        # if self.mergeTeam():
        #     log.info("UserDB.mergeTeams worked!")

        # if self.mergeFavorites():
        #     log.info("UserDB.mergeFavorites worked!")

        # These may take a long time to complete
        #if self.mergeInterests():
        #    log.info("UserDB.mergeInterests worked!")

        if self.mergeLicenses():
            log.info("UserDB.mergeLicenses worked!")

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
    user.mergeAuxTables()
    
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
