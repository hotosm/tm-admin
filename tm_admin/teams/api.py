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
from tm_admin.types_tm import Mappingtypes, Projectstatus, Taskcreationmode, Editors, Permissions, Projectpriority, Projectdifficulty, Teamrole, Teammemberfunctions
# from osm_rawdata.pgasync import PostgresClient
from tm_admin.teams.teams_class import TeamsTable
from tm_admin.teams.team_members_class import Team_membersTable
from tm_admin.messages.messages import MessagesDB
from tm_admin.projects.projects import ProjectsDB
from tm_admin.users.users import UsersDB
from tm_admin.teams.teams import TeamsDB
import re
from codetiming import Timer
import asyncio
from tm_admin.pgsupport import PGSupport

# The number of threads is based on the CPU cores
info = get_cpu_info()
cores = info["count"] * 2

# Instantiate logger
log = logging.getLogger(__name__)

class TeamsAPI(PGSupport):
    def __init__(self):
        """
        Create a class to handle the backend API calls, so the code can be shared
        between test cases and the actual code.

        Returns:
            (TeamsAPI): An instance of this class
        """
        self.allowed_roles = [
            Teamrole.TEAM_MAPPER,
            Teamrole.TEAM_VALIDATOR,
            Teamrole.TEAM_MANAGER,
        ]
        super().__init__("teams")

    async def initialize(self,
                      uri: str,
                      ):
        """
        Connect to all tables for API endpoints that require
        accessing multiple tables.

        Args:
            inuri (str): The URI for the TM Admin output database
        """
        await self.connect(uri)
        await self.getTypes("teams")

    async def getByID(self,
                     team_id: int,
                    ):
        """
        Get all the information for a team using it's ID

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
        Get all the information for a team using the name

        Args:
            name (str): The team to get the data for

        Returns:
            (dict): the team information
        """
        log.debug(f"--- getByName() ---")
        sql = f"SELECT * FROM teams WHERE name='{name}'"
        results = await self.execute(sql)
        return results
        
    async def addMember(self,
                        member: Team_membersTable,
                        ):
        """

        Args:
            
        Returns:
            
        """
        log.warning(f"addMember(): unimplemented!")

        return False

    async def removeMember(self):
        """

        Args:
            
        Returns:
            
        """
        log.warning(f"removeMember(): unimplemented!")

        return False

    async def addProject(self):
        """

        Args:
            
        Returns:
            
        """
        log.warning(f"addProject(): unimplemented!")

        return False

    async def removeProject(self):
        """

        Args:
            
        Returns:
            
        """
        log.warning(f"removeProject(): unimplemented!")

        return False

    async def validateMembers(self):
        """
        Validates that the users exist

        Args:
            
        Returns:
            
        """
        log.warning(f"validateMembers(): unimplemented!")


        return False

    async def activateMember(self):
        """

        Args:
            
        Returns:
            
        """
        log.warning(f"activateMember(): unimplemented!")

        return False

    async def checkFunction(self,
                       team_id: int,
                       user_id: int,
                       function: Teammemberfunctions,
                       ):
        """
        Check if a team member has a specific team function.

        Args:
            team_id (int): The team to check
            user_id (int): The user to check
            function (Teammemberfunctions): Member or Manager

        Returns:
            (bool): Whether the user is a manager of this team
        """
        log.warning(f"isManager(): unimplemented!")
        sql = "SELECT jsonb_path_query(team_members, '$.members[*] ? (@.function==\"%s\" && @.user_id==%d)') AS members FROM teams WHERE id=%d;" % (function.name, user_id, team_id)
        result = await self.execute(sql)

        return result

    async def joinRequest(self,
                          team_id: int,
                          user_id: int,
                          ):
        """
        If user has team manager permission add directly to the team
        without request.E.G. Admins, Org managers.

        Args:
            team_id (int): The team ID
            user_id (int): The user ID
        """
        log.warning(f"joinRequest(): unimplemented!")

        return False

    async def processJoinRequest(self):
        # team_id, from_user_id, username, function, action
        log.warning(f"processRequest(): unimplemented!")

        return False

    async def processInvite(self,
                            team_id: int,
                            user_id: int,
                            name: str,
                            action: str,
                            ):
        """
        Create the Accept or Reject invitation request message.

        Args:
            team_id (int): The team the members are on
            user_id (int): The user sending the invite
            name (str): The user the invite was sent to
            action (str): The action
        """
        # team_id, from_user_id, username, function, action
        log.warning(f"processRequest(): unimplemented!")

        # Construct the message
        mdb = MessagesDB()

        return False

    async def sendInvite(self,
                          team_id: int,
                          user_id: int,
                          ):
        """
        Send an invite to a user to join a team.

        Args:
            team_id (int): The team to join
            user_id (int): The user to join
        """
        log.warning(f"sendInvite(): unimplemented!")
        # Construct the message
        mdb = MessagesDB()

        return False

    async def DeleteInvite(self,
                          team_id: int,
                          user_id: int,
                          ):
        """
        Delete a invite message to join a team

        Args:
            team_id (int): The team to delete
            user_id (int): The user to delete
        """
        log.warning(f"deleteInvite(): unimplemented!")
        # Construct the message
        mdb = MessagesDB()

        return False

    async def checkMembership(self,
                            project_id: int,
                            user_id: int,
                            ):
        """
        Given a project and permitted team roles, check user's membership
        in the team list.

        Args:
            project_id (int): The project to check
            user_id (int): The ID of the user to check

        Returns:
            (bool): If the user has the required permissions
        """
        log.warning(f"isMember(): in progress!")
        projectsdb.getTeamRole(project_id, team_id)
        # self.allowed_roles
        sql = f" "
        results = await self.execute(sql)
        return results
        
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
