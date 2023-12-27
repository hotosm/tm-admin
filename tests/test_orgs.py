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

def get_organisation_by_id():
    log.debug(f"--- get_organisation_by_id() ---")
    # organisation_id: int) -> Organisation:
    id = 1
    # all = user.getByID(id)
    result = organization.getByWhere(f" id='{id}'")
    assert len(result) > 0

def get_organisation_by_name():
    # organisation_name: str) -> Organisation:
    log.debug(f"--- get_organisation_by_name() ---")
    name= 'Other'
    result = organization.getByWhere(f" name='{name}'")
    assert len(result) > 0

def get_organisation_name_by_id():
    # organisation_id: int) -> str:
    log.debug(f"--- get_organisation_name_by_id() ---")
    id = 1
    result = organization.getByWhere(f" id='{id}'")
    assert len(result) > 0 and result[0][0]['name'] == 'Other'

def get_organisations():
    # manager_user_id: int):
    log.debug(f"--- get_organisations() ---")
    result = organization.getAll()
    assert len(result) > 0

def delete_organisation():
    # organisation_id: int):
    log.debug(f"delete_organisation() unimplemented!")
    id = 1
    #result = organization.deleteByID(id)
    #assert len(result) > 0

def create_organisation():
    # new_organisation_dto: NewOrganisationDTO) -> int:
    log.debug(f"create_organisation() unimplemented!")
    pass

def update_organisation():
    # organisation_dto: UpdateOrganisationDTO) -> Organisation:
    log.debug(f"update_organisation() unimplemented!")
    pass

def get_organisations_managed_by_user():
    # user_id: int):
    log.debug(f"get_organisations_managed_by_user() unimplemented!")
    pass

def get_projects_by_organisation_id():
    # organisation_id: int) -> Organisation:
    log.debug(f"get_projects_by_organisation_id() unimplemented!")
    pass

def get_organisation_stats():
    #
    log.debug(f"get_organisation_stats() unimplemented!")
    pass

def assert_validate_name():
    # org: Organisation, name: str):
    log.debug(f"assert_validate_name() unimplemented!")
    pass

def assert_validate_users():
    # organisation_dto: OrganisationDTO):
    log.debug(f"assert_validate_users() unimplemented!")
    pass

def can_user_manage_organisation():
    # organisation_id: int, user_id: int):
    log.debug(f"can_user_manage_organisation() unimplemented!")
    pass

def is_user_an_org_manager():
    # organisation_id: int, user_id: int):
    log.debug(f"is_user_an_org_manager() unimplemented!")
    pass

# We don't need to test these they are for sqlachemy, which we're not using. Instead
# we use the UsersTable() to represent the table schema
# def get_organisation_dto():
# def get_organisations_managed_by_user_as_dto():
# def get_organisations_as_dto():
# def get_campaign_organisations_as_dto():
# def get_organisation_by_id_as_dto():
# def get_organisation_by_slug_as_dto():


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

    get_organisation_by_id()
    get_organisation_by_name()
    get_organisation_name_by_id()
    create_organisation()
    update_organisation()
    delete_organisation()
    get_organisations()
    get_organisations_managed_by_user()
    get_projects_by_organisation_id()
    get_organisation_stats()
    assert_validate_name()
    assert_validate_users()
    can_user_manage_organisation()
    is_user_an_org_manager()
    # get_campaign_organisations_as_dto()
    # get_organisations_managed_by_user_as_dto()
    # get_organisation_by_id_as_dto()
    # get_organisation_by_slug_as_dto()
    # get_organisation_dto()
    # get_organisations_as_dto(
