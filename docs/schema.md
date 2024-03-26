# Changing The TM Admin Schema

This document covers how to make changes to the data schemas used in
TM Admin, and the changes that were made from the original Tasking
Manager (TM). The Field Mapping Tasking Manager (FMTM) database schema
was originally based on the TM schema, but doesn't use all the tables,
plus added columns. TM Admin has a unified schema that is designed to
work with any tasking manager style project.

# The configuration file

A simple YAML based config file is used as a single source for all the
data structures. This makes it easier to exchange data between
postgres, protobuf, and python. The format for configuring a schema is
explained in more detail in [this document](configuring.md). Any
changes to the config file are propogated into the different formats.

Updating the config file then requires regenerating all the output
files. After any changes to the config files, the test cases should be
run to make sure nothing breaks. If the config change is to support a
new internal API, then that new function should be added to the test
cases.

## Merging Tables

I've been experimenting with the tradeoffs between JSONB columns vs
nested tables in Postgres. The current Tasking Manager database schema
has multiple small two columns tables, most of those got turned into
arrays as I refactoring the schema. But some of the tables in TM are
larger like project_team or task_history. Those I had been using as a
nested array. The advantages, easy to query, you can see all the
columns in each table. Nested tables are being used to reduce needing
multiple SQL queries in series to get basic information. The downside
is a nested table has to exist in the database when the primary table
is created, so there is a dependency problem. It's also a touch
confusing, since when you list the tables, you have several of these
adding clutter. When doing a bulk insert of multiple tables, it's
messy dealing with the dependencies.

Since Postgres v12, there are new functions for dealing with JSONB
columns that I think make them better than nested tables. A JSONB
column doesn't need to be defined ahead of time, it's created
dynamically, so also easier to update in the future. They're also
fast, JSONB columns have their own index. The downside is the syntax
for accessing a JSONB column reminds me of AWK, write-once, difficult
to debug. You wind up with SQL like this:

	SELECT jsonb_path_query(team_members, '$.members[*] ? (@.function[*] == "MEMBER" && @.active=="false")') AS player FROM teams WHERE "id" = 3;

I'm burying the SQL queries in a python module, but luckily at one
point implementing new queries is mostly cut & paste with minor
editing for column names.

## Enum Usage

The current code base for the Tasking Manager defines a bunch of
enums, which aren't actually used for database access. This makes the
code harder to read as most of the code and the database only use the
integer value. This project enforces the use of enums as it makes the
code more readable, and more secure. Unfortuantely when using the
existing data in the Tasking Manager database, this requires
conversion. As a jsonb column may also contain enum values, this
requires the data being inserted or updated to loop through all the
values to convert them.

## The Types files

All of the enums have been extracted from FMTM and TM, and are defined
in the *types.yaml* file. This file must be processed before all the
others, since it defines custom data types all the other files depend
on. While the names of the types is the same across platforms, there
are minor differences in capitalization which are easily handled.

### types_tm.sql

This file contains the definitions for postgres. These add new types
into postgres, which can then be used by the other tables.

### types_tm.py

This file contains the definitions for python. These are standard
Python IntEnums, so it's possible to get both the name or the numeric
value.

### types_tm.proto

This file contains the protobuf definitions required by gRPC. These
are needed to compile any of the other protobuf files.

## Regenerating the files

After any changes to one of the config files, the various output files
must be generated. A utility program is included to regenerate all the
files, and then updates the database table schemas too. Note that this
will wipe any existing data, so is only used to initialize the
database.

	tmadmin-manager.py */*.yaml -v

If you just want to regenerate the output files to view a change, or
work with only one table, use the *generate.py* program. There is also
a base class *Generator* that can be used by other programs.

	generate.py users/users.yaml -v

## The Python API

There are two python files generated to work with the data structures
directly. One is a direct representation of the database table
schema. This is in the __*_class.py__ file. Each one contains a class
for each table in the config file. For example, the *users* table has
a **UsersTable** class. Each column in the table is a parameter with a
default value, so the internal data is the same as the database. The
internal data stucture is used throughout TM Admin. When instantiating
an instance of this class, any column can be specified as a
parameter. This class is used to insert data into the table, to update
existing data, or to query data.

	ut = UsersTable(name='foobar', email_address="bar@foo.com", mapping_level='INTERMEDIATE')

The other is for managing protobuf messages. As a protobuf message
does not contain the full record from the table, these are similar to
the __*Table__ class, but just have less fields in the data
structure. What is in the protobuf messages is defined in the config
file using the [share keyword](configuring.md). This is only used to
create and parse gRPC messages. Since all the field names between
these two classes are the same, it's easy to exchange data.

# Importing Data From Tasking Manager
	
If you have access to an actual postgres database with Tasking Manager
data in it, it can be imported into the *tm-admin* database schema. As
the tm-admin schema was originally based on the TM database schema,
this is mostly a direct copy. The only major change is in the tasking
manager, it only uses the integer value for an array, even when there
is a Enum already for this. This project uses the proper enums
instead, so some conversion is required.

Since the data structure for python is in the *types_tm.py* file,
it's easy to instantiate a class and get the name for the enum from
it's integer value.

	from tm_admin.types_tm import Userrole,
	value = 1
	role = Userrole(value)
	print(role.name)

## Importing the Data

Data can be imported from a current Tasking Manager into the new
database schema. This can be done on a table by table process, or a
unified way. There are a few steps to import data from an existing
Tasking Manager database into the schema used by TM Admin. The TM
Admin schema is a superset, all columns in primary tables are the same
in TM and TM Admin. The main differences some of the tables from the
Tasking Manager have been incorporated into the primary tables to
reduce the amount of database queries required for some of the
endpoints.

Tasking Manager uses integers for Enum values when accessing the
database. TM Admin uses the proper Enum as it makes the code easier to
read and also forces all values to be in range. Once the primary table
is imported, then each table has to be updated with the small utility
tables. Those have all been replaced by using array columns, as most
where just two columns anyway. The list of utility tables is covered
later in this document.

It is assumed the data will only be imported once when upgrading
Tasking Manager to a new major version. This is so no data is lost.

### Importing a Table

To import only one table, initially use the *tmdb.py* program to
import the existing primary table into TM Admin. This only imports a
single table without any dependencies.

	tmdb.py -t users -v

Some of the primary tables from Tasking Manager have small auxilary
tables that then need to be imported. Since importing these updates an
existing record instead of inserting it, the primary table's data
obviously must be imported first.

To import the remaining tables into the array columns or a jsonb
column, each base class has support for their format. For example, to
import all the utility tables for the primary *users* table, do this:

	users/users.py -v

Note that the base classes have methods for importing everything, so
they can be utilized by other programs. The simple terminal based way
is of primary interest only to developers.

### Importing everything

While importing single tables is useful for development, most just
want to import everything. There is a utility program that does
this. Currently this goes through several steps required to setup a
database from scratch. This required you have created the database
already, but it has no tables defined.

        # Generate all language binding files
        tmadmin_manage.py -v -c generate */*.yaml

        # Create the tables in the database
        tmadmin_manage.py -v -c create */*.sql

        # Import the data for the all primary tables.
        tmadmin_manage.py -v -c import

        # Import the data for just the users table
        tmadmin_manage.py -v -c import users

The default databases used by this program are *tm4* for the existing
data, and *tm_admin* for the new database. This can also be changed
using the *-i* and *-o* options to this program. There is more detail
on the tmadmin-manage.py program [on this page](tmadmin-manage.md).

### Default Tables

There are a few support tables that have preset values, like interests
or licenses. These are tables in the database because they can be
updated by the front end, which we can't do as a Enum. So these are
just default values that get indexed by the other tables.

### Changes

The existing TM database schema has been extended multiple times over
many years. One common theme is is often has multiple tables for a
single record type. Many of these are small, and consist primarily of
2 columns, usually two IDs. For example project_id and
user_id. There's much more detail on the existing database schema
[here](tmschema.md).

#### User Table

Rather than have a separate *project_favorites* table, an array of projects has
been added as *favorite_projects*. Same with the *user_interests* and
*user_licenses*. *user_interests* is now an array of interest IDs, and
*user_licenses* is a single integer. The *users_with_email* columns
has been removed as it's possible to just query the database for users
with or without email addresses.

#### Projects Table

There's a lot of project related tables.

From project_info:

* name
* short_description
* description
* instructions

From **project_allowed_users** table

* add to array of users

From **project_favorites** table

* add to array of favorites

From **project_interests** table

Right now a project has a single interest, but it'd be easy to exapand
to an array if multiple interest support was wanted.

* add integer column

From **project_custom_editors** table

* appears to only be used for Rapid, but it's in the Enum for editors,
  so uneeded now

From **project_priority_areas** tables

* add array of priority areas

From **project_teams** table

* Add *team_id*, *team_role* to *member* jsonb column.

#### Organizations Table

From **organisation_managers** tables into an array in the
organizations table.

* Add array of manager's user IDs

#### Teams Table

The teams table is based on OSM teams, but has been modified to
support any team.
Added columns from the **team_members** to the TM Admin *teams* jsonb
column.

* Team ID
* function (mapper or manager)
* active

The *join_request_notifications* column in team_members has been left
out as this will be in the notification table.

#### Tasks Table

This is obviously a heavily used table, and in the Tasking Manager, is
actually 5 tables. The goal here is to merge the tables together using
postgres arrays and jsonb columns to reduce the number of sequential
queries that need to be made for some API endpoints.

This table also has two indexes, as the task ID is not unique across
all projects, only within a single project. Both the task ID and
project ID need to be used in queries to get the right one.

* task_mapping_issues is now an Enum instead of a table

##### Task History Table

The *task_history* table is now a jsonb column within the tasks
table. The *id* column is no longer needed, and the *project_id* and
*task_id* are already in the tasks table. In TM the action is a
string, which in TM Admin is a proper Enum, which is used instead. The
*action_text*, *action_date* and *user_id* are all preserved in the
jsonb column. The action is now using an Enum in the code, and the
equivalant SQL type everywhere.

##### Task Mapping Issues

This table in Tasking Manager must be new, as it contains little
data. It's basically a summary of the issue, like "Missed
Features(s)", or "Feature Geometry", with a count of how many features
have this issue. I'm not sure the category actually needs to be a
column.

Currently in the Tasking Manager there is an index into the history
table, which no longer exists. So the details of the issue are merged
with the issues jsob column. THe only two columns still in use is
issue and count.

In the Tasking Manager, there is a task status of *BADIMAGERY*, which
has been moved to the *Mapping_issue* enum, which is more appropriate.

##### Task Invalidation History Table

This table has been merged into the history as invalidation is an
update to the history. Several columns have been dropped as nopw they
are unnecessary, id, project_id, task_id. Updated_data seemes like a
duplicate, so using the two validate or invalidate dates, since
updates change those.

##### Task Annotations

This table appears not to be used by TM yet.

##### Notifications

TODO: not implemented yet

##### Messages

The messages table is imported with no changes.

#### Campaigns

Currently in TM, campaigns are implemented as a primary table, and two
utility ones. These two utility tables gone in TM Admin, and replaced
by an array for each.

## Testing Changes

The code has been designed to be flexible and dynamic. Most of the
code extracts the keys & values from the data itself. There is a lot
of looping through data structures to keep things self-adjusting.

A test suite has been created from the internal APIs used by the
backends of TM and FMTM. Many of the API endpoints are for
convienince, getting the value of a column from the database, or
updating existing data. Some are more functional, accessing one or
more tables to produce the correct output. These tests duplicate the
lower-level functionality the existing backends require.

