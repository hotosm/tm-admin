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
    pbar = tqdm.tqdm(queries)
    for sql in pbar:
    # for sql in queries:
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

    async def mergeAnnotations(self,
                        inpg: PostgresClient,
                        ):
        """
        Merge the task_annotation table from Tasking Manager into
        TM Admin. This table doesn't actually appear to be currently
        used by TM at all.
        """
        table = "task_annotations"
        log.error(f"mergeAnnotations() Unimplemented as the source is empty!")
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

        await self.mergeHistory(inpg)

        await self.mergeInvalidations(inpg)

        # This is now handled by mergeHistory
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
                        text="merging table took {seconds:.0f}s",
                        logger=log.debug,
                    )
        log.info(f"Merging {table} table...")
        timer.start()

        # There is a small amount of data in this table, and we need to
        # coorelate it to the task history when merging, so read in
        # the entire dataset.
        sql = f"SELECT * FROM task_mapping_issues ORDER BY id;"
        # print(sql)
        data = await inpg.execute(sql)
        entries = len(data)
        log.debug(f"There are {len(data)} records in task_mapping_issues")
        issues = dict()
        # pbar = tqdm.tqdm(data)
        # for record in pbar:
        for record in data:
            hid = record['task_history_id']
            issues[hid] = {'issue': record['issue'],
                           'category': record['mapping_issue_category_id'],
                           'count': record['count'],
                           }

        # Now get the data from the history table
        sql = f"SELECT * FROM {table}"
        # print(sql)
        data = await inpg.execute(sql)
        entries = len(data)
        log.debug(f"There are {len(data)} records in {table}")

        chunk = round(entries/cores)

        # FIXME: create an array of SQL queries, so later we can use
        # prepared_queries in asyncpg for better performance. We also don't
        # need all of the columns from the TM table, since task ID and
        # project ID are already part of the table schema.
        queries = list()
        # pbar = tqdm.tqdm(data)
        #for record in pbar:
        for record in data:
            entry = {"user_id": record['user_id']}
            # entry['action'] = Taskaction(record['action']).name
            entry['action'] = record['action']
            # The action_text column often has issues with embedded
            # quotes.
            if record['action_text']:
                fix = record['action_text'].replace('"', '&quot;')
            entry['action_text'] = fix.replace("'", '&apos;').replace("\xa0", "")
            if record['action_date']:
                entry['action_date'] = '{:%Y-%m-%dT%H:%M:%S}'.format(record['action_date'])
            # If there is an issue, add it to the record in the jsonb column
            if record['id'] in issues:
                entry.update(issues[record['id']])
                entry.update(issues[record['id']])
                # entry['issue'] = issues['issue']
                # entry['category'] = issues['category']
                # entry['count'] = issues['count']
            asc = str(entry).replace("'", '"').replace("\\'", "'")
            sql = "UPDATE tasks SET history = '{\"history\": [%s]}' WHERE id=%d AND project_id=%d" % (asc, record['task_id'], record['project_id'])
            # print(sql)
            queries.append(sql)

            # Add a timestamp to the created column so this table can
            # be partitioned.
            sql = f"UPDATE tasks SET created = '{entry['action_date']}' WHERE id={record['task_id']} AND project_id={record['project_id']}"
            # print(sql)
            queries.append(sql)

        entries = len(queries)
        chunk = round(entries/cores)
        import copy
        async with asyncio.TaskGroup() as tg:
            for block in range(0, entries, chunk):
                # for index in range(0, cores):
                outpg = PostgresClient()
                # FIXME: this should not be hard coded
                await outpg.connect('localhost/tm_admin')
                # FIXME: this may be removed after testing, but memory
                # corruption errors fored this workaround.
                foo = copy.copy(queries[block:block + chunk -1])
                log.debug(f"Dispatching thread {block}:{block + chunk - 1}")
#                await updateThread(foo, outpg)
                # await updateThread(queries[block:block + chunk], outpg)
                task = tg.create_task(updateThread(foo, outpg))
        timer.stop()

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
            sql = "UPDATE tasks SET invalidation_history = '{\"history\": [%s]}' WHERE id=%d AND project_id=%d" % (asc, record['task_id'], record['project_id'])
            # print(sql)
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
                task = tg.create_task(updateThread(queries[block:block + chunk], outpg))

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
