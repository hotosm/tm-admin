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
from alive_progress import alive_bar
from tqdm import tqdm
from codetiming import Timer
import threading

# Instantiate logger
log = logging.getLogger(__name__)

# The number of threads is based on the CPU cores
info = get_cpu_info()
cores = info["count"] * 2

MsgFilter = {
    'user_id': int = 0,
    'locale': str = "en",
    'page': int = 0,
    'page_size': int = 10,
    'sort_by': str = None,
    'sort_direction': bool = True,
    'message_type': Message_type = None,
    'from_username': str = None,
    'project_id': int = None,
    'task_id': = None,
    'status' = None,
):

class MessagesDB(DBSupport):
    def __init__(self,
                 dburi: str = "localhost/tm_admin",
                ):
        """
        A class to access the messages table.

        Args:
            dburi (str): The URI string for the database connection

        Returns:
            (MessagesDB): An instance of this class
        """
        self.pg = None
        self.profile = MessagesTable()
        self.types = dir(tm_admin.types_tm)
        super().__init__('messages', dburi)

    def getByFilter(self,
                    user_id: int,
                    locale: str,
                    page: int,
                    page_size = 10,
                    sort_by = None,
                    sort_direction = None,
                    message_type = None,
                    from_username = None,
                    project = None,
                    task_id = None,
                    status = None,
                    ):
        """
        Filter
        Args:
            msg (MessagesTable): The filter criteria

        Returns:
            (list): the messages that match the filter
        """
        if sort_column is None:
        if project is not None:
        if task_id is not None:
        if status in ["read", "unread"]:
        if message_type:
        if from_username is not None:

    
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

    message = MessagesDB(args.uri)

    # These may take a long time to complete
    #if message.mergeInterests():
    #    log.info("MessageDB.mergeInterests worked!")


if __name__ == "__main__":
    """This is just a hook so this file can be run standalone during development."""
    main()
