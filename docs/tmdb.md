# tmdb.py

This program imports existing data from the HOT Tasking Manager into
this modified database schema.

	usage: tmclient [-h] [-v [VERBOSE]] [-i INURI] [-o OUTURI] -t TABLE

	options:
		-h, --help                 show this help message and exit
		-v, --verbose              verbose output
		-i INURI, --inuri INURI    The URI string for the TM database
		-o OUTURI, --outuri OUTURI The URI string for the TM Admin database
		-t TABLE, --table TABLE    The table to import into

## example

For example, this command will import the data for the messages table,
from the datbase *localhost/tm4" into the datbase
*localhost/tm_admin*.

	./tmdb.py -v -i localhost/tm4 -o localhost/tm_admin -t messages
