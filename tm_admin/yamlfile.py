#!/usr/bin/python3

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

import yaml

# Instantiate logger
log = logging.getLogger(__name__)

class YamlFile(object):
    """Config file in YAML format."""

    def __init__(
        self,
        filespec: str,
    ):
        """This parses a yaml file into a dictionary for easy access.

        Args:
            filespec (str): The filespec of the YAML file to read

        Returns:
            (YamlFile): An instance of this object
        """
        self.filespec = None
        # if data == str:
        self.filespec = filespec
        self.file = open(filespec, "rb").read()
        self.yaml = yaml.load(self.file, Loader=yaml.Loader)
        self.data = dict()

    def getEntries(self):
        """
        Convert the list from the YAML file into a searcable data structure
        """
        table = list(self.yaml[0].keys())[0]
        for entry in self.yaml[0][table]:
            for key, values in entry.items():
                self.data[key] = {'array': False, 'required': False, 'share': False}
                for item in values:
                    # The only values that's a string is the data type
                    if type(item) == str:
                        if item[:7] == 'public.':
                            self.data[key]['datatype'] = item[7:].capitalize()
                        else:
                            self.data[key]['datatype'] = item
                    else:
                        [[k, v]] = item.items()
                        self.data[key][k] = v

        return self.data
    
    def dump(self):
        """Dump internal data structures, for debugging purposes only."""
        if self.filespec:
            print("YAML file: %s" % self.filespec)
        for key, values in self.data.items():
            print(f"Key is: {key}")
            for k, v in values.items():
                print(f"\t{k} = {v}")
            print("------------------")

#
# This script can be run standalone for debugging purposes. It's easier to debug
# this way than using pytest,
#
if __name__ == "__main__":
    """This is just a hook so this file can be run standlone during development."""
    parser = argparse.ArgumentParser(description="Read and parse a YAML file")
    parser.add_argument("-v", "--verbose", action="store_true", help="verbose output")
    parser.add_argument("-i", "--infile", required=True, default="./xforms.yaml", help="The YAML input file")
    args, known = parser.parse_known_args()

    # if verbose, dump to the terminal.
    if args.verbose is not None:
        log.setLevel(logging.DEBUG)
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(threadName)10s - %(name)s - %(levelname)s - %(message)s")
        ch.setFormatter(formatter)
        log.addHandler(ch)

    yaml1 = YamlFile(args.infile)
    
    x = yaml1.getEntries()
    yaml1.dump()

    # table = ("nodes", "ways_poly")
    # where = ("building", "amenity", "shop", "tourism")
    # tmp = yaml1.write(table)
    # yaml2 = YamlFile(tmp)
    # yaml2.dump()
