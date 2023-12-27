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
# from tm_admin.users.users_proto import UsersMessage
#from tm_admin.yamlfile import YamlFile
from tm_admin.users.users import UsersDB
from tm_admin.projects.projects import ProjectsDB
from tm_admin.types_tm import Userrole, Mappinglevel
from datetime import datetime
from tm_admin.users.users_class import UsersTable

# Instantiate logger
log = logging.getLogger(__name__)

import tm_admin as tma
rootdir = tma.__path__[0]

# FIXME: For now these tests assume you have a local postgres installed. One has the TM
# database, the other for tm_admin.

user = UsersDB('localhost/testdata')
project = ProjectsDB('localhost/testdata')

def send_welcome_message():
    """Sends welcome message to new user at Sign up"""
    # user: User):
    log.debug(f"--- send_welcome_message() unimplemented!")

def send_message_after_validation():
    # ):
    log.debug(f"--- send_message_after_validation() unimplemented!")
    # status: int, validated_by: int, mapped_by: int, task_id: int, project_id: int

def send_message_to_all_contributors():
    # project_id: int, message_dto: MessageDTO):
    log.debug(f"--- send_message_to_all_contributors() unimplemented!")
    """Sends supplied message to all contributors on specified project."""

def _push_messages():
    # messages):
    log.debug(f"--- _push_messages() unimplemented!")

def send_message_after_comment():
    log.debug(f"--- send_message_after_comment() unimplemented!")
    # comment_from: int, comment: str, task_id: int, project_id: int

def send_project_transfer_message():
    log.debug(f"--- send_project_transfer_message() unimplemented!")
    # project_id: int,

def get_user_link():
    # username: str):
    log.debug(f"--- get_user_link() unimplemented!")

def get_team_link():
    # team_name: str, team_id: int, management: bool):
    log.debug(f"--- get_team_link() unimplemented!")

def send_request_to_join_team():
    log.debug(f"--- send_request_to_join_team() unimplemented!")
    # from_user: int, from_username: str, to_user: int, team_name: str, team_id: int

def accept_reject_request_to_join_team():
    log.debug(f"--- accept_reject_request_to_join_team() unimplemented!")
    # from_user: int,
        
def accept_reject_invitation_request_for_team():
    log.debug(f"--- accept_reject_invitation_request_for_team() unimplemented!")
    # from_user: int,
    
def send_team_join_notification():
    log.debug(f"--- send_team_join_notification() unimplemented!")
    # from_user: int,

def send_message_after_chat():
    log.debug(f"--- send_message_after_chat() unimplemented!")
    #    chat_from: int, chat: str, project_id: int, project_name: str
    
def send_favorite_project_activities():
    # user_id: int):
    log.debug(f"--- send_favorite_project_activities() unimplemented!")

def resend_email_validation():
    """Resends the email validation email to the logged in user"""
    # user_id: int):
    log.debug(f"--- resend_email_validation() unimplemented!")

def _parse_message_for_bulk_mentions():
    log.debug(f"--- _parse_message_for_bulk_mentions() unimplemented!")
    # message: str, project_id: int, task_id: int = None
    
def _parse_message_for_username():
    log.debug(f"--- _parse_message_for_username() unimplemented!")
    # message: str, project_id: int, task_id: int = None

def has_user_new_messages():
    """Determines if the user has any unread messages"""
    # user_id: int) -> dict:
    log.debug(f"--- has_user_new_messages() unimplemented!")

def get_all_messages():
    log.debug(f"--- get_all_messages() unimplemented!")
    # user_id: int,

def get_message():
    """Gets the specified message"""
    # message_id: int, user_id: int) -> Message:
    log.debug(f"--- get_message() unimplemented!")

def mark_all_messages_read():
    """Marks all messages as read for the user"""
    # user_id: int, message_type: str = None):
    log.debug(f"--- mark_all_messages_read() unimplemented!")

def mark_multiple_messages_read():
    """Marks the specified messages as read for the user"""
    # message_ids: list, user_id: int):
    log.debug(f"--- mark_multiple_messages_read() unimplemented!")

def get_message_as_dto():
    """Gets the selected message and marks it as read"""
    # message_id: int, user_id: int):
    log.debug(f"--- get_message_as_dto() unimplemented!")

def delete_message():
    """Deletes the specified message"""
    # message_id: int, user_id: int):
    log.debug(f"--- delete_message() unimplemented!")

def delete_multiple_messages():
    """Deletes the specified messages to the user"""
    # message_ids: list, user_id: int):
    log.debug(f"--- delete_multiple_messages() unimplemented!")

def delete_all_messages():
    """Deletes all messages to the user"""
    # user_id: int, message_type: str = None):
    log.debug(f"--- delete_all_messages() unimplemented!")

def get_task_link():
    log.debug(f"--- get_task_link() unimplemented!")
    #project_id: int, task_id: int, base_url=None, highlight=False

def get_project_link():
    log.debug(f"--- get_project_link() unimplemented!")
    # project_id: int,

def get_user_profile_link():
    """Helper method to generate a link to a user profile"""
    # user_name: str, base_url=None) -> str:
    log.debug(f"--- get_user_profile_link() unimplemented!")

def get_user_settings_link():
    """Helper method to generate a link to a user profile"""
    # section=None, base_url=None) -> str:
    log.debug(f"--- get_user_settings_link() unimplemented!")

def get_organisation_link():
    log.debug(f"--- get_organisation_link() unimplemented!")
    # ganisation_id: int, organisation_name: str, base_url=None

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
        # format=("%(asctime)s.%(msecs)03d [%(levelname)s] " "%(name)s | %(funcName)s:%(lineno)d | %(message)s"),
        format=("[%(levelname)s] " "%(name)s | %(funcName)s:%(lineno)d | %(message)s"),
        datefmt="%y-%m-%d %H:%M:%S",
        stream=sys.stdout,
    )

    send_welcome_message()
    send_message_after_validation()
    send_message_to_all_contributors()
    _push_messages()
    send_message_after_comment()
    send_project_transfer_message()
    get_user_link()
    get_team_link()
    send_request_to_join_team()
    accept_reject_request_to_join_team()
    accept_reject_invitation_request_for_team()
    send_team_join_notification()
    send_message_after_chat()
    send_favorite_project_activities()
    resend_email_validation()
    _parse_message_for_bulk_mentions()
    _parse_message_for_username()
    has_user_new_messages()
    get_all_messages()
    get_message()
    mark_all_messages_read()
    mark_multiple_messages_read()
    get_message_as_dto()
    delete_message()
    delete_multiple_messages()
    delete_all_messages()
    get_task_link()
    get_project_link()
    get_user_profile_link()
    get_user_settings_link()
    get_organisation_link()
