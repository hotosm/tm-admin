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
from sys import argv
#from __future__ import print_function
import grpc

import tm_admin.services_pb2
import tm_admin.services_pb2_grpc
import tm_admin.types_pb2
import tm_admin.types_pb2_grpc
import tm_admin.users.users_pb2
import tm_admin.users.users_pb2_grpc
from tm_admin.yamlfile import YamlFile

# Instantiate logger
log = logging.getLogger("tm-admin")

import tm_admin as tma
rootdir = tma.__path__[0]

class TMClient(object):
    def __init__(self,
                target: str,
                ):
        self.hosts = YamlFile(f"{rootdir}/services.yaml")
        target = self.getTarget(target)
        [[host, port]] = target.items()
        self.hosts = YamlFile(f"{rootdir}/services.yaml")
        channel = grpc.insecure_channel(f"{host}:{port}")
        stub = tm_admin.services_pb2_grpc.TMAdminStub(channel)
        response = stub.SayHello(tm_admin.services_pb2.HelloRequest(name='you'))
        print(f"TMAdmin client received: {response}")

    def getTarget(self,
                target: str,
                ):
        return self.hosts.yaml[0][target][0]
    
def main():
    """This main function lets this class be run standalone by a bash script."""
    parser = argparse.ArgumentParser(
        prog="tmclient",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="gRPC Client",
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

    tm = TMClient('test')

    # target = tm.getTarget('test')
    # [[host, port]] = target.items()
    # channel = grpc.insecure_channel(f"{host}:{port}")
    # stub = tm_admin.services_pb2_grpc.TMAdminStub(channel)
    # response = stub.SayHello(tm_admin.services_pb2.HelloRequest(name='you'))
    # print(f"TMAdmin client received: {response}")

if __name__ == "__main__":
    """This is just a hook so this file can be run standalone during development."""
    main()
