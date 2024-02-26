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
from tm_admin.types_tm import Mappingtypes, Projectstatus, Taskcreationmode, Editors, Permissions, Projectpriority, Projectdifficulty, Teamroles
from tm_admin.projects.projects_class import ProjectsTable
from tm_admin.tasks.tasks_class import TasksTable
from tm_admin.messages.messages import MessagesDB
from tm_admin.projects.projects import ProjectsDB
from tm_admin.users.users import UsersDB
from tm_admin.teams.teams import TeamsDB
from shapely import wkb, get_coordinates
from tm_admin.dbsupport import DBSupport
from tm_admin.generator import Generator
from osm_rawdata.pgasync import PostgresClient
import re
# from progress import Bar, PixelBar
from tqdm import tqdm
import tqdm.asyncio
from codetiming import Timer
import asyncio

# The number of threads is based on the CPU cores
info = get_cpu_info()
cores = info["count"] * 2

# Instantiate logger
log = logging.getLogger(__name__)

class CampaignsAPI(PostgresClient):
    def __init__(self):
        """
        Create a class to handle the backend API calls, so the code can be shared
        between test cases and the actual code.

        Returns:
            (CampaignsAPI): An instance of this class
        """
        self.allowed_roles = [
            Teamroles.TEAM_MAPPER,
            Teamroles.TEAM_VALIDATOR,
            Teamroles.TEAM_MANAGER,
        ]
        self.messagesdb = MessagesDB()
        self.usersdb = UsersDB()
        self.teamsdb = TeamsDB()

    async def connectDBs(self,
                      uri: str,
                      ):
        """
        Connect to all tables for API endpoints that require accessing multiple tables.

        Args:
            inuri (str): The URI for the TM Admin output database
        """
        await self.connect(uri)
        await self.messagesdb.connect(uri)
        await self.usersdb.connect(uri)
        await self.teamsdb.connect(uri)

    async def create(self,
                     campaign: CampaignsTable,
                     ):
        """
        Create a campaign and add it to the database.

        Args:
            campaign (CampaignsTable): The team data

        Returns:
            (bool): Whether the campaign got created
        """
        log.warning(f"create(): unimplemented!")

        return False

    async def update(self,
                     campaign: CampaignsTable,
                     ):
        """
        Update a campaign that is already in the database.

        Args:
            campaign (CampaignsTable): The campaign data

        Returns:
            (bool): Whether the campaign got updated
        """
        log.warning(f"update(): unimplemented!")

        return False

    async def delete(self,
                    campaign_id: int,
                    ):
        """
        Delete a campaign from the database.

        Args:
            campaign_id (id): The campaign data

        Returns:
            (bool): Whether the campaign got deleted
        """
        log.warning(f"delete(): unimplemented!")

        return False

async def main():
    """This main function lets this class be run standalone by a bash script."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", nargs="?", const="0", help="verbose output")
    parser.add_argument("-u", "--uri", default='localhost/tm_admin', help="Database URI")

    args = parser.parse_args()

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

if __name__ == "__main__":
    """This is just a hook so this file can be run standalone during development."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
