# Code Structure

This document is only of use to people considering being part of our
development community.

# Code walkthrough

This is a short description of the file layout for this project.

## The Top Level

The top level directory mostly has subdirectories where all the work
is done, so this is mostly project management files, like python
packaging.

The primary directories are:

* main/tests - Which contains all the test cases
* main/docs - Which contains all the documentation
* main/tm_admin - Which contains all of the code.

## Makefiles

Some directories have a Makefile. This is for automating tasks used by
developers. This is common for generating documentation or the other
files this project creates. Since Makefiles do dependency tracking, it
reduces the amount of files that hace to be regenerated after a
change.

## Generated Files

This project supports multiple language bindings. These are all
configured by the YAML based confg file that defines the data
structures. The *generator.py* program creates the output files from
the config file. These

For example for the users table:

* users_class.py - A class that defines the data as a dictionary
* users.proto.py - The protobuf file for gRPC
* users_proto.py - A class for accessing protobuf messages
	
## Adding A Table

To add a new database table, create the directory for it, and then
create the following 3 files. Rename *foo* of course.

	tm_admin/foo/
		-> api.py
		-> foo.py
		-> foo.yaml

The *foo.yaml* file defines the data structure for accessing the
database. It is required when adding a new table. The *foo.py* is the
one that defines the *FooDB* class, which is the glue between postgres
and this project. The *FooDB* class contains code for direct table
management within the database.

The *api.py* files ia an API for accessing the database for Tasking
Manager style projects. This can be incorporated into a FastAPI or
Flask backend.

## Testing

All the test cases in the *tests* directory can be run standalone
while debugging them, or via *pytest* for github. Note that all test
cases must support the asyncio API used in the rest of the code.

## API Support

Each table directory contains an *api.py* files, which is support code
for a website backend. This lets the queries used to support the front
end share code with the testsuite.
