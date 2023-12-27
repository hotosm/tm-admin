# Changing The TM Admin Schema

This document covers how to make changes to the data schemas used in
TM Admin, and the changes that were made from the original Tasking
Manager (TM).

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

There are two steps to import data from an existing Tasking Manager
database into the schema used by TM Admin. The TM Admin schema is a
superset, all columns in primary tables are the same in TM and TM
Admin. Initially use the *tmdb.py* program to import the existing
primary table iunto TM Admin.

	tmdb.py -t users -v

Since TM uses integers for Enum values, TM Admin uses the proper Enum
as it makes the code easier to read and also forces all values to be
in range. Once the primary table is imported, then each table has to
be updated with the small utility tables. Those have all been replaced
by using array columns, as most where just two columns anyway. The
list of utility tables is covered later in this document. To import
the remaining tables into the array columns, each base class has
support for their format. For example, to import all the utility
tables for the primary *users* table, do this:

	users/users.py -v

Note that the base classes have methods for importing everything, so
they can be utilized by other programs. The simple terminal based way
is of primary interest only to developers.

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

The *users* tables also absorbed the team_members table, adding these
columns to the *users* table.

* join_request_notifications
* team
* active
* function

#### Import support

TM Admin uses a unified database schema, whereas TM often has multiple
small tables with only two columns. When importing data from TM into
TM Admin, the contents of those tables gets merged into the existing
*users* table. I'm assuming the original developers didn't like using
arrays.

* mergeLicenses() - Merge the TM *user_licenses* table into TM Admin
* mergeInterests() - Merge the TM *user_interests* table into TM Admin
* mergeFavorites() - Merge the TM *project_favorites* table into TM Admin

#### Projects Table

There's a lot of project related tables.

From project_info:

* name
* short_description
* description
* instructions

From **project_allowed_users** table

* add array of users

From **project_favorites** table

* add array of favorites

From **project_interests** table

* add integer column

From **project_custom_editors** table

* appears to only be used for Rapid, but it's in the Enum for editors,
  so uneeded now

From **project_priority_areas** tables

* add array of priority areas

From **project_teams** table

* FIXME: not sure
* team_id, project_id, team_role

#### Organizations Table

From **organisation_managers**

* Add array of manager's user IDs

#### Teams Table

Added columns from team_members to TM Admin *users* table
* Team ID
* function (mapper or manager)
* active

The *join_request_notifications* column in team_members has been left
out as this will be in the notification table.

#### Tasks Table

task_mapping_issues is now an Enum instead of a table

##### Task Annotations

TODO: not implemented yet

##### Task History Table

TODO: not implemented yet

##### Task Invalidation History Table

##### Notifications

TODO: not implemented yet

##### Messages

TODO: not implemented yet

#### Project Chat

TODO: not implemented yet

