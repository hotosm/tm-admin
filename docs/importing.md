# Importing Tasking Manager Data

It is possible to import the entire database from an existing Tasking
Manager (TM) into the new schema.  This should only need to be done
once if transitioning to using *tm-admin* as the backend for TM. It is
also useful for development, as their is no better way to make sure
tm-admin can support the backend needs of a Tasking Manager style
project.

# The Initial Import

The TM [database
schema](https://hotosm.github.io/tasking-manager/developers/tmschema/)
uses small two column tables to relate various IDs together using a
postgre SQL. This is inefficient, tm-admin uses postgres arrays and
nested tables instead to limit doing multiple queires in sequency to
get simple results from the initial query.

The primary tables are:

* tasks
* users
* projects
* organizations
* campaigns
* teams
* messages
* notifications

Changes between the TM schema and the one used by tm-admin are
documented [here](schema.md).

[tmdb.py](tmdb.md)

# Importing The Supplementary Tables

Each directory has a python file that will read the data from a TM
database table, but for tm-admin, it gets merged in as either an array
or a nested table.

* users
* projects
* tasks
