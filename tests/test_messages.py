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
from tm_admin.types_tm import Userrole, Mappinglevel
from datetime import datetime
from tm_admin.messages.api import MessagesAPI
from tm_admin.users.users_class import UsersTable
from tm_admin.messages.messages import MessagesDB
from tm_admin.messages.messages_class import MessagesTable
import asyncio
from codetiming import Timer

# Instantiate logger
log = logging.getLogger(__name__)

import tm_admin as tma
rootdir = tma.__path__[0]

# FIXME: For now these tests assume you have a local postgres installed. One has the TM
# database, the other for tm_admin.

# user = UsersDB()
messages = MessagesAPI()

async def create_message():
    # log.debug(f--- create_message() unimplemented!)
    msg = MessagesTable(id = 197862, message="Hi has just been validated",
                        from_user_id = 7775678, to_user_id = 6643593,
                        date = '2018-06-04T04:49:02.614348',
                        read = False,message_type=4,
                        project_id = 3213, task_id = 777,
                        )
    result = await messages.create(msg)

    msg = MessagesTable(id=272032,message="Hi has just been validated",
                        from_user_id = 7775590, to_user_id = 8405478,
                        date = '2018-07-19T03:17:42.122209',
                        read = False, message_type = 4,
                        project_id = 4231, task_id = 90,
                        )
    result = await messages.create(msg)

    msg = MessagesTable(id=89136,message="Hi has just been validated",
                         from_user_id = 5484336, to_user_id = 3043750,
                         date = '2018-02-07T13:32:47.56986',
                         read = False, message_type = 4,
                         project_id = 4091, task_id = 55
                         )
    result = await messages.create(msg)

async def get_all_messages():
    log.debug(f"--- get_all_messages() unimplemented!")

async def get_message():
    """Gets the specified message to a user"""
    log.debug(f"--- get_message() ---")
    # message_id: int, to_ser_id: int) -> Message:
    message_id = 197862
    user_id = 6643593
    data = await messages.getColumns(['*'], {"id": message_id, "to_user_id": user_id})
    assert len(data) > 0

async def send_welcome_message():
    """Sends welcome message to new user at Sign up"""
    # user: User):
    log.debug(f"--- send_welcome_message() unimplemented!")

async def send_message_after_validation():
    # ):
    log.debug(f"--- send_message_after_validation() unimplemented!")
    # status: int, validated_by: int, mapped_by: int, task_id: int, project_id: int

async def send_message_to_all_contributors():
    # project_id: int, message_dto: MessageDTO):
    log.debug(f"--- send_message_to_all_contributors() unimplemented!")
    """Sends supplied message to all contributors on specified project."""

async def _push_messages():
    # messages):
    log.debug(f"--- _push_messages() unimplemented!")

async def send_message_after_comment():
    log.debug(f"--- send_message_after_comment() unimplemented!")
    # comment_from: int, comment: str, task_id: int, project_id: int

async def send_project_transfer_message():
    log.debug(f"--- send_project_transfer_message() unimplemented!")
    # project_id: int,

async def get_user_link():
    # username: str):
    log.debug(f"--- get_user_link() unimplemented!")

async def get_team_link():
    # team_name: str, team_id: int, management: bool):
    log.debug(f"--- get_team_link() unimplemented!")

async def send_request_to_join_team():
    log.debug(f"--- send_request_to_join_team() unimplemented!")
    # from_user: int, from_username: str, to_user: int, team_name: str, team_id: int

async def accept_reject_request_to_join_team():
    log.debug(f"--- accept_reject_request_to_join_team() unimplemented!")
    # from_user: int,
        
async def accept_reject_invitation_request_for_team():
    log.debug(f"--- accept_reject_invitation_request_for_team() unimplemented!")
    # from_user: int,
    
async def send_team_join_notification():
    log.debug(f"--- send_team_join_notification() unimplemented!")
    # from_user: int,

async def send_message_after_chat():
    log.debug(f"--- send_message_after_chat() unimplemented!")
    #    chat_from: int, chat: str, project_id: int, project_name: str
    
async def send_favorite_project_activities():
    # user_id: int):
    log.debug(f"--- send_favorite_project_activities() unimplemented!")

async def resend_email_validation():
    """Resends the email validation email to the logged in user"""
    # user_id: int):
    log.debug(f"--- resend_email_validation() unimplemented!")

async def _parse_message_for_bulk_mentions():
    log.debug(f"--- _parse_message_for_bulk_mentions() unimplemented!")
    # message: str, project_id: int, task_id: int = None
    
async def _parse_message_for_username():
    log.debug(f"--- _parse_message_for_username() unimplemented!")
    # message: str, project_id: int, task_id: int = None

async def has_user_new_messages():
    """Determines if the user has any unread messages"""
    # user_id: int) -> dict:
    log.debug(f"--- has_user_new_messages() unimplemented!")
async def mark_all_messages_read():
    """Marks all messages as read for the user"""
    # user_id: int, message_type: str = None):
    log.debug(f"--- mark_all_messages_read() unimplemented!")

async def mark_multiple_messages_read():
    """Marks the specified messages as read for the user"""
    # message_ids: list, user_id: int):
    log.debug(f"--- mark_multiple_messages_read() unimplemented!")

async def get_message_as_dto():
    """Gets the selected message and marks it as read"""
    # message_id: int, user_id: int):
    log.debug(f"--- get_message_as_dto() unimplemented!")

async def delete_all_messages():
    """Deletes all messages to the user"""
    # user_id: int, message_type: str = None):
    log.debug(f"--- delete_all_messages() unimplemented!")

async def get_task_link():
    log.debug(f"--- get_task_link() unimplemented!")
    #project_id: int, task_id: int, base_url=None, highlight=False

async def get_project_link():
    log.debug(f"--- get_project_link() unimplemented!")
    # project_id: int,

async def get_user_profile_link():
    """Helper method to generate a link to a user profile"""
    # user_name: str, base_url=None) -> str:
    log.debug(f"--- get_user_profile_link() unimplemented!")

async def get_user_settings_link():
    """Helper method to generate a link to a user profile"""
    # section=None, base_url=None) -> str:
    log.debug(f"--- get_user_settings_link() unimplemented!")

async def get_organisation_link():
    log.debug(f"--- get_organisation_link() unimplemented!")
    # ganisation_id: int, organisation_name: str, base_url=None

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
        # format=("%(asctime)s.%(msecs)03d [%(levelname)s] " "%(name)s | %(funcName)s:%(lineno)d | %(message)s"),
        format=("[%(levelname)s] " "%(name)s | %(funcName)s:%(lineno)d | %(message)s"),
        datefmt="%y-%m-%d %H:%M:%S",
        stream=sys.stdout,
    )

    # await user.connect(args.uri)
    await messages.initialize(args.uri)
    await create_message()

    await send_welcome_message()
    await send_message_after_validation()
    await send_message_to_all_contributors()
    await _push_messages()
    await send_message_after_comment()
    await send_project_transfer_message()
    await get_user_link()
    await get_team_link()
    await send_request_to_join_team()
    await accept_reject_request_to_join_team()
    await accept_reject_invitation_request_for_team()
    await send_team_join_notification()
    await send_message_after_chat()
    await send_favorite_project_activities()
    await resend_email_validation()
    await _parse_message_for_bulk_mentions()
    await _parse_message_for_username()
    await has_user_new_messages()
    await get_all_messages()
    await get_message()
    await mark_all_messages_read()
    await mark_multiple_messages_read()
    await get_message_as_dto()
    # await delete_message()
    # await delete_multiple_messages()
    await delete_all_messages()
    await get_task_link()
    await get_project_link()
    await get_user_profile_link()
    await get_user_settings_link()
    await get_organisation_link()

    # Cleanup the records this test added
    await messages.delete([197862, 272032, 89136])

if __name__ == "__main__":
    """This is just a hook so this file can be run standalone during development."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
