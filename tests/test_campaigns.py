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
from tm_admin.projects.api import ProjectsAPI
from tm_admin.teams.api import TeamsAPI
from tm_admin.projects.projects import ProjectsDB
from tm_admin.campaigns.campaigns import CampaignsDB
# from tm_admin.campaigns.api import CampaignsAPI
from tm_admin.types_tm import Userrole, Mappinglevel
from datetime import datetime
from tm_admin.users.users_class import UsersTable
from tm_admin.campaigns.campaigns_class import CampaignsTable
import asyncio

# Instantiate logger
log = logging.getLogger(__name__)

import tm_admin as tma
rootdir = tma.__path__[0]

# FIXME: For now these tests assume you have a local postgres installed.
# One has the TM database, the other for tm_admin.

campaign = CampaignsDB()

async def get_all_campaigns():
    """Returns a list of all campaigns"""
    # ) -> CampaignListDTO:
    log.debug(f"--- get_all_campaigns() ---")
    result = await campaign.getAll()
    assert len(result) > 0

async def get_campaign():
    """Gets the specified campaign"""
    log.debug(f"--- get_campaign() ---")
    id = 4
    result = await campaign.getByID(id)
    assert len(result) > 0

async def get_campaign_by_name():
    name = 'Mbomou'
    log.debug(f"--- get_campaign_by_name() ---")
    result = await campaign.getByName(name)
    assert len(result) > 0

async def delete_campaign():
    """Delete campaign for a project"""
    # campaign_id: int):
    log.debug(f"--- delete_campaign() ---")
    id = 5
    # result = campaign.deleteByID(id)
    # assert len(result) > 0

async def delete_project_campaign():
    """Delete campaign for a project"""
    # project_id: int, campaign_id: int):
    log.debug(f"--- delete_project_campaign() unimplemented!")
    id = 5
    # result = campaign.deleteByID(id)

async def create_campaign():
    """Creates a new campaign"""
    # campaign_dto: NewCampaignDTO):
    log.debug(f"--- create_campaign() unimplemented!")

async def create_campaign_project():
    """Assign a campaign with a project"""
    # dto: CampaignProjectDTO):
    log.debug(f"--- create_campaign_project() unimplemented!")

async def create_campaign_organisation():
    """Creates new campaign from DTO"""
    # organisation_id: int, campaign_id: int):
    log.debug(f"--- create_campaign_organisation() unimplemented!")

async def campaign_organisation_exists():
    # campaign_id: int, org_id: int):
    log.debug(f"--- campaign_organisation_exists() unimplemented!")

async def delete_organisation_campaign():
    """Delete campaign for a organisation"""
    # organisation_id: int, campaign_id: int):
    log.debug(f"--- delete_organisation_campaign() unimplemented!")

async def update_campaign():
    # campaign_dto: CampaignDTO, campaign_id: int):
    log.debug(f"--- update_campaign() unimplemented!")

# tm-admin doesn't use sqlalchemy, so no dtos. We use Campaings.DB instead.
# def get_campaign_as_dto():
#     """Gets the specified campaign"""
#     # campaign_id: int, user_id: int):
#     log.debug(f"--- get_campaign_as_dto() unimplemented!")

# def get_project_campaigns_as_dto():
#     """Gets all the campaigns for a specified project"""
#     # project_id: int) -> CampaignListDTO:
#     log.debug(f"--- get_project_campaigns_as_dto() unimplemented!")

# def get_organisation_campaigns_as_dto():
#     """Gets all the campaigns for a specified project"""
#     # organisation_id: int) -> CampaignListDTO:
#     log.debug(f"--- get_organisation_campaigns_as_dto() unimplemented!")

async def main():
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

    # await user.connect(args.uri)
    await campaign.connect(args.uri)

    await get_campaign()
    await get_campaign_by_name()
    await delete_campaign()
    await delete_project_campaign()
    await get_all_campaigns()
    await create_campaign()
    await create_campaign_project()
    await create_campaign_organisation()
    await campaign_organisation_exists()
    await delete_organisation_campaign()
    await update_campaign()
    # get_campaign_as_dto()
    # get_project_campaigns_as_dto()
    # get_organisation_campaigns_as_dto()

if __name__ == "__main__":
    """This is just a hook so this file can be run standalone during development."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
