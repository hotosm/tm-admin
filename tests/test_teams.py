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
# from tm_admin.organizations.organizations_proto import OrganizationsMessage
#from tm_admin.yamlfile import YamlFile
from tm_admin.organizations.organizations import OrganizationsDB
from tm_admin.types_tm import Organizationtype, Mappinglevel
from datetime import datetime

# Instantiate logger
log = logging.getLogger(__name__)

import tm_admin as tma
rootdir = tma.__path__[0]

# FIXME: For now these tests assume you have a local postgres installed. One has the TM
# database, the other for tm_admin.

organization = OrganizationsDB('localhost/tm_admin')

def request_to_join_team():
    # team_id: int, user_id: int)
    log.debug(f"request_to_join_team() unimplemented!")

def add_user_to_team():
    log.debug(f"add_user_to_team() unimplemented!")
    #

def add_team_member():
    log.debug(f"add_team_member() unimplemented!")
    # team_id, user_id, function, active=False)

def send_invite():
    log.debug(f"send_invite() unimplemented!")
    # team_id, from_user_id, username
    
def accept_reject_join_request():
    log.debug(f"accept_reject_join_request() unimplemented!")
    # team_id, from_user_id, username, function, action
    
def accept_reject_invitation_request():
    log.debug(f"accept_reject_invitation_request() unimplemented!")
    # 

def leave_team():
    log.debug(f"leave_team() unimplemented!")
    # team_id, username
    
def add_team_project():
    log.debug(f"add_team_project() unimplemented!")
    #
    
def delete_team_project():
    log.debug(f"delete_team_project() unimplemented!")
    # team_id, project_id
    
def get_all_teams():
    log.debug(f"get_all_teams() unimplemented!")
    # search_dto: TeamSearchDTO) -> TeamsListDT
                  
def get_team_as_dto():
    log.debug(f"get_team_as_dto() unimplemented!")
    #

def get_projects_by_team_id():
    log.debug(f"get_projects_by_team_id() unimplemented!")
    # team_id: int
    
def get_project_teams_as_dto():
    log.debug(f"get_project_teams_as_dto() unimplemented!")
    # project_id: int) -> TeamsListDT
                             
def change_team_role():
    log.debug(f"change_team_role() unimplemented!")
    #  int, project_id: int, role: str
    
def get_team_by_id():
    log.debug(f"get_team_by_id() unimplemented!")
    # team_id: int) -> Tea
                   
def get_team_by_name():
    log.debug(f"get_team_by_name() unimplemented!")
      #  str) -> Tea
                     
def create_team():
    log.debug(f"create_team() unimplemented!")
    #  -> in
    
def update_team():
    log.debug(f"update_team() unimplemented!")
    # team_dto: TeamDTO) -> Tea
                
def assert_validate_organisation():
    log.debug(f"assert_validate_organisation() unimplemented!")
    # org_id: int
                
def assert_validate_members():
    log.debug(f"assert_validate_members(team_dto:) unimplemented!")
    #  TeamDTO
    
def _get_team_members():
    log.debug(f"_get_team_members() unimplemented!")
    # team_id: int
    
def _get_active_team_members():
    log.debug(f"_get_active_team_members() unimplemented!")
    # team_id: int
    
def activate_team_member():
    log.debug(f"activate_team_member() unimplemented!")
    # team_id: int, user_id: int
    
def delete_invite():
    log.debug(f"delete_invite() unimplemented!")
    # team_id: int, user_id: int
    
def is_user_team_member():
    log.debug(f"is_user_team_member() unimplemented!")
    # team_id: int, user_id: int
    
def is_user_an_active_team_member():
    log.debug(f"is_user_an_active_team_member() unimplemented!")
    # team_id: int, user_id: int
    
def is_user_team_manager():
    log.debug(f"is_user_team_manager() unimplemented!")
    # team_id: int, user_id: int
    
def delete_team():
    log.debug(f"delete_team() unimplemented!")
    # team_id: int
    
def check_team_membership():
    log.debug(f"check_team_membership() unimplemented!")
    # project_id: int, allowed_roles: list, user_id: int
    
def send_message_to_all_team_members():
    log.debug(f"send_message_to_all_team_members() unimplemented!")

if __name__ == "__main__":
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

    request_to_join_team()
    add_user_to_team()
    add_team_member()
    send_invite()
    accept_reject_join_request()
    accept_reject_invitation_request()
    leave_team()
    add_team_project()
    delete_team_project()
    get_all_teams()
    get_team_as_dto()
    get_projects_by_team_id()
    get_project_teams_as_dto()
    change_team_role()
    get_team_by_id()
    get_team_by_name()
    create_team()
    update_team()
    assert_validate_organisation()
    assert_validate_members()
    _get_team_members()
    _get_active_team_members()
    activate_team_member()
    delete_invite()
    is_user_team_member()
    is_user_an_active_team_member()
    is_user_team_manager()
    delete_team()
    check_team_membership()
    send_message_to_all_team_members()
