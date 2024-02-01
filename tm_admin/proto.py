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

# Instantiate logger
log = logging.getLogger(__name__)

import tm_admin as tma
rootdir = tma.__path__[0]

class ProtoBuf(object):
    def __init__(self,
                sqlfile: str = None,
                ):
        """
        A class that generates protobuf files from the config data.

        Returns:
            (ProtoBuf): An instance of this class
        """
        self.sqlfile = sqlfile

    def createEnumProto(self,
                    enums: dict,
                    ):
        """
        Process a list of enums into the protobuf version.

        Args:
            enums (dict): The list of tables to generate a protobuf for.

        Returns:
            (list): The list of enums in protobuf format
        """
        out = list()
        out.append(f"syntax = 'proto3';")
        for name, value in enums.items():
            index = 0
            out.append(f"enum {name.capitalize()} {{")
            for entry in value:
                out.append(f"\t{entry} = {index};")
                index += 1
            out.append('};')

        return out

    def createTableProto(self,
                    tables: list,
                    ):
        """
        Process a list of tables into the protobuf version.

        Args:
            tables (list): The list of tables to generate a protobuf for.

        Returns:
            (list): The list of tables in protobuf format
        """
        out = list()
        out.append(f"syntax = 'proto3';")
        # types.proto is generated from the types.yaml file.
        # out.append("import 'types_tm.proto';")
        out.append("package tmadmin;")
        out.append("import 'types_tm.proto';")
        out.append("import 'google/protobuf/timestamp.proto';")

        convert = {'timestamp': "google.protobuf.Timestamp",
                   'polygon': 'bytes', 'point': 'bytes'}
        for table in tables:
            index = 1
            for key, value in table.items():
                out.append(f"message {key} {{")
                optional = ""
                repeated = ""
                # print(f"VALUE: {value}")
                for data in value:
                    #if type(data) == str:
                    #    log.warning(f"ENUM: {data}")
                    #    continue
                    for entry, settings in data.items():
                        # print(f"DATA: {entry} = {settings}")
                        #    datatype = settings[0][7:].capitalize()
                        share = False
                        array = ""
                        datatype = None
                        required = ""
                        optional = ""
                        for item in settings:
                            if type(item) == str:
                                # print(f"DATA: {item}")
                                if item[:15] == 'public.geometry':
                                    datatype = "bytes"
                                elif item[:7] == 'public.':
                                    datatype = item[7:].capitalize()
                                elif item in convert:
                                    datatype = convert[item]
                                else:
                                    datatype = item
                                continue
                            if type(item) == dict:
                                [[k, v]] = item.items()
                                if k == 'required' and v:
                                    required = k
                                if k == 'optional' and v:
                                    optional = k
                                if k == 'share':
                                    share = True
                                if k == 'array':
                                    array = "repeated"
                        if not share:
                            continue
                        # out.append(f"\t{required} {optional} {datatype} {entry} = {index};")
                        out.append(f"\t {array} {optional} {datatype} {entry} = {index};")
                        index += 1
            out.append(f"}}")

        return out

def main():
    """This main function lets this class be run standalone by a bash script."""
    parser = argparse.ArgumentParser(
        prog="config",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Manage the postgres database for the tm-admin project",
        epilog="""
        This should only be run standalone for debugging purposes.
        """,
    )
    parser.add_argument("-v", "--verbose", nargs="?", const="0", help="verbose output")
    args, known = parser.parse_known_args()

    if len(argv) <= 1:
        parser.print_help()
        # quit()

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

    tm = ProtoBuf()
    for table in known:
        out1, out2 = tm.createProtoFromSQL(table)
        name = table.replace('.sql', '.proto')
        # pyfile = table.replace('.sql', '.py')
        # xx = tm.protoToDict(name)
        # name = table.replace('.yaml', '.proto')
        out = tm.createTableProto()
        if len(out1) > 0:
            with open(name, 'w') as file:
                file.writelines([str(i)+'\n' for i in out1])
                file.close()
        if len(out2) > 0:
            with open(name, 'w') as file:
                file.writelines([str(i)+'\n' for i in out2])
                file.close()
        log.info(f"Wrote {name} to disk")

if __name__ == "__main__":
    """This is just a hook so this file can be run standalone during development."""
    main()
