#!/usr/bin/python3

# Copyright (c) 2022, 2023, 2024 Humanitarian OpenStreetMap Team
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
import geojson
from cpuinfo import get_cpu_info
from shapely.geometry import shape
from shapely import centroid
from tm_admin.types_tm import Mappingtypes, Projectstatus, Taskcreationmode, Editors, Permissions, Projectpriority, Projectdifficulty, Roles
from tm_admin.projects.projects_class import ProjectsTable
from shapely import wkb, get_coordinates
from tm_admin.dbsupport import DBSupport
from tm_admin.generator import Generator
from osm_rawdata.pgasync import PostgresClient
from tm_admin.access import Roles
import re
# from progress import Bar, PixelBar
from tqdm import tqdm
import tqdm.asyncio
from codetiming import Timer
import asyncio
from tm_admin.yamlfile import YamlFile

# Find the other files for this project
import tm_admin as tma
rootdir = tma.__path__[0]

# The number of threads is based on the CPU cores
info = get_cpu_info()
cores = info["count"] * 2

# Instantiate logger
log = logging.getLogger(__name__)

async def updateThread(
    queries: list,
    db: PostgresClient,
):
    """Thread to handle importing data

    Args:
        queries (list): The list of SQL queries to execute
        db (PostgresClient): A database connection
    """
    pbar = tqdm.tqdm(queries)
    # for sql in queries:
    for sql in pbar:
        # print(sql)
        result = await db.execute(sql)

    return True

class ProjectsDB(DBSupport):
    def __init__(self,
                 dburi: str = "localhost/tm_admin",
                ):
        """
        A class to access the projects table.

        Args:
            dburi (str): The URI string for the database connection

        Returns:
            (ProjectsDB): An instance of this class
        """
        self.pg = None
        self.profile = ProjectsTable()
        self.types = dir(tm_admin.types_tm)
        super().__init__('projects')

    async def mergeInfo(self,
                        inpg: PostgresClient,
                        ):
        table = 'project_info'
        timer = Timer(initial_text=f"Merging {table} table...",
                      text="merging table took {seconds:.0f}s",
                      logger=log.debug,
                    )
        log.info(f"Merging {table} table...")

        timer.start()
        # columns = await inpg.getColumns(table)
        columns = f"project_id, name, short_description, description, instructions, per_task_instructions"

        sql = f"SELECT {columns} FROM {table} ORDER BY project_id"
        # print(sql)
        result = await inpg.execute(sql)

        # pbar = tqdm.tqdm(result)
        queries = list()
        for record in result:
            # in Postgres, to escape a single quote, you use two single quotes. So
            # we have to fix this before encoding it.
            if record['name']:
                name = record['name'].replace("'", "''").encode('utf-8')
            if record['description']:
                description = record['description'].replace("'", "''").encode('utf-8')
            else:
                description = "NULL".encode('utf-8')
            if record['short_description']:
                short = record['short_description'].replace("'", "''").encode('utf-8')
            else:
                short = "NULL".encode('utf-8')
            if record['per_task_instructions']:
                task = record['per_task_instructions'].replace("'", "''").encode('utf-8')
            else:
                task = "NULL".encode('utf-8')
            if record['instructions']:
                instructions = record['instructions'].replace("'", "''").encode('utf-8')
            else:
                instructions = "NULL".encode('utf-8')
            # sql = f"UPDATE projects SET id={record['project_id']}, default_locale='{record['locale']}', name={name},short_description={short},description={description},instructions={instructions},per_task_instructions={task} WHERE id={record['project_id']};"
            sql = f"UPDATE projects SET name='{name.decode('utf-8')}', short_description='{short.decode('utf-8')}', description='{description.decode('utf-8')}', instructions='{instructions.decode('utf-8')}' WHERE id={record['project_id']};"
            # await self.pg.execute(sql)
            queries.append(sql)

        entries = len(queries)
        chunk = round(entries / cores)

        #pbar = tqdm.tqdm(queries)
        # FIXME: It'd be nice if we could have a progress meter that works with range
        log.warning(f"This makes take time, so please wait...")
        async with asyncio.TaskGroup() as tg:
            for block in range(0, entries, chunk):
                outpg = PostgresClient()
                await outpg.connect('localhost/tm_admin')
                # log.debug(f"Dispatching thread {block}:{block + chunk}")
                # await updateThread(queries, outpg)
                task = tg.create_task(updateThread(queries[block:block + chunk], outpg))
        timer.stop()
        return True

    async def mergeInterests(self,
                        inpg: PostgresClient,
                        ):
        table = "project_interests"
        timer = Timer(initial_text=f"Merging {table} table...",
                      text="merging table took {seconds:.0f}s",
                      logger=log.debug,
                    )
        log.info(f"Merging {table} table...")
        timer.start()
        sql = f"SELECT * FROM {table} ORDER BY project_id"
        # print(sql)
        result = await inpg.execute(sql)

        entries = len(result)
        log.debug(f"There are {entries} entries in {table}")
        chunk = round(entries / cores)
        # pbar = tqdm.tqdm(result)

        queries = list()
        for record in result:
            pid = record.get('project_id')
            sql = f" UPDATE projects SET interests = {record['interest_id']} WHERE id={pid}"
            #print(sql)
            queries.append(sql)
            #result = await self.pg.execute(sql)

        entries = len(queries)
        chunk = round(entries / cores)

        #pbar = tqdm.tqdm(queries)
        # FIXME: It'd be nice if we could have a progress meter that works with range
        log.warning(f"This makes take time, so please wait...")
        async with asyncio.TaskGroup() as tg:
            for block in range(0, entries, chunk):
                outpg = PostgresClient()
                await outpg.connect('localhost/tm_admin')
                # log.debug(f"Dispatching thread {block}:{block + chunk}")
                # await updateThread(queries, outpg)
                task = tg.create_task(updateThread(queries[block:block + chunk], outpg))

        timer.stop()
        return True

    async def mergeAuxTables(self,
                             inuri: str,
                             outuri: str,
                             ):
        """
        Merge more tables from TM into the unified projects table.

        Args:
            inuri (str): The input database
            outuri (str): The output database
        """
        await self.connect(outuri)

        inpg = PostgresClient()
        await inpg.connect(inuri)

        await self.mergeAllowed(inpg)

        await self.mergeTeams(inpg)

        await self.mergeInfo(inpg)

        await self.mergeChat(inpg)

        await self.mergeInterests(inpg)

        await self.mergePriorities(inpg)

        # The project favorites table is imported into the users table instead.
        # await self.mergeFavorites(inpg)

    async def mergeChat(self,
                        inpg: PostgresClient,
                        ):
        table = "project_chat"
        timer = Timer(initial_text=f"Merging {table} table...",
                      text="merging table took {seconds:.0f}s",
                      logger=log.debug,
                    )
        log.info(f"Merging {table} table...")
        timer.start()
        sql = f"SELECT * FROM project_chat ORDER BY project_id"
        # print(sql)
        result = await inpg.execute(sql)
        data = dict()
        queries = list()
        for record in tqdm.tqdm(result):
            # The messages has embedded quotes.
            message = record['message'].replace("'", "&apos;")
            sql = f" INSERT INTO chat(id, project_id, user_id, time_stamp, message) VALUES({record['id']}, {record['project_id']}, {record['user_id']}, '{record['time_stamp']}', '{message}')"
            # print(sql)
            queries.append(sql)
            #result = await self.pg.execute(sql)

        entries = len(queries)
        chunk = round(entries / cores)

        #pbar = tqdm.tqdm(queries)
        # FIXME: It'd be nice if we could have a progress meter that works with range
        log.warning(f"This makes take time, so please wait...")
        async with asyncio.TaskGroup() as tg:
            for block in tqdm.tqdm(range(0, entries, chunk)):
                outpg = PostgresClient()
                await outpg.connect('localhost/tm_admin')
                # log.debug(f"Dispatching thread {block}:{block + chunk}")
                # await updateThread(queries, outpg)
                task = tg.create_task(updateThread(queries[block:block + chunk], outpg))

        timer.stop()
        return True

    async def mergeTeams(self,
                        inpg: PostgresClient,
                        ):
        table = "project_teams"
        log.error(f"mergeTeams() Unimplemented!")
        timer = Timer(initial_text=f"Merging {table} table...",
                      text="merging table took {seconds:.0f}s",
                      logger=log.debug,
                    )
        log.info(f"Merging {table} table...")
        timer.start()
        sql = f"SELECT * FROM {table} ORDER BY project_id"
        # print(sql)
        result = await inpg.execute(sql)

        entries = len(result)
        log.debug(f"There are {entries} entries in {table}")
        chunk = round(entries / cores)
        # pbar = tqdm.tqdm(result)

        # yaml = YamlFile(f"{rootdir}/projects/projects_teams.yaml")
        # for variable in yaml.yaml[0]['project_teams']:
        #     for k, v in variable.items():
        #         # It's one of our Enums used in a jsonb column
        #         if v[:7] == "public.":

        # postgres could return this as an array, but we'd still have to process it
        # to create the SQL query, instead we build an array of teams for each
        # project, which becomes a nice clean way to add an array.
        teams = dict()
        for record in result:
            if record['role'] < 0:
                role = Roles(Roles.READ_ONLY)
            else:
                if record['role'] == 0:
                    role = Roles(Roles.READ_ONLY)
                elif record['role'] == 1:
                    role = Roles(Roles.VALIDATOR)
                elif record['role'] == 2:
                    role = Roles(Roles.PROJECT_MANAGER)
            if record['project_id'] not in teams:
                teams[record['project_id']] = [{"role": role.name,
                                            "team_id": record['team_id']}]
            else:
                teams[record['project_id']].append({"role": role.name,
                                        "team_id": record['team_id']})
        queries = list()
        for project, members in teams.items():
            # Sometimes the role wasn't set
            try:
                role = Roles(record['role'])
            except:
                role = Roles(1)

            # sql = "UPDATE projects SET teams=teams||'{\"team_id\": %s, \"role\": %s}' WHERE id=%d" % (record['team_id'], role, pid)
            # Note that this will replace any existing values for this column
            asc = str(members).replace("'", '"').replace("\\'", "'")
            sql = "UPDATE projects SET members = '{\"teams\": %s}' WHERE id=%d;" % (asc, project)
            # print(sql)
            queries.append(sql)
            #result = await self.pg.execute(sql)

        entries = len(queries)
        chunk = round(entries / cores)
        #pbar = tqdm.tqdm(queries)
        # FIXME: It'd be nice if we could have a progress meter that works with range
        log.warning(f"This makes take time, so please wait...")
        async with asyncio.TaskGroup() as tg:
            for block in range(0, entries, chunk):
                outpg = PostgresClient()
                await outpg.connect('localhost/tm_admin')
                # log.debug(f"Dispatching thread {block}:{block + chunk}")
                # await updateThread(queries, outpg)
                task = tg.create_task(updateThread(queries[block:block + chunk], outpg))

        timer.stop()
        return True

    # This tables turns out to not be used anymore, this is supported
    # by teams.
    async def mergeAllowed(self,
                        inpg: PostgresClient,
                        ):
        table = "project_allowed_users"
        timer = Timer(initial_text=f"Merging {table} table...",
                      text="merging table took {seconds:.0f}s",
                      logger=log.debug,
                    )
        log.info(f"Merging {table} table...")
        timer.start()
        # Get all the users that are managers or admins. Luckily this
        # has very few results
        sql = f"SELECT json_agg(tmp) FROM (SELECT id,role FROM users WHERE role>0) AS tmp;"
        # print(sql)
        result = await inpg.execute(sql)
        admins = dict()
        for entry in eval(result[0]['json_agg']):
            admins[entry['id']] = Roles(Roles.PROJECT_MANAGER)
        # It's faster to do this in Python than postgres
        # sql = f"SELECT u.user_id,(SELECT ARRAY(SELECT c.project_id FROM {table} c WHERE c.user_id = u.user_id)) AS projects FROM {table} u;"
        sql = f"SELECT * FROM project_allowed_users ORDER BY project_id"
        # print(sql)
        result = await inpg.execute(sql)
        data = dict()
        for record in result:
            if not record['project_id'] in data:
                entry = list()
                data[record['project_id']] = entry
                if record['user_id'] in admins:
                    role = admins[record['user_id']]
                else:
                    role = Roles(Roles.MAPPER)
                entry.append({"user_id": record['user_id'],
                              "role": role.name})

        entries = len(result)
        log.debug(f"There are {entries} entries in {table}, and {len(data)} in the array")
        chunk = round(entries / cores)
        # This table has a small amount of data, so threading would be overkill.
        # for record in pbar:
        for pid, array in tqdm.tqdm(data.items()):
            # user = {"user_id": }
            #sql = f" UPDATE projects SET allowed_users = ARRAY{array} WHERE id={pid}"
            asc = str(entry).replace("'", '"').replace("\\'", "'")
            sql = "UPDATE projects SET members = '{\"users\": %s}' WHERE id=%d;" % (asc, pid)

            # print(sql)
            result = await self.pg.execute(sql)

        timer.stop()
        return True

    async def mergePriorities(self,
                        inpg: PostgresClient,
                        ):
        table = "project_priority_areas"
        timer = Timer(initial_text=f"Merging {table} table...",
                      text="merging table took {seconds:.0f}s",
                      logger=log.debug,
                    )
        log.info(f"Merging {table} table...")
        timer.start()
        # It's faster to do this in Python than postgres
        # sql = f"SELECT u.user_id,(SELECT ARRAY(SELECT c.project_id FROM {table} c WHERE c.user_id = u.user_id)) AS projects FROM {table} u;"
        sql = f"SELECT * FROM {table} ORDER BY project_id"
        # print(sql)
        result = await inpg.execute(sql)
        data = dict()
        for record in result:
            if not record['project_id'] in data:
                entry = list()
                data[record['project_id']] = entry
            entry.append(record['priority_area_id'])

        entries = len(result)
        log.debug(f"There are {entries} entries in {table}, and {len(data)} in the array")
        chunk = round(entries / cores)
        # This table has a small amount of data, so threading would be overkill.
        # for record in pbar:
        for pid, array in tqdm.tqdm(data.items()):
            sql = f" UPDATE projects SET priority_areas = ARRAY{array} WHERE id={pid}"
            # print(sql)
            result = await self.pg.execute(sql)

        timer.stop()
        return True

async def main():
    """This main function lets this class be run standalone by a bash script."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", nargs="?", const="0", help="verbose output")
    parser.add_argument("-i", "--inuri", default='localhost/tm4',
                            help="Database URI")
    parser.add_argument("-o", "--outuri", default='localhost/tm_admin',
                            help="Database URI")
    parser.add_argument("-b", "--boundary", help="The project AOI")

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

    proj = ProjectsDB(args.outuri)
    # user.resetSequence()
    #all = proj.getAll()

    timer = Timer(initial_text=f"Merging all other tables...",
                      text="Importing took {seconds:.0f}s",
                      logger=log.debug,
                    )
    timer.start()
    await proj.mergeAuxTables(args.inuri, args.outuri)
    timer.stop()

    # file = open(args.boundary, 'r')
    # boundary = geojson.load(file)
    # geom = shape(boundary[0]['geometry'])
    # center = centroid(geom)

    # Don't pass id, let postgres auto increment
    # ut = ProjectsTable(author_id=1, outline=geom, centroid=center,
    #                    created='2021-12-15 09:58:02.672236',
    #                    task_creation_mode='GRID', status='DRAFT',
    #                    mapping_level='BEGINNER')
    # proj.createTable(ut)
    # print(all)

    #all = proj.getByID(1)
    #print(all)
            
    # all = proj.getByName('fixme')
    # print(all)
            

if __name__ == "__main__":
    """This is just a hook so this file can be run standalone during development."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
