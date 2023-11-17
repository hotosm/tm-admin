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
from pathlib import Path
from tm_admin.yamlfile import YamlFile

# Instantiate logger
log = logging.getLogger("tm-admin")

import tm_admin as tma
rootdir = tma.__path__[0]

class Generator(object):
    def __init__(self,
                filespec: str = None,
                ):
        self.filespec = None
        self.yaml = None
        if filespec:
            self.filespec = Path(filespec)
            self.yaml = YamlFile(filespec)
        self.createTypes()

    def readConfig(self,
                    filespec: str,
                    ):
        self.filespec = Path(filespec)
        self.yaml = YamlFile(filespec)

    def createTypes(self):
        gen = self.readConfig(f'types.yaml')
        out = self.createSQLEnums()
        with open('types_tm.sql', 'w') as file:
            file.write(out)
        out = self.createProtoEnums()
        with open('types_tm.proto', 'w') as file:
            file.write(out)
        out = self.createPyEnums()
        with open('types_tm.py', 'w') as file:
            file.write(out)

    def createSQLEnums(self):
        out = ""
        for entry in self.yaml.yaml:
            [[table, values]] = entry.items()
            out += f"DROP TYPE IF EXISTS public.{table} CASCADE;\n"
            out += f"CREATE TYPE public.{table} AS ENUM (\n"
            for line in values:
                out += f"\t'{line}',\n"
            out += ");\n"
        return out

    def createProtoEnums(self):
        out = "syntax = 'proto3';\n\n"
        for entry in self.yaml.yaml:
            index = 1
            [[table, values]] = entry.items()
            out += f"enum {table.capitalize()} {{\n"
            for line in values:
                out += f"\t{line} = {index};\n"
                index += 1
            out += "};\n\n"
        return out

    def createPyEnums(self):
        out = f"from enum import Enum\n"
        for entry in self.yaml.yaml:
            index = 1
            [[table, values]] = entry.items()
            out += f"class {table.capitalize()}(Enum):\n"
            for line in values:
                out += f"\t{line} = {index}\n"
                index += 1
            out += '\n'
        return out

    def createProtoTable(self):
        out = list()
        out.append("'syntax = 'proto3';'")
        out.append("import 'types.proto';")
        for entry in self.yaml.yaml:
            [[table, values]] = entry.items()
            out += f"message {table} {{"
            for line in values:
                print(line)
                [[k, v]] = line.items()
                required = ""
                array = ""
                public = False
                if type(v) == bool:
                    if k == 'Sequence' and v:
                        sequence = True
                        continue
                for item in v:
                    print(item)
                    if type(item) == dict:
                        if 'required' in item and item['required']:
                            required = ' NOT NULL'
                        if 'array' in item and item['array']:
                            array = "repeated"
                    if type(item) == str:
                        if item[:7] == 'public.':
                            public = True
                    if len(v) >= 2:
                        if 'required' in v[1] and v[1]['required']:
                            required = ' NOT NULL'

        return out

    def createSQLTable(self):
        out = ""
        convert = {'int32': 'integer',
                   'int64': 'bigint',
                   'bool': 'boolean',
                   'string': 'character varying',
                   'bytes': 'bytea',
                   'timestamp': 'timestamp without time zone',
                   }
        sequence = list()
        for entry in self.yaml.yaml:
            [[table, values]] = entry.items()
            out += f"DROP TABLE IF EXISTS public.{table} CASCADE;\n"
            out += f"CREATE TABLE public.{table} (\n"
            for line in values:
                [[k, v]] = line.items()
                required = ""
                array = ""
                public = False
                for item in v:
                    if type(item) == dict:
                        if 'sequence' in item and item['sequence']:
                            sequence.append(k)
                        if 'required' in item and item['required']:
                            required = ' NOT NULL'
                        if 'array' in item and item['array']:
                            array = "[]"
                    if type(item) == str:
                        if item[:7] == 'public.':
                            public = True
                    if len(v) >= 2:
                        if 'required' in v[1] and v[1]['required']:
                            required = ' NOT NULL'
                if public:
                    out += f"\t{k} {v[0]}{array}{required},\n"
                else:
                    out += f"\t{k} {convert[v[0]]}{array}{required},\n"
            out = out[:-2]
            out += "\n);\n"

            if len(sequence) > 0:
                for key in sequence:
                    out += f"""
DROP SEQUENCE IF EXISTS public.users_{key}_seq CASCADE;
CREATE SEQUENCE public.users_{key}_seq
        START WITH 1
        INCREMENT BY 1
        NO MINVALUE
        NO MAXVALUE
        CACHE 1;
"""
        return out
    
def main():
    """This main function lets this class be run standalone by a bash script."""
    parser = argparse.ArgumentParser(
        prog="generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Generate SQL, Protobuf, and Python data structures",
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

    gen = Generator()
    for file in known:
        path = Path(file)
        gen.readConfig(file)
        out = gen.createSQLTable()
        with open('foo.sql', 'w') as file:
            file.write(out)
        print(out)

if __name__ == "__main__":
    """This is just a hook so this file can be run standalone during development."""
    main()
    