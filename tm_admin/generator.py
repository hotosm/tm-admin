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
from tm_admin.proto import ProtoBuf
from datetime import datetime

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
        self.yaml2py = {'int32': 'int',
                    'int64': 'int',
                    'bool': 'bool',
                    'string': 'str',
                    'bytes': 'bytes',
                    'timestamp': '',
                    }
        

    def readConfig(self,
                    filespec: str,
                    ):
        self.filespec = Path(filespec)
        self.yaml = YamlFile(filespec)

    def createTypes(self):
        gen = self.readConfig(f'{rootdir}/types.yaml')
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
            out = out[:-2]
            out += "\n);\n"
        return out

    def createProtoEnums(self):
        out = "syntax = 'proto3';\n\n"
        for entry in self.yaml.yaml:
            index = 0
            [[table, values]] = entry.items()
            out += f"enum {table.capitalize()} {{\n"
            for line in values:
                out += f"\t{line} = {index};\n"
                index += 1
            out += "};\n\n"
        return out

    def createPyEnums(self):
        out = f"import logging\n"
        out += f"from enum import Enum\n"
        for entry in self.yaml.yaml:
            index = 1
            [[table, values]] = entry.items()
            out += f"class {table.capitalize()}(Enum):\n"
            for line in values:
                out += f"\t{line} = {index}\n"
                index += 1
            out += '\n'
        return out

    def createPyMessage(self):
        out = f"""
import logging
from datetime import timedelta

log = logging.getLogger("tm-admin")
        """
        for entry in self.yaml.yaml:
            [[table, settings]] = entry.items()
            out += f"""
class {table.capitalize()}Message(object):
    def __init__(self, 
            """
            # print(table, settings)
            share = False
            datatype = None
            data = "        self.data = {"
            for item in settings:
                if type(item) == dict:
                    [[k, v]] = item.items()
                    for k1 in v:
                        if type(k1) == dict:
                            [[k2, v2]] = k1.items()
                            if k2 == 'share' and v2:
                                share = True
                                # out += f"\nshare {k1}"
                        elif type(k1) == str:
                            if k1 in self.yaml2py:
                                datatype = self.yaml2py[k1]
                            else:
                                datatype = item
                                continue
                    if share:
                        share = False
                        out += f"{k}: {datatype} = None, "
                        data += f"'{k}': {k}, "
        out += "):\n"
        out += f"{data[:-2]}}}\n"

        return out

    def createPyClass(self):
        out = f"""
import logging
from datetime import datetime
import tm_admin.types_tm

log = logging.getLogger("tm-admin")

        """
        for entry in self.yaml.yaml:
            [[table, settings]] = entry.items()
            out += f"""
class {table.capitalize()}Table(object):
    def __init__(self, 
            """
            datatype = None
            now = datetime.now()
            data = "            self.data = {"
            for item in settings:
                if type(item) == dict:
                    [[k, v]] = item.items()
                    for k1 in v:
                        if type(k1) == dict:
                            continue
                        elif type(k1) == str:
                            if k1[:7] == 'public.':
                                # FIXME: It's in the SQL types
                                log.warning(f"SQL ENUM {k1}!")
                                datatype = k1[7:].capitalize()
                            elif k1 in self.yaml2py:
                                datatype = self.yaml2py[k1]
                            else:
                                datatype = item
                                continue
                        if k1 == 'bool':
                            out += f"{k}: {datatype} = False, "
                        elif k1 == 'timestamp':
                            out += f"{k}: datetime = '{datetime.now()}', "
                        elif k1[:7] == 'public.':
                            # defined = f"tm_admin.types_tm.{k1[7:].capitalize()}()"
                            # out += f"{k}: {defined} =  1, "
                            out += f"{k}: int =  1, "
                        else:
                            out += f"{k}: {datatype} = None, "
                        # print(k)
                        data += f"'{k}': {k}, "
        out = out[:-2]
        out += "):\n"
        out += f"{data[:-2]}}}\n"

        return out
    
    def createProtoMessage(self):
        pb = ProtoBuf()
        out = pb.createTableProto(self.yaml.yaml)
        return out

    def createSQLTable(self):
        out = "-- Do not edit this file, it's generated from the yaml file\n\n"
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
            unique = ""
            typedef = ""
            for line in values:
                # these are usually from the types.yaml file, which have no
                # settings beyond the enum value.
                # if type(line) == str:
                #     print(f"SQL TABLE: {typedef} {line}")
                #     typedef = table
                #     continue
                [[k, v]] = line.items()
                required = ""
                array = ""
                public = False
                primary = ""
                for item in v:
                    if type(item) == dict:
                        if 'sequence' in item and item['sequence']:
                            sequence.append(k)
                            primary = k
                        if 'required' in item and item['required']:
                            required = ' NOT NULL'
                        if 'array' in item and item['array']:
                            array = "[]"
                        if 'unique' in item and item['unique']:
                            unique = k
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
            if len(unique) > 0:
                out += f"\tUNIQUE({unique})\n);\n"

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
    for config in known:
        gen.readConfig(config)
        out = gen.createSQLTable()
        sqlfile = config.replace('.yaml', '.sql')
        path = Path(sqlfile)
        #if path.exists():
        #    path.rename(file.replace('.sql', '_bak.sql'))
        with open(sqlfile, 'w') as file:
            file.write(out)
            log.info(f"Wrote {sqlfile} to disk")
            file.close()
        proto = config.replace('.yaml', '.proto')
        out = gen.createProtoMessage()
        with open(proto, 'w') as file:
            file.writelines([str(i)+'\n' for i in out])
            log.info(f"Wrote {proto} to disk")
            file.close()

        out = gen.createPyClass()
        py = config.replace('.yaml', '_class.py')
        with open(py, 'w') as file:
            file.write(out)
            log.info(f"Wrote {py} to disk")
            file.close()
        # print(out)
        out = gen.createPyMessage()
        py = config.replace('.yaml', '_proto.py')
        with open(py, 'w') as file:
            file.write(out)
            log.info(f"Wrote {py} to disk")
            file.close()
        # print(out)
        
if __name__ == "__main__":
    """This is just a hook so this file can be run standalone during development."""
    main()
