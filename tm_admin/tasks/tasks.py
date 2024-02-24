#!/usr/bin/python3

# Copyright (c) 2023, 2024 Humanitarian OpenStreetMap Team
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

# Humanitarian OpenStreetmap Task
# 1100 13th Street NW Suite 800 Washington, D.C. 20005
# <info@hotosm.org>

import argparse
import logging
import sys
import os
from sys import argv
from datetime import datetime
from dateutil.parser import parse
import concurrent.futures
from tm_admin.types_tm import Taskaction
from tm_admin.dbsupport import DBSupport
from tm_admin.tasks.tasks_class import TasksTable
from tm_admin.tasks.task_history_class import Task_historyTable
from tm_admin.tasks.task_invalidation_history_class import Task_invalidation_historyTable
from osm_rawdata.pgasync import PostgresClient
from tqdm import tqdm
from codetiming import Timer
import threading
from cpuinfo import get_cpu_info
import psycopg2.extensions
from dateutil.parser import parse
import time
from tqdm import tqdm
import tqdm.asyncio
import asyncio
from codetiming import Timer

# Instantiate logger
log = logging.getLogger(__name__)

# The number of threads is based on the CPU cores
info = get_cpu_info()
cores = info["count"] * 2

async def updateThread(
    queries: list,
    db: PostgresClient,
):
    """Thread to handle importing data

    Args:
        queries (list): The list of SQL queries to execute
        db (PostgresClient): A database connection
    """
    # pbar = tqdm.tqdm(queries)
    # for sql in queries:
    # for sql in pbar:
    print(sql)
    result = await db.execute(sql)

    return True

async def historyThread(
    data: list,
    db: PostgresClient,
    table: str = "tasks",
):
    """Thread to handle importing

    Args:
        data (list): The list of records to import
        db (PostgresClient): A database connection
        table (str): The table to update
    """
    # pbar = tqdm(data)
    for entry in data:
        # there is only one entry if using row_to_json()
        id = entry['id']
        uid = entry['user_id']
        pid = entry['project_id']
        tid = entry['task_id']
        action = entry['action']
        date = entry['action_date']
        # Remove embedded single quotes
        text = str()
        if entry['action_text'] is None:
            text = "NULL"
        else:
            text = entry['action_text'].replace("'", "")
        timestamp = str(entry['action_date'])
        # timestamp = "{%Y-%m-%dT%H:%M:%S}".format(date)
        # timestamp = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%f")
        # entry['action_date'] = timestamp
        # FIXME: currently the schema has this as an int, it's actully an enum
        func = eval(f"Taskaction.{action}")
        # columns = f"id, project_id, history.action, history.action_text, history.action_date, history.user_id"
        # nested = f"{record['id']}, {record['project_id']}, {func.value}, '{text}', '{timestamp}', {record['user_id']}"
        sql = f"UPDATE tasks "
        sql += f" SET history=history||({pid}, {tid}, {func.value}, '{text}', '{timestamp}', {uid})::task_history"
        # sql += f" SET history = (SELECT ARRAY_APPEND(history,({func.value}, '{text}', '{timestamp}', {entry['user_id']})::task_history)) "
        sql += f" WHERE id={entry['task_id']} AND project_id={entry['project_id']}"
        print(f"{sql};")
        #try:
        result = db.execute(sql)
        #except:
        #    log.error(f"Couldn't execute query! '{sql}'")

    return True

async def invalidationThread(
    data: list,
    db: PostgresClient,
):
    """Thread to handle importing

    Args:
        data (list): The list of records to import
        db (PostgresClient): A database connection
    """
    pbar = tqdm.tqdm(data)
    for record in pbar:
        map_timestamp = "NULL"
        inval_timestamp = "NULL"
        up_timestamp = "NULL"
        val_timestamp = "NULL"
        date = record['mapped_date']
        if date is not None:
            map_timestamp = "'{:%Y-%m-%dT%H:%M:%S}'".format(date)
        date = record['invalidated_date']
        if date is not None:
            inval_timestamp = "'{:%Y-%m-%dT%H:%M:%S}'".format(date)
        date = record['updated_date']
        if date is not None:
            up_timestamp = "'{:%Y-%m-%dT%H:%M:%S}'".format(date)
        date = record['validated_date']
        if date is not None:
            val_timestamp = "'{:%Y-%m-%dT%H:%M:%S}'".format(date)

        vid = "NULL"
        if record['validator_id'] is not None:
            vid = record['validator_id']

        # columns = f"is_closed, mapper_id, mapped_date, invalidator_id, invalidated_date, invalidation_history_id, validator_id, validated_date, updated_date"

        sql = f"UPDATE tasks"
        # sql += f"  SET invalidation_history = (SELECT ARRAY_APPEND(invalidation_history,({record['is_closed']}, {record['mapper_id']}, {map_timestamp}, {record['invalidator_id']}, {inval_timestamp}, {record['invalidation_history_id']}, {vid}, {val_timestamp}, {up_timestamp})::task_invalidation_history)) "
        sql += f"  SET invalidation_history = invalidation_history||({record['is_closed']}, {record['mapper_id']}, '{record['mapped_date']}', {record['invalidator_id']}, '{record['invalidated_date']}', {record['invalidation_history_id']}, {record['validator_id']}, '{record['validated_date']}', '{record['updated_date']}')::task_invalidation_history"
        sql += f"WHERE id={record['task_id']} AND project_id={record['project_id']}"
        # print(sql)
        result = await db.execute(sql)

    return True

class TasksDB(DBSupport):
    def __init__(self,
                dburi: str = "localhost/tm_admin",
                ):
        """
        A class to access the tasks table.

        Args:
            dburi (str): The URI string for the database connection.

        Returns:
            (TasksDB): An instance of this class.
        """
        self.profile = TasksTable()
        super().__init__('tasks')

    async def mergeIssues(self,
                        inpg: PostgresClient,
                        ):
        table = "task_mapping_issues"
        log.error(f"mergeIssues() Unimplemented!")
        timer = Timer(initial_text=f"Merging {table} table...",
                      text="merging table took {seconds:.0f}s",
                      logger=log.debug,
                    )
        log.info(f"Merging {table} table...")

    async def mergeAnnotations(self,
                        inpg: PostgresClient,
                        ):
        table = "task_annotationstask_annotations"
        log.error(f"mergeAnnotations() nimplemented!")
        timer = Timer(initial_text="Merging {table} table...",
                      text="merging {table table took {seconds:.0f}s",
                      logger=log.debug,
                    )
        log.info(f"Merging {table} table...")

    async def mergeAuxTables(self,
                             inuri: str,
                             outuri: str,
                             ):
        """
        Merge more tables from TM into the unified tasks table.

        Args:
            inuri (str): The input database
            outuri (str): The output database
        """
        await self.connect(outuri)

        inpg = PostgresClient()
        await inpg.connect(inuri)

        # FIXME: in TM, this table is empty
        # await self.mergeAnnotations(inpg)

        # await self.mergeHistory(inpg)

        await self.mergeInvalidations(inpg)

        # await self.mergeIssues(inpg)

    async def mergeHistory(self,
                        inpg: PostgresClient,
                        ):
        """
        A method to merge the contents of the TM campaign_projects into
        the campaigns table as an array.
        """
        table = 'task_history'
        timer = Timer(initial_text=f"Merging {table} table...",
                        # text=f"merging {table} table took {seconds:.0f}s",
                      logger=log.debug,
                    )
        log.info(f"Merging {table} table...")
        # pg = PostgresClient()
        # await pg.connect('localhost/tm4')
        # sql = f"SELECT MIN(project_id),MAX(project_id) FROM task_history"
        # Get the number of records
        # sql = f"SELECT reltuples::bigint AS estimate FROM  pg_class WHERE oid = 'public.task_history'::regclass;"
        # entries = await pg.getRecordCount(table)

        sql = f"SELECT * FROM {table}"
        # print(sql)
        timer.start()
        data = await inpg.execute(sql)
        entries = len(data)
        log.debug(f"There are {len(data)} records in {table}")
        timer.stop()

        chunk = round(entries/cores)
        blocks = list()
        # Some tables in the input database are huge, and can either core
        # dump python, or have performance issues. Past a certain threshold
        # the data needs to be queried in pages instead of the entire table
        # This is a huge table, we can't read in the entire thing

        async with asyncio.TaskGroup() as tg:
            for block in range(0, entries, chunk):
                # for index in range(0, cores):
                outpg = PostgresClient()
                await outpg.connect('localhost/tm_admin')
                log.debug(f"Dispatching thread {block}:{block + chunk}")
                # await licensesThread(data, outpg)
                await historyThread(data[block:block + chunk], outpg)
                # task = tg.create_task(historyThread(data[block:block + chunk], outpg))

        # result = historyThread(data, adminpg[index], f"{table}{index}_view")

    async def mergeInvalidations(self,
                        inpg: PostgresClient,
                        ):
        """
        A method to merge the contents of the TM campaign_projects into
        the campaigns table as an array.
        """
        table = 'task_invalidation_history'
        timer = Timer(initial_text=f"Merging {table} table...",
                        text="merging table took {seconds:.0f}s",
                        logger=log.debug,
                    )
        log.info(f"Merging {table} table...")

        sql = f"SELECT * FROM {table} ORDER BY project_id"
        # print(sql)
        timer.start()
        data = await inpg.execute(sql)
        entries = len(data)
        log.debug(f"There are {entries} records in {table}")

        # FIXME: create an array of SQL queries, so later we can use
        # prepared_queries in asyncpg for better performance.
        queries = list()
        for record in data:
            tid = record['task_id']
            entry = {"mapper_id": record['mapper_id']}
            if record['invalidator_id']:
                entry['invalidator_id'] = record['invalidator_id']
            else:
                entry['invalidator_id'] = 0
            if record['validator_id']:
                entry['validator_id'] = record['validator_id']
            else:
                entry['validator_id'] = 0
            if record['mapped_date']:
                entry['mapped_date'] = '{:%Y-%m-%dT%H:%M:%S}'.format(record['mapped_date'])
            if record['invalidated_date']:
                entry['mapped_date'] = '{:%Y-%m-%dT%H:%M:%S}'.format(record['invalidated_date'])
            if record['validated_date']:
                entry['mapped_date'] = '{:%Y-%m-%dT%H:%M:%S}'.format(record['validated_date'])
            if record['updated_date']:
                entry['mapped_date'] = '{:%Y-%m-%dT%H:%M:%S}'.format(record['updated_date'])
            if record['is_closed']:
                entry["is_closed_id"] = "true"
            else:
                entry["is_closed_id"] = "false"
            # entries[record['task_id']].append(entry)
            asc = str(entry).replace("'", '"').replace("\\'", "'")
            # UPDATE tasks SET invalidation_history = '{"history": [{"user_id": 35, "mapper_id": 11593853, "invalidator_id": 11596055}]}' WHERE id=35 AND project_id=105;
            sql = "UPDATE tasks SET invalidation_history = '{\"history\": [%s]}' WHERE id=%d AND project_id=%d" % (asc, record['task_id'], record['project_id'])
            print(sql)
            queries.append(sql)

        entries = len(queries)
        chunk = round(entries / cores)
        async with asyncio.TaskGroup() as tg:
            for block in range(0, entries, chunk):
                # for index in range(0, cores):
                outpg = PostgresClient()
                # FIXME: this should not be hard coded
                await outpg.connect('localhost/tm_admin')
                log.debug(f"Dispatching thread {block}:{block + chunk}")
                #await updateThread(queries[block:block + chunk], outpg)
                task = tg.create_task(updateThread(data[block:block + chunk], outpg))

async def main():
    """This main function lets this class be run standalone by a bash script."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", nargs="?", const="0", help="verbose output")
    parser.add_argument("-i", "--inuri", default='localhost/tm4',
                            help="Database URI")
    parser.add_argument("-o", "--outuri", default='localhost/tm_admin',
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

    tasks = TasksDB(args.inuri)
    await tasks.mergeAuxTables(args.inuri, args.outuri)

    # # user.resetSequence()
    # all = task.getAll()
    # # Don't pass id, let postgres auto increment
    # ut = TasksTable(project_id=1)
    # task.createTable(ut)
    # # print(all)

    # all = task.getByID(1)
    # print(all)
            
    # all = task.getByName('test')
    # print(all)

    #ut = TasksTable(name='foobar', organisation_id=1, visibility='PUBLIC')
    # This is obviously only for manual testing
    #user.updateTask(ut, 17)

if __name__ == "__main__":
    """This is just a hook so this file can be run standalone during development."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
