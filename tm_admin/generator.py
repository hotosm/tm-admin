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
                filespec: str = f"{rootdir}/types.yaml",
                ):
        self.filespec = Path(filespec)
        self.yaml = YamlFile(filespec)

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
        out = "syntax = 'proto3';"
        for entry in self.yaml.yaml:
            index = 1
            [[table, values]] = entry.items()
            out += f"enum {table.capitalize()} {{\n"
            for line in values:
                out += f"\t{line} = {index};\n"
                index += 1
            out += "};\n\n"
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
        # quit()

    # if verbose, dump to the terminal.
    if args.verbose is not None:
        log.setLevel(logging.DEBUG)
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(threadName)10s - %(name)s - %(levelname)s - %(message)s")
        ch.setFormatter(formatter)
        log.addHandler(ch)

    gen = Generator()
    # out = gen.createSQLEnums()
    out = gen.createProtoEnums()
    print(out)

if __name__ == "__main__":
    """This is just a hook so this file can be run standalone during development."""
    main()
    
