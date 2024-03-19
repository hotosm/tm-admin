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
# from tm_admin.organizations.organizations_proto import OrganizationsMessage
#from tm_admin.yamlfile import YamlFile
from tm_admin.organizations.organizations import OrganizationsDB
from tm_admin.types_tm import Organizationtype, Mappinglevel, Teammemberfunctions
from datetime import datetime
from tm_admin.teams.teams import TeamsDB
from tm_admin.teams.api import TeamsAPI
from tm_admin.teams.teams_class import TeamsTable
import asyncio
from codetiming import Timer
from tm_admin.teams.team_members_class import Team_membersTable
import tm_admin

# Instantiate logger
log = logging.getLogger(__name__)

import tm_admin as tma
rootdir = tma.__path__[0]

# FIXME: For now these tests assume you have a local postgres installed. One has the TM
# database, the other for tm_admin.

teams = TeamsAPI()

async def create_teams():
    await teams.deleteRecords([1, 2])
    await teams.resetSequence()
    team_id = 1
    team = TeamsTable(id = team_id, organisation_id = 56,
                      name = "HOT Practice Team",
                      description = "For fun", visibility = "PUBLIC",)
    result = await teams.insertRecords([team])

    team_members = {"active": "false", "user_id": 1, "function": "MEMBER"}
#                     {"active": "true", "user_id": 2, "function": "MANAGER"}
    result = await teams.updateColumns({"team_members": team_members}, {"id": team_id})
    team_members =  {"active": "true", "user_id": 2, "function": "MANAGER"}
    result = await teams.appendColumns({"team_members": team_members}, {"id": team_id})

    team_id = 2
    team = TeamsTable(id = team_id, organisation_id = 56, name = "Not Enough Practice",
                      description = "Hello World!", visibility = "PUBLIC")
    result = await teams.insertRecords([team])

    team_members = {"active": "true", "user_id": 3, "function": "MEMBER"}
    result = await teams.updateColumns({"team_members": team_members}, {"id": team_id})

async def get_team_by_id():
    log.debug(f"get_team_by_id() unimplemented!")
    team_id = 1
    result = await teams.getByID(team_id)
    # print(result)
    assert len(result) > 0

async def update_team():
    log.debug(f"update_team() unimplemented!")
    team = Team_membersTable()
    # FIXME: add data!
    # results = await teams.update(team)

async def get_team_by_name():
    log.debug(f"get_team_by_name() unimplemented!")
    name = "HOT Practice Team"
    result = await teams.getByName(name)
    # print(result)
    assert len(result) > 0

async def request_to_join_team():
    # team_id: int, user_id: int)
    log.debug(f"request_to_join_team() unimplemented!")
    member = str() # UserTable()
    # result = teams.getByName(member)
    # assert len(result) > 0

# async def add_user_to_team():
#    log.debug(f"add_user_to_team() unimplemented!")

async def add_team_member():
    log.debug(f"add_team_member() unimplemented!")
    # team_id, user_id, function, active=False)
    member = Team_membersTable()
    result = await teams.addMember(member)
    # assert result

async def _get_team_members():
    log.debug(f"--- _get_team_members() ---")
    team_id = 1
    result = await teams.getColumns({'*'}, {"id": team_id})
    # print(result)
    assert len(result) > 0

async def send_invite():
    log.debug(f"send_invite() unimplemented!")
    team_id = 1
    user_id = 17255752
    results = await teams.sendInvite(team_id, user_id)
    # print(results)
    # team_id, from_user_id, username
    
async def accept_reject_join_request():
    log.debug(f"accept_reject_join_request() unimplemented!")
    team_id = 1
    user_id = 1
    name = "HOT Practice Team"
    action = "accept"
    results = await teams.processInvite(team_id, user_id, name, action)
    # team_id, from_user_id, username, function, action
    
async def _get_active_team_members():
    log.debug(f"--- _get_active_team_members() ---")
    team_id = 1
    function = Teammemberfunctions(1)
    result = await teams.getActiveMembers(team_id, True)
    print(result)
    assert len(result) > 0

async def is_user_an_active_team_member():
    log.debug(f"is_user_an_active_team_member() unimplemented!")
    user_id = 1
    team_id = 1
    result = await teams.getColumns({'*'}, {"id": team_id, "user_id": user_id})
    assert result
    # team_id: int, user_id: int
    
async def get_all_teams():
    log.debug(f"--- get_all_teams() ---")
    # search_dto: TeamSearchDTO) -> TeamsListDT
    user_id = 1
    team_id = 1
    result = await teams.getColumns({'*'})
    assert len(result) > 0

async def is_user_team_member():
    log.debug(f"--- is_user_team_member() ---")
    user_id = 3
    team_id = 2
    function = Teammemberfunctions(Teammemberfunctions.MEMBER)
    result = await teams.checkFunction(team_id, user_id, function)
    assert result

async def is_user_team_manager():
    log.debug(f"--- is_user_team_manager() ---")
    # team_id: int, user_id: int
    user_id = 2
    team_id = 1
    function = Teammemberfunctions(Teammemberfunctions.MANAGER)
    result = await teams.checkFunction(team_id, user_id, function)
    assert result

async def accept_reject_invitation_request():
    log.debug(f"accept_reject_invitation_request() unimplemented!")

async def leave_team():
    log.debug(f"leave_team() unimplemented!")
    # team_id, username

async def add_team_project():
    log.debug(f"add_team_project() unimplemented!")

async def delete_team_project():
    log.debug(f"delete_team_project() unimplemented!")
    # team_id, project_id

async def get_projects_by_team_id():
    log.debug(f"get_projects_by_team_id() unimplemented!")
    # team_id: int

# FIXME: This should be in the projects API
async def change_team_role():
    log.debug(f"change_team_role() unimplemented!")
    #  int, project_id: int, role: str

# FIXME: this should be in the organizations API
async def assert_validate_organisation():
    log.debug(f"assert_validate_organisation() unimplemented!")
    # org_id: int

async def assert_validate_members():
    log.debug(f"assert_validate_members(team_dto:) unimplemented!")
    #  TeamDTO

async def check_team_membership():
    log.debug(f"check_team_membership() unimplemented!")
    # project_id: int, allowed_roles: list, user_id: int

async def activate_team_member():
    log.debug(f"activate_team_member() unimplemented!")
    # team_id: int, user_id: int

async def delete_invite():
    log.debug(f"delete_invite() unimplemented!")
    # team_id: int, user_id: int

async def send_message_to_all_team_members():
    log.debug(f"send_message_to_all_team_members() unimplemented!")

# async def get_team_as_dto():
#     log.debug(f"get_team_as_dto() unimplemented!")

# async def get_project_teams_as_dto():
#     log.debug(f"get_project_teams_as_dto() unimplemented!")
#     # project_id: int) -> TeamsListDT                             

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", nargs="?", const="0", help="verbose output")
    parser.add_argument("-u", "--uri", default='localhost/testdata', help="Database URI")
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

    await teams.initialize(args.uri)
    await create_teams()

    await request_to_join_team()
    await add_team_member()
    await send_invite()
    await accept_reject_join_request()
    await accept_reject_invitation_request()
    await leave_team()
    await add_team_project()
    await delete_team_project()
    await get_all_teams()
    await get_projects_by_team_id()
    await change_team_role()
    await get_team_by_id()
    await get_team_by_name()
    await update_team()
    await assert_validate_organisation()
    await assert_validate_members()
    await _get_team_members()
    await _get_active_team_members()
    await activate_team_member()
    await delete_invite()
    await is_user_team_member()
    await is_user_an_active_team_member()
    await is_user_team_manager()
    await check_team_membership()
    await send_message_to_all_team_members()
    # await get_team_as_dto()
    # await get_project_teams_as_dto()

if __name__ == "__main__":
    """This is just a hook so this file can be run standalone during development."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
