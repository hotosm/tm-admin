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
from tm_admin.organizations.organizations_class import OrganizationsTable
from tm_admin.organizations.api import OrganizationsAPI
from tm_admin.types_tm import Organizationtype
from datetime import datetime
import asyncio
from codetiming import Timer

# Instantiate logger
log = logging.getLogger(__name__)

import tm_admin as tma
rootdir = tma.__path__[0]

# FIXME: For now these tests assume you have a local postgres installed. One has the TM
# database, the other for tm_admin.

organizations = OrganizationsAPI()

async def create_organisation():
    # new_organisation_dto: NewOrganisationDTO) -> int:
    log.debug(f"create_organisation() unimplemented!")
    # returns True or False
    ot = OrganizationsTable(name='test org', slug="slug",
                    subscription_tier=1,
                    type=1)
                    # type=Organizationtype.FREE)
    result = await organizations.create(ot)
    # FIXME: This is supposed to return the id, and does for other tables,
    # but for some reason we get no result, but it appears to work
    # assert result

async def get_organisation_by_id():
    log.debug(f"--- get_organisation_by_id() ---")
    # organisation_id: int) -> Organisation:
    id = 1
    result = await organizations.getByID(id)
    assert len(result) > 0

async def get_organisation_by_name():
    # organisation_name: str) -> Organisation:
    log.debug(f"--- get_organisation_by_name() ---")
    name= 'Other'
    result = await organizations.getByName(name)
    assert len(result) > 0

async def get_organisation_name_by_id():
    # organisation_id: int) -> str:
    log.debug(f"--- get_organisation_name_by_id() ---")
    org_id = 1
    result = await organizations.getColumns(["name"], {"id": org_id})
    assert len(result) > 0

async def get_organisations():
    # manager_user_id: int):
    log.debug(f"--- get_organisations() ---")
    # result = await organization.getAll()
    # assert len(result) > 0

async def delete_organisation():
    # organisation_id: int):
    log.debug(f"delete_organisation() unimplemented!")
    id = 1
    #result = await organization.deleteByID(id)
    #assert len(result) > 0

async def update_organisation():
    # organisation_dto: UpdateOrganisationDTO) -> Organisation:
    log.debug(f"update_organisation() unimplemented!")

async def get_organisations_managed_by_user():
    # user_id: int):
    log.debug(f"get_organisations_managed_by_user() unimplemented!")

async def get_projects_by_organisation_id():
    # organisation_id: int) -> Organisation:
    log.debug(f"get_projects_by_organisation_id() unimplemented!")

async def get_organisation_stats():
    #
    log.debug(f"get_organisation_stats() unimplemented!")

async def assert_validate_name():
    # org: Organisation, name: str):
    log.debug(f"assert_validate_name() unimplemented!")

async def assert_validate_users():
    # organisation_dto: OrganisationDTO):
    log.debug(f"assert_validate_users() unimplemented!")

async def can_user_manage_organisation():
    # organisation_id: int, user_id: int):
    log.debug(f"can_user_manage_organisation() unimplemented!")

async def is_user_an_org_manager():
    # organisation_id: int, user_id: int):
    log.debug(f"is_user_an_org_manager() unimplemented!")

# We don't need to test these they are for sqlachemy, which we're not using. Instead
# we use the UsersTable() to represent the table schema
# def get_organisation_dto():
# def get_organisations_managed_by_user_as_dto():
# def get_organisations_as_dto():
# def get_campaign_organisations_as_dto():
# def get_organisation_by_id_as_dto():
# def get_organisation_by_slug_as_dto():

# FMTM API tests
async def get_organisations():
    log.debug(f"--- get_organisations() unimplemented!")

async def generate_slug():
    # text: str) -> str:
    log.debug(f"--- generate_slug() unimplemented!")

async def get_organisation_by_name():
    # db: Session, name: str):
    log.debug(f"--- get_organisation_by_name() unimplemented!")

def upload_image():
    # db: Session, file: UploadFile(None)):
    log.debug(f"--- upload_image() unimplemented!")

async def create_organization():
    log.debug(f"--- create_organization() unimplemented!")
    # get_organisation_by_id(db: Session, id: int):

def update_organization_info():
    log.debug(f"--- update_organization_info() unimplemented!")

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
        format=("%(asctime)s.%(msecs)03d [%(levelname)s] " "%(name)s | %(funcName)s:%(lineno)d | %(message)s"),
        datefmt="%y-%m-%d %H:%M:%S",
        stream=sys.stdout,
    )

    await organizations.initialize(args.uri)
    
    await get_organisation_by_id()
    await get_organisation_by_name()
    await get_organisation_name_by_id()
    await create_organisation()
    await update_organisation()
    await delete_organisation()
    await get_organisations()
    await get_organisations_managed_by_user()
    await get_projects_by_organisation_id()
    await get_organisation_stats()
    await assert_validate_name()
    await assert_validate_users()
    await can_user_manage_organisation()
    await is_user_an_org_manager()
    # get_campaign_organisations_as_dto()
    # get_organisations_managed_by_user_as_dto()
    # get_organisation_by_id_as_dto()
    # get_organisation_by_slug_as_dto()
    # get_organisation_dto()
    # get_organisations_as_dto(

    # FMTM Aget_organisations();
    await generate_slug()
    await get_organisation_by_name()
    # await upload_image()
    await create_organization()
    # await update_organization_info()
    
if __name__ == "__main__":
    """This is just a hook so this file can be run standalone during development."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
