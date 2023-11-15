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
from pathlib import Path
from sys import argv
from osm_rawdata.postgres import uriParser, PostgresClient
from concurrent import futures
from threading import Lock
import time
import grpc
from grpc_reflection.v1alpha import reflection
from tm_admin.yamlfile import YamlFile

import tm_admin.services_pb2
import tm_admin.services_pb2_grpc
import tm_admin.types_pb2
import tm_admin.types_pb2
import tm_admin.types_pb2_grpc
import tm_admin.users.users_pb2
import tm_admin.users.users_pb2_grpc

# Instantiate logger
log = logging.getLogger("tm-admin")

import tm_admin as tma
rootdir = tma.__path__[0]

semaphore = Lock()

class _UserServicer(tm_admin.services_pb2_grpc.TMAdminServicer):
    def SayHello(self, request, context):
        return tm_admin.services_pb2.HelloReply(
            message="Hello, {}!".format(request.name)
        )
    
# class _{ProjectServicer(route_guide_pb2_grpc.RouteGuideServicer):
#     """Provides methods that implement functionality of route guide server."""

#     def __init__(self):
#         self.db = route_guide_resources.read_route_guide_database()


class TMServer(object):
    def __init__(self,
                 target: str,
                 ):
        self.hosts = YamlFile(f"{rootdir}/services.yaml")
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        tm_admin.services_pb2_grpc.add_TMAdminServicer_to_server(
            _UserServicer(), server
        )
        # route_guide_pb2_grpc.add_RouteGuideServicer_to_server(
        #     _RouteGuideServicer(), server
        # )
        SERVICE_NAMES = (
            tm_admin.services_pb2.DESCRIPTOR.services_by_name['TMAdmin'].full_name,
            reflection.SERVICE_NAME,
        )
        reflection.enable_server_reflection(SERVICE_NAMES, server)

        target = self.getTarget(target)
        [[host, port]] = target.items()
        server.add_insecure_port(f"[::]:{port}")
        server.start()
        server.wait_for_termination()

    def getTarget(self,
                target: str,
                ):
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

    if len(argv) <= 1:
        parser.print_help()
        # quit()

    # if verbose, dump to the terminal.
    if args.verbose is not None:
        log.setLevel(logging.DEBUG)
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(threadName)10s - %(name)s - %(levelname)s - %(message)s")
        ch.setFormatter(formatter)
        log.addHandler(ch)

    tm = TMServer('test')

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    tm_admin.services_pb2_grpc.add_TMAdminServicer_to_server(
        _UserServicer(), server
    )
    # route_guide_pb2_grpc.add_RouteGuideServicer_to_server(
    #     _RouteGuideServicer(), server
    # )
    SERVICE_NAMES = (
        tm_admin.services_pb2.DESCRIPTOR.services_by_name['TMAdmin'].full_name,
        reflection.SERVICE_NAME,
    )
    # reflection.enable_server_reflection(SERVICE_NAMES, server)
    # server.add_insecure_port("[::]:50051")
    # server.start()
    # server.wait_for_termination()

if __name__ == "__main__":
    """This is just a hook so this file can be run standalone during development."""
    main()
