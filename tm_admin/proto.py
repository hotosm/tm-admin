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
log = logging.getLogger("tm-admin")

import tm_admin as tma
rootdir = tma.__path__[0]

class ProtoBuf(object):
    def __init__(self,
                sqlfile: str = None,
                ):
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
            table (list): The list of tables to generate a protobuf for.

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

        convert = {'timestamp': "google.protobuf.Timestamp"}
        for table in tables:
            index = 1
            for key, value in table.items():
                out.append(f"message {key} {{")
                optional = ""
                repeated = ""
                for data in value:
                    #print(f"DATA: {data}")
                    for entry, settings in data.items():
                        # print(f"DATA: {entry} = {settings}")
                        # print(f"DATA: {entry} = {settings}")
                        #    datatype = settings[0][7:].capitalize()
                        share = False
                        array = ""
                        datatype = None
                        required = ""
                        optional = ""
                        for item in settings:
                            if type(item) == str:
                                #print(f"DATA: {item}")
                                if item[:7] == 'public.':
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

    def protoToDict(self,
                    filespec: str,
                    ):
        inblock = False
        array = False
        dataout = dict()
        convert = {'int32': 'int', 'int64': 'long', 'string': 'str'}
        with open(filespec, 'r') as file:
            for line in file.readlines():
                if line[:6] == 'syntax' or line[:6] == 'import' or line[:2] == '//':
                    continue
                elif line[0] == '}':
                    inblock = False
                    continue
                elif line[:7] == 'message':
                    name = line.strip().split(' ')[1]
                    inblock = True
                    continue
                elif inblock:
                    keyword = None
                    datatype = None
                    tmp = line.strip().split(' ')
                    if tmp[0] == 'repeated':
                        array = True
                        datatype = tmp[1]
                        keyword = tmp[2]
                    elif tmp[0] == 'optional':
                        datatype = tmp[1]
                        keyword = tmp[2]
                    else:
                        datatype = tmp[0]
                        keyword = tmp[1]
                    
                    dataout[keyword] = None
                    
        return dataout

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
    if args.verbose is not None:
        log.setLevel(logging.DEBUG)
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(threadName)10s - %(name)s - %(levelname)s - %(message)s")
        ch.setFormatter(formatter)
        log.addHandler(ch)

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
