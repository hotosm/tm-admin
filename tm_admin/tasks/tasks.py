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
from osm_rawdata.postgres import uriParser, PostgresClient
from tqdm import tqdm
from codetiming import Timer
import threading
from cpuinfo import get_cpu_info
import psycopg2.extensions


# Instantiate logger
log = logging.getLogger(__name__)

# The number of threads is based on the CPU cores
info = get_cpu_info()
cores = info["count"]

def historyThread(
    data: list,
    db: PostgresClient,
):
    """Thread to handle importing

    Args:
        data (list): The list of records to import
        db (PostgresClient): A database connection
        tm (TMImport): the input handle
    """
    pbar = tqdm(data)
    for record in pbar:
        action = record['action']
        date = record['action_date']
        # Remove embedded single quotes
        text = str()
        if record['action_text'] is None:
            text = "NULL"
        else:
            text = record['action_text'].replace("'", "")
        timestamp = "{:%Y-%m-%dT%H:%M:%S}".format(date)
        record['action_date'] = "NULL" #timestamp
        # FIXME: currently the schema has this as an int, it's actully an enum
        func = eval(f"Taskaction.{action}")
        record['action'] = func.value
        # columns = f"id, project_id, history.action, history.action_text, history.action_date, history.user_id"
        # nested = f"{record['id']}, {record['project_id']}, {func.value}, '{text}', '{timestamp}', {record['user_id']}"
        sql = f"UPDATE tasks"
        # sql += f" SET history.action='{func.value}', history.action_text='{text}', history.action_date='{timestamp}' WHERE id={record['task_id']} AND project_id={record['project_id']}"
        sql += f" SET history = (SELECT ARRAY_APPEND(history,({func.value}, '{text}', '{timestamp}', {record['user_id']})::task_history)) "
        sql += f"WHERE id={record['task_id']} AND project_id={record['project_id']}"
        # print(f"{sql};")
        try:
            result = db.dbcursor.execute(sql)
        except:
            log.error(f"Couldn't execute query! '{sql}'")

    return True

def invalidationThread(
    data: list,
    db: PostgresClient,
):
    """Thread to handle importing

    Args:
        data (list): The list of records to import
        db (PostgresClient): A database connection
    """
    pbar = tqdm(data)
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

        columns = f"is_closed, mapper_id, mapped_date, invalidator_id, invalidated_date, invalidation_history_id, validator_id, validated_date, updated_date"

        # columns = f"id, project_id, invalidation_history.is_closed, invalidation_history.mapper_id, invalidation_history.mapped_date, invalidation_history.invalidator_id, invalidation_history.invalidated_date, invalidation_history.invalidation_history_id, invalidation_history.validator_id, invalidation_history.validated_date, invalidation_history.updated_date"
        # nested = f"{record['id']}, {record['project_id']}, {record['is_closed']}, {record['mapper_id']}, {map_timestamp}, {record['invalidator_id']}, {inval_timestamp}, {record['invalidation_history_id']}, {vid}, {val_timestamp}, {up_timestamp}"
        sql = f"UPDATE tasks"
        #sql += f" SET invalidation_history.is_closed={record['is_closed']}, invalidation_history.mapper_id={record['mapper_id']}, invalidation_history.mapped_date={map_timestamp}, invalidation_history.invalidator_id={record['invalidator_id']}, invalidation_history.invalidated_date={inval_timestamp}, invalidation_history.invalidation_history_id={record['invalidation_history_id']}, invalidation_history.validator_id={vid}, invalidation_history.validated_date={val_timestamp}, invalidation_history.updated_date={up_timestamp}"
        sql += f"  SET invalidation_history = (SELECT ARRAY_APPEND(invalidation_history,({record['is_closed']}, {record['mapper_id']}, {map_timestamp}, {record['invalidator_id']}, {inval_timestamp}, {record['invalidation_history_id']}, {vid}, {val_timestamp}, {up_timestamp})::task_invalidation_history)) "
        sql += f"WHERE id={record['task_id']} AND project_id={record['project_id']}"
        # print(f"{sql};")
        try:
            result = db.dbcursor.execute(sql)
        except:
            log.error(f"Couldn't execute query! '{sql}'")
            #return False

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
        super().__init__('tasks', dburi)

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
        tmp = f"{table.capitalize()}Table()"
        tt = eval(tmp)
        columns = str(tt.data.keys())[11:-2].replace("'", "")

        # sql = f"SELECT row_to_json({self.table}) as row FROM {self.table} ORDER BY id LIMIT {count} OFFSET {offset}"
        sql = f"SELECT {columns} FROM {table} ORDER BY project_id LIMIT {count} OFFSET {offset}"
        # print(sql)
        result = list()
        try:
            pg.dbcursor.execute(sql)
            result = pg.dbcursor.fetchall()
        except:
            log.error(f"Couldn't execute: {sql}")

        data = list()
        # Since we're not using row_to_json(), build a data structure
        for record in result:
            table = dict(zip(tt.data.keys(), record))
            data.append(table)

        return data

    def mergeHistory(self):
        """
        A method to merge the contents of the TM campaign_projects into
        the campaigns table as an array.
        """
        table = 'task_history'
        adminpg = list()
        tmpg = list()
        for i in range(0, cores + 1):
            # FIXME: this shouldn't be hardcoded
            adminpg.append(PostgresClient('localhost/tm_admin'))
            # tmpg.append(PostgresClient('localhost/tm4'))

        pg = PostgresClient('localhost/tm4')
        sql = f"SELECT COUNT(id) FROM task_history"
        # sql = f"SELECT id, project_id, task_id, action, action_text, action_date, user_id FROM task_history"
        # print(sql)
        try:
            result = pg.dbcursor.execute(sql)
        except:
            log.error(f"Couldn't execute query! {sql}")
            return False
        # data = pg.dbcursor.fetchall()
        entries = pg.dbcursor.fetchone()[0]
        log.debug(f"There are {entries} records in {table}")

        # This input data is huge! Make smaller chunks
        chunk = round((entries / cores))

        # Some tables in the input database are huge, and can either core
        # dump python, or have performance issues. Past a certain threshold
        # the data needs to be queried in pages instead of the entire table
        # This is a huge table, we can't read in the entire thing
        with concurrent.futures.ThreadPoolExecutor(max_workers=cores) as executor:
            # adminpg = PostgresClient('localhost/tm_admin'))
            # tmpg = PostgresClient('localhost/tm4'))
            for block in range(0, entries, chunk):
                adminpg = PostgresClient('localhost/tm_admin')
                index = 0
                try:
                    data = self.getPage(block, chunk, pg, table)
                    if len(data) == 0:
                        log.error(f"getPage() returned no data for {block}:{chunk}")
                        data = self.getPage(block, chunk, pg, table)
                        if len(data) == 0:
                            log.error(f"getPage() returned no data for {block}:{chunk}, second attempt")
                            continue
                except:
                    #tmpg[index].dbshell.close()
                    #tmpg[index] = PostgresClient('localhost/tm4')
                    log.error(f"Couldn't get a page of data!")
                    continue
                try:
                    log.error(f"Dispatching thread {index}...")
                    result = historyThread(data, adminpg)
                    # result = executor.submit(historyThread, data, adminpg)
                    index += 1
                except:
                    log.error(f"FIXME: {index}")
                    index = 0
            executor.shutdown()

        # # cleanup the connections
        # for conn in adminpg:
        #     conn.dbshell.close()
        # for conn in tmpg:
        #     conn.dbshell.close()

    def mergeInvalidations(self):
        """
        A method to merge the contents of the TM campaign_projects into
        the campaigns table as an array.
        """
        table = 'task_invalidation_history'
        adminpg = list()
        for i in range(0, cores + 1):
            # FIXME: this shouldn't be hardcoded
            adminpg.append(PostgresClient('localhost/tm_admin'))

        tmpg = PostgresClient('localhost/tm4')
        sql = f"SELECT COUNT(id) FROM {table}"
        # print(sql)
        try:
            result = tmpg.dbcursor.execute(sql)
        except:
            log.error(f"Couldn't execute query! {sql}")
            return False
        entries = tmpg.dbcursor.fetchone()[0]
        log.debug(f"There are {entries} records in {table}")

        chunk = round(entries / cores)

        # Some tables in the input database are huge, and can either core
        # dump python, or have performance issues. Past a certain threshold
        # the data needs to be queried in pages instead of the entire table
        # This is a huge table, we can't read in the entire thing
        with concurrent.futures.ThreadPoolExecutor(max_workers=cores) as executor:
            index = 0
            for block in range(0, entries, chunk):
                data = self.getPage(block, chunk, tmpg, table)
                # result = invalidationThread(data, adminpg[index])
                result = executor.submit(invalidationThread, data, adminpg[index])
                index += 1
            executor.shutdown()

        # cleanup the connections
        tmpg.dbshell.close()
        for conn in adminpg:
            conn.dbshell.close()

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

    tasks = TasksDB(args.uri)
    # tasks.mergeAxuTables()
    # tasks.mergeHistory()
    tasks.mergeInvalidations()

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
    main()
