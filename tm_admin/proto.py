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

    def convertType(self):
        pass
        # double
        # float
        # int32 (int)
        # int64 (long)
        # bool
        # bytes
        # string
    def createProto(self,
                    sqlfile: str,
                    ):
        """
        Read an SQL file and produce data to create protobuf .proto files.

        Args:
            sqlfile (str): The SQL file to process.

        Returns:
            (dict): The list of enums and types
            (dict): The list of tables
        """
        tables = dict()
        enums = dict()
        table = dict()
        log.info(f"Processing {sqlfile}...")
        with open(sqlfile, 'r') as file:
            inblock = False
            inenum = True
            nume = list()
            name = None
            for line in file.readlines():
                optional = ""
                repeated = ""
                # We don't care about the NOT NULL parameter
                loc = line.find('NOT')
                tmp = ' '.join(line[:loc].split()).split()
                # optional is for anything that is NOT NULL
                if loc > 0:
                    optional = "optional "
                if line[:2] == ");":
                    if inblock:
                        inblock = False
                        tables[name] = table
                        print(f"Done table {name}...")
                    elif inenum:
                        inenum = False
                        enums[name] = nume
                        print(f"Done enum {name}...")
                    continue
                if line[:12] == 'CREATE TABLE':
                    name = tmp[2].replace("public.", "")
                    inblock = True
                    continue
                if line[:11] == 'CREATE TYPE' and tmp[4] == 'ENUM':
                    name = tmp[2].replace("public.", "")
                    nume = list()
                    inenum = True
                    continue
                if len(tmp) == 2 and inblock:
                    table[tmp[0]] = tmp[1]
                    continue
                if len(tmp) == 3 and inblock:
                    if tmp[2][-1:] == ',':
                        table[tmp[0]] = f"{tmp[1]}_{tmp[2][:-1]}"
                    else:
                        table[tmp[0]] = f"{tmp[1]}_{tmp[2]}"
                    continue
                if len(tmp) == 1 and inenum:
                    if  tmp[0][-1:] == ',':
                        nume.append(f"{tmp[0][1:-2]}")
                    else:
                        nume.append(f"{tmp[0][1:-1]}")
                # Repeated is for arrays
                if line[:2] == "[]":
                    repeated = "repeated"

        out1 = self.createEnumProto(enums)
        out2 = self.createTableProto(tables)

        return out1, out2

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
                    tables: dict,
                    ):
        """
        Process a list of tables into the protobuf version.

        Args:
            table (dict): The list of tables to generate a protobuf for.

        Returns:
            (list): The list of tables in protobuf format
        """
        out = list()
        convert = {'integer': 'int32',
                   'bigint': 'int64',
                   'boolean': 'bool',
                   'character_varying': 'string',
                   'bytea': 'bytes',
                   }
        out.append(f"syntax = 'proto3';")
        out.append("import 'types.proto';")

        for name, value in tables.items():
            out.append(f"message {name} {{")
            index = 1
            for table, data in tables.items():
                optional = ""
                repeated = ""
                for k1, v1 in data.items():
                    # Remove any embedded commas
                    v1 = v1.replace(',', '')
                    # print(f"DATA: {k1} = {v1}")
                    if v1[:7] == 'public.':
                        # log.debug(f"Got enum '{k1}' from types.proto")
                        v1 = v1[7:].capitalize()
                        # out.append(f"\t{optional}  {v1} {k1} = {index};")
                    # FIXME: Sometimes this has a number for a fixed length string
                    elif v1[:17] == 'character_varying':
                        v1 = v1[:17]
                    # It's an array, ie.. repeated field
                    elif v1[-2:] == '[]':
                        # log.debug(f"Got an array for {k1}")
                        v1 = v1[:-2]
                        repeated = 'repeated'
                    # it's an enum defined in types.proto
                    if v1 not in convert:
                        if v1[:8] == 'Geometry':
                            # log.debug(f"Got a geometry for {k1}")
                            out.append(f"\t{optional}  bytes {k1} = {index};")
                    else:
                        out.append(f"\t{optional}  {repeated} {convert[v1]} {k1} = {index};")
                    index += 1
            out += f"}}";

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
        quit()

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
        out1, out2 = tm.createProto(table)
        name = table.replace('.sql', '.proto')
        pyfile = table.replace('.sql', '.py')
        # xx = tm.protoToDict(name)
        
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
