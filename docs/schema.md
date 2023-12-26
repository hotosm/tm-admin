# Changing The TM Admin Schema

# The configuration file

A simple YAML based config file is used as a single source for all the
data structures. This makes it easier to exchange data between
postgres, protobuf, and python. The format for configuring a schema is
explained in more detail in [this document](configuring.md). Any
changes to the config file are propogated into the different formats.

## The Types files

All of the enums have been extracted from FMTM and TM, and are defined
in the *types.yaml* file. This file must be processed before all the
others, since it defines custom data types all the other files depend
on. While the names of the types is the same across platforms, there
are minor differences in capitalization which are easily handled.

### types_tm.sql

This file contains the definitions for postgres.

### types_tm.py

This file contains the definitions for python.

### types_tm.proto

This file contains the definitions for gRPC.

## Regenerating the files

After any changes to one of the config files, the various output files
must be generated. A utility program is included to regenerate all the
files, and then updates the database tables too.

	tmadmin-manager.py */*.yaml -v

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

	./tmdb.py -t users -v

Zero bytes
organisation_managers, project_teams, task_invalidation_history, user_licenses, user_roles

No entries
alembic_version, licenses, mapping_issue_categories, osm_lines, project_aoi, project_chat, task_mapping_issues, teams, layer, topology

### Default Tables

There are a few support tables that have preset values, like interests
or licenses. These are tables in the database because they can be
updated by the front end, which we can't do as a Enum. So these are
just default values that get indexed by the other tables.

### Changes

The existing TM database schema has been extended multiple times over
many years. One common theme is is often has multiple tables for a
single record type. Many of these are small, and consist primarily of
2 columns, usually two IDs. For example project_id and user_id.

#### User Table

Rather than have a separate *project_favorites* table, an array of projects has
been added as *favorite_projects*. Same with the *user_interests* and
*user_licenses*. *user_interests* is now an array of interest IDs, and
*user_licenses* is a single integer. The *users_with_email* columns
has been removed as it's possible to just query the database for users
with or without email addresses.

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

From project_allowed_users
* add array of users

From project_favorites
* add array of favorites

From project_interests
* add integer column

From project_custom_editors
* appears to only be used for Rapid, but it's in the Enum for editors,
  so uneeded now

From project_priority_areas
* add array of priority areas

From project_teams
* FIXME: not sure

#### Organizations Table

From organisation_managers
* Add array of manager's user IDs

#### Tasks Table

task_mapping_issues is now an Enum instead of a table

##### Task Annotations

TODO: not implemented yet

##### Task History Table

TODO: not implemented yet

##### Task Invalidation History Table

##### Notifications

TODO: not implemented yet

#### Project Chat

TODO: not implemented yet
