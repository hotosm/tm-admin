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
from pathlib import Path
from sys import argv
from osm_rawdata.postgres import uriParser, PostgresClient
from  protobuf_serialization import serialize_to_protobuf, protobuf_to_dict
from concurrent import futures
# from threading import Lock
import time
import grpc
from grpc_reflection.v1alpha import reflection
from tm_admin.yamlfile import YamlFile

import tm_admin.services_pb2
import tm_admin.services_pb2_grpc
# import tm_admin.types_tm_pb2
# import tm_admin.types_tm_pb2_grpc
import tm_admin.users.users_pb2_grpc
from tm_admin.users.users_pb2 import users
from tm_admin.teams.teams_pb2 import teams
from tm_admin.users.users_pb2 import users
from tm_admin.organizations.organizations_pb2 import organizations
from tm_admin.tasks.tasks_proto import TasksMessage
from tm_admin.teams.teams_proto import TeamsMessage
from tm_admin.users.users_proto import UsersMessage
from tm_admin.organizations.organizations_proto import OrganizationsMessage
from tm_admin.projects.projects_proto import ProjectsMessage
from tm_admin.types_tm import Command, Notification


# Instantiate logger
log = logging.getLogger(__name__)

import tm_admin as tma
rootdir = tma.__path__[0]

# semaphore = Lock()

class RequestServicer(tm_admin.services_pb2_grpc.TMAdminServicer):
    def doRequest(self, request, context):
        action = protobuf_to_dict(request)

        if action['cmd'] == Command.GET_USER:
            print("USER")
        elif action['cmd'] == Command.GET_ORG:
            print("ORG")
        elif action['cmd'] == Command.GET_PROJECT:
            print("PROJECT")
        elif action['cmd'] == Command.GET_TEAM:
            print("TEAM")
        bar = {'one': 1, 'two': 2}
        foo = {'error_code': 1, 'error_msg':'nothing'}
        foobar = serialize_to_protobuf(foo, tm_admin.services_pb2.tmresponse)
        foobar.data['one'] = '1'
        foobar.data['two'] = '2'
        # print(f"FOOBAR: {foobar}")
        # bar = tm_admin.services_pb2.tmresponse(error_code=0, error_msg="none")
        return(foobar)

    def GetUserRequest(self, request, context):
        foo = protobuf_to_dict(request)

        xx = response()
        # foobar = serialize_to_protobuf(foo, tm_admin.users.users_pb2.users)
        print(f"FOOBAR: {foobar}")
        bar = tm_admin.services_pb2.response(**foo)
        return(bar)

    def GetProjectRequest(self, request, context):
        foo = protobuf_to_dict(request)

        # foobar = serialize_to_protobuf(foo, tm_admin.users.users_pb2.users)
        # print(f"FOOBAR: {foobar}")
        bar = tm_admin.projects.projects_pb2(**foo)
        return(bar)

        # return tm_admin.services_pb2.HelloReply(
        #     message="Hello, {}!".format(request.name), id=3,
        # )

    def GetTeamRequest(self, request, context):
        foo = protobuf_to_dict(request)

        # foobar = serialize_to_protobuf(foo, tm_admin.users.users_pb2.users)
        # print(f"FOOBAR: {foobar}")
        bar = tm_admin.teams.teams_pb2.users(**foo)
        return(bar)

    def GetOrganizationRequest(self, request, context):
        foo = protobuf_to_dict(request)

        # foobar = serialize_to_protobuf(foo, tm_admin.users.users_pb2.users)
        # print(f"FOOBAR: {foobar}")
        bar = tm_admin.organizations.organizations_pb2.users(**foo)
        return(bar)

    # These methods get a user profile, and add it to the database
    def GetUserProfile(self, users, context):
        foo = protobuf_to_dict(request)

        # foobar = serialize_to_protobuf(foo, tm_admin.users.users_pb2.users)
        # print(f"FOOBAR: {foobar}")
        bar = tm_admin.users.users_pb2.users(**foo)
        return(bar)

    def GetProjectProfile(self, projects, context):
        foo = protobuf_to_dict(request)

        # foobar = serialize_to_protobuf(foo, tm_admin.users.users_pb2.users)
        # print(f"FOOBAR: {foobar}")
        bar = tm_admin.projects.projects_pb2.users(**foo)
        return(bar)

    def GetTeamProfile(self, teams, context):
        foo = protobuf_to_dict(request)

        # foobar = serialize_to_protobuf(foo, tm_admin.users.users_pb2.users)
        # print(f"FOOBAR: {foobar}")
        bar = tm_admin.teams.teams_pb2.users(**foo)
        return(bar)

    def GetOrganizationProfile(self, teams, context):
        foo = protobuf_to_dict(request)

        # foobar = serialize_to_protobuf(foo, tm_admin.users.users_pb2.users)
        # print(f"FOOBAR: {foobar}")
        bar = tm_admin.organizations.organizations_pb2.users(**foo)
        return(bar)

        
# class _{ProjectServicer(route_guide_pb2_grpc.RouteGuideServicer):
#     """Provides methods that implement functionality of route guide server."""


#         self.db = route_guide_resources.read_route_guide_database()

class TMServer(object):
    def __init__(self,
                 target: str,
                 ):
        """
        Instantiate a server

        Args:
            target (str): The name of the target program

        Returns:
            (TMServer): An instance of this class
        """
        self.hosts = YamlFile(f"{rootdir}/services.yaml")
        log.debug("Starting server")
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        tm_admin.services_pb2_grpc.add_TMAdminServicer_to_server(
            RequestServicer(), server
        )
        # Enable reflection for grpc_cli
        SERVICE_NAMES = (
            tm_admin.services_pb2.DESCRIPTOR.services_by_name['TMAdmin'].full_name,
            reflection.SERVICE_NAME,
        )
        reflection.enable_server_reflection(SERVICE_NAMES, server)

        target = self.getTarget(target)
        [[host, port]] = target.items()
        # FIXME: this needs to use SSL for a secure connection
        server.add_insecure_port(f"[::]:{port}")
        server.start()
        server.wait_for_termination()

    def getTarget(self,
                target: str,
                ):
        """
        Get the target hostname and IP port number

        Args:
            target (str): The name of the target program

        Returns:
            (dict): the hostname and IP port for this target program
        """
        return self.hosts.yaml[0][target][0]

def main():
    """This main function lets this class be run standalone by a bash script."""
    parser = argparse.ArgumentParser(
        prog="tmserver",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Server for gRPC communication",
        epilog="""
        This should only be run standalone for debugging purposes.
        """,
    )
    parser.add_argument("-v", "--verbose", nargs="?", const="0", help="verbose output")

    args = parser.parse_args()

    # if len(argv) <= 1:
    #     parser.print_help()
    #     quit()

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

    # This blocks till  this process is killed
    tm = TMServer('test')

if __name__ == "__main__":
    """This is just a hook so this file can be run standalone during development."""
    main()
