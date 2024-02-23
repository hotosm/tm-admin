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
from tm_admin.types_tm import Mappingtypes, Projectstatus, Taskcreationmode, Editors, Permissions, Projectpriority, Projectdifficulty, Teamroles, Teammemberfunctions
from osm_rawdata.pgasync import PostgresClient
from tm_admin.teams.team_members_class import Team_membersTable
import re
from codetiming import Timer
import asyncio

# The number of threads is based on the CPU cores
info = get_cpu_info()
cores = info["count"] * 2

# Instantiate logger
log = logging.getLogger(__name__)

class TeamMember(object):
    def __init__(self,
                 team_id: int,
                 user_id: int,
                 function: Teammemberfunctions,
                 active: bool = False,
                 ):
        self.team_id = team_id
        self.user_id = user_id
        self.function = function
        self.active = active
    
class TeamsAPI(PostgresClient):
    def __init__(self):
        self.allowed_roles = [
            Teamroles.TEAM_MAPPER,
            Teamroles.TEAM_VALIDATOR,
            Teamroles.TEAM_MANAGER,
        ]

    async def getByID(self,
                     team_id: int,
                    ):
        """
        Get all the information for a team

        Args:
            team_id (int): The team to get the data for

        Returns:
            (dict): the team information
        """
        log.debug(f"--- getByID() ---")
        sql = f"SELECT * FROM teams WHERE id={team_id}"
        results = await self.execute(sql)
        return results

    async def getByName(self,
                        name: str,
                        ):
        """
        Get all the information for a team

        Args:
            name (str): The team to get the data for

        Returns:
            (dict): the team information
        """
        log.debug(f"--- getByName() ---")
        sql = f"SELECT * FROM teams WHERE name='{name}'"
        results = await self.execute(sql)
        return results

    async def create(self):
        log.warning(f"create(): unimplemented!")
        
    async def update(self):
        log.warning(f"update(): unimplemented!")
        
    async def delete(self):
        log.warning(f"delete(): unimplemented!")
        
    async def getAllTeams(self):
        log.warning(f"getAllTeams(): unimplemented!")
    
    async def addMember(self,
                        member: TeamMember,
                        ):
        log.warning(f"addMember(): unimplemented!")

    async def removeMember(self):
        log.warning(f"removeMember(): unimplemented!")

    async def addProject(self):
        log.warning(f"addProject(): unimplemented!")

    async def removeProject(self):
        log.warning(f"removeProject(): unimplemented!")

    async def validateMembers(self):
        """Validates that the users exist"""
        log.warning(f"validateMembers(): unimplemented!")

    async def activateMember(self):
        log.warning(f"activateMember(): unimplemented!")

    async def isActive(self):
        log.warning(f"isActive(): unimplemented!")

    async def isManager(self):
        log.warning(f"isManager(): unimplemented!")

    async def isMember(self):
        log.warning(f"isMember(): unimplemented!")

    async def checkMembership(self,
                            project_id: int,
                            user_id: int,
                            ):
        """
        Given a project and permitted team roles, check user's membership
        in the team list.

        Args:
            project_id (int): The ID of the project
            user_id (int): The IS of the user

        Returns:
            (bool): If the user has the required permissions
        """
        log.warning(f"isMember(): unimplemented!")
        # self.allowed_roles

        
    async def getActiveMembers(self,
                                team_id: int,
                                flip: bool = False,
                            ):
        """
        Get all the active or inactive members of a team.

        Args:
            team_id (int): The team to get the members of
            flip (bool): Returns false instead of true members

        Returns:
            (list): The active members for this team
        """
        if flip:
            sql = "SELECT jsonb_path_query(team_members, '$.members[*] ? (@.active==\"false\")') AS members FROM teams WHERE id=%d;" % team_id
        else:
            sql = "SELECT jsonb_path_query(team_members, '$.members[*] ? (@.active==\"true\")') AS members FROM teams WHERE id=%d;" % team_id

        results = await self.execute(sql)
        return results

    async def getMembers(self,
                        team_id: int,
                        function: int,
                        ):
        """
        Get all the members of a team regardless of whether they are active
        or not.

        Args:
            team_id (int): The team to get the members of
            function (Teammemberfunctions): Member or Manager

        Returns:
            (list): The members for team
        """
        if function == 0:
            # Get all members regardless of function
            sql = "SELECT jsonb_path_query(team_members, '$.members[*] ? (@.function[*] == \"MEMBER\" || @.function[*] == \"MANAGER\")')->'user_id' AS members FROM teams WHERE id=%d;" % team_id
        else:
            # Get just members or managers
            sql = "SELECT jsonb_path_query(team_members, '$.members[*] ? (@.function[*] == \"%s\")')->'user_id' AS members FROM teams WHERE id=%d;" % (function.name, team_id)

        results = await self.execute(sql)
        return results

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
