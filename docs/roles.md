# Managing Roles & Permissions

Currently there are two sets of roles in Tasking Manager style
projects, users and teams, The team roles only apply to teams, a
users indivigual role is used for mapping. For a user on a team, their
role is derived from the team's role.

While it would be possible to implement complex access rules for most
operations, I think a ladder approach is easiest. Operations just
require a certain minimal role level. For example, an assocate
project manager might be able to update a project profile, but not be
able to delete it. It is entirely possible that an associate project
mamager would be helping with managing mappers and team profiles as
well.

## Team Roles

The HOT Tasking Mannager (Tasking Manager) has these team roles:

	- teamroles:
		- READ_ONLY
		- MAPPER
		- VALIDATOR
		- MANAGER

The HOT Field Mapping Tasking Manager (FMTM) doesn't quite have the
same concept as an OSM Team, as it uses OpenDataKit (ODK) instead of
OpenStreetMap (OSM). If a field mappers using FMTM are also in an OSM
Teams, they should be able to use OSM Teams from FMTM, but Teams
support in FMTM is not something on the roadmap. It is entirely likely
field mapper may want to form a team, whether they have an OSM account
or not. For now, FMTM doesm't need to add any additional roles. 

## User Roles

The HOT Tasking Mannager (Tasking Manager) has these user roles:

	- userrole:
		- USER_READ_ONLY
		- MAPPER
		- ADMIN
		- PROJECT_MANAGER

The expanded set of roles used by the Field Mapping Tasking Manager
(FMTM) is:

	- userrole:
		- FIELD_ADMIN
		- ORGANIZATION_ADMIN
		- PROJECT_MANAGER
		- ASSOCIATE_MANAGER
		- VALIDATOR
		- WEB_ADMIN

A difference here is FMTM has VALIDATOR as a user roles, where Tasking
Manager has it as a team role. Other changes are the addition of
multiple administrative roles. Since roles aren't portable across
projects, this can be ignored. I'm not sure SUPER_ADMIN and
WEB_ADMIN are needed, it seems those access permissions would be
handled by postgres directly. Currently FMTM is not using most of
these roles yet, and is linmited to READ_ONLY (the default), ADMIN,
and VALIDATOR.

# Data Exchange

Since this project supports data exchange between projects, it's worth
nothing that roles *are not* portable across projects. Even withnin
Tasking Manager, a project manager in one project only may be  mapper
in another, Especially for Tasking Manager projects transferred to
FMTM.

There are other limitations, for example, the ability to send and
receive data from other projects other than automated messages.

# Role Handling

## Tasking Manager Role Handling

The Tasking Manager has a rich set of roles. Initially all roles were
user roles, but currently these have been replaced by team roles. The
user role is now derived from the team role. By default, all teams and
users are READ_ONLY. Only an ADMIN, VALIDATOR, or PROJECT_MANAGER
can change a user or team role.

## FMTM Role Handling

Currently FMTM only supports the ADMIN and READ_ONLY roles. READ_ONLY
limits users to only viewing publically accessible projects. The ADMIN
is the only one who can create, modify, or delete projects.

# Tasking Manager Admin Roles

Since TM-Admin supports multiple projects, it has an
enhanced set of roles and permissions. The roles for each project are
defined in a configuration file to allow for project specific roles
and access permissions.

## Mapper

For Tasking Manager, a MAPPER is tracing features using satellite
imagery with the goal of adding these to OSM. By default, a new user
or team is READ_ONLY, and limited to only viewing public projects.

For FMTM, a mapper is using ODK Collect to collect data, not all of
which is for OSM. Once a mapper is logged into FMTM, then they hgain
the MAPPER role, whic allows them to download the XForm, data extract,
and imagery basemap.

## Organization Manager

The ORGANIZATION_MANAGER is responsible for creating and maintaining
the organization profile for the TM or FMTM. They would be
responsible for specifying a PROJECT_MANAGER for the organization's
projects. The ORGANIZATION_MANAGER is also responsbile to create the
campign for a mapping project.

## Project Manager

The project manager is responsible for creating and maintaining
project profiles. They have the ability to delete projects when
necessary.

## Associate Manager

The ASSOCIATE_MANAGER is usually a PROJECT_MANAGER in training, and
has most of the permissions of a project manager other than project
or campaign creation or deletion. Their role is to support the
PROJECT_MANAGER, who may be responsible for multiple projects.

The ASSOCIATE_MANAGER also doubles as the FIELD_ADMIN, as it's not
uncommon to need somebody in the field to unlock tasks

## Validator

For Tasking Manager, the VALIDATOR role is responsible to sign off on
the quality of the features that have been traced. They have the
abilit to modify the task status to be invalidated. This may be due to
poor building geometry, unconnected highway segments, or unsupport tag
or values. Often the PROJECT_MANAGER is also the VALIDATOR, so any
PROJECT_MANAGER would also have permissions to validate. With the
implementation of teams, it is also possible that there will be a team
of validators for a project.

Since FMTM uses ODK, the chances of bad tag values is limited, but
not always, as it is possible to incorrectly answer a question, or
misspellings in text fields. If a user consistently makes the same
mistakes, a task may be invalidated requiring that task to be mapped
again. Since FMTM supports both public data for OSM, and private data
for the project sponsors, the VALIDATOR will also make sure no private
data, like gender for example, leaks into OSM.

# Permission Categories

Permissions are based on the user or team role. In FMTM, this is
simple, for TM, it's much more complicated, as often it involves the
mappers level within OSM as well.

It's common in the industry to use these 4 high-level permissions for
access control. All other permissions are based on top of these, and
of course the role is also taken into consideration.

## read

This access is limited to read-only access of public facing
content. This the default for users and teams until somebody with
higher permissions updates it.

## create

This access allows the create of projects, organizations, and
campaigns.

## delete

This allows for the deletion of projects, organizations, and
campaigns.

## modify

This allows for the modification of projects, organizations, and
campaigns.

## Team Permissions

Team support for TM is implemented using OSM Teams, and are created on
the OSM Teams website by a project or organization manager. It is not
required for all mappers to be in a team. For mappers on a team, they
inherit the team role, and don't have a user role. Users not in a team
still have a user role. For a user to join a team, they are invited
via email, and have to respond to the email before they are officially
on a team.

## User Permissons

For users not in a team, the default is a MAPPER, which lets them
select tasks and start mapping. The project manager or admin can
update a users role. Only an admin can designate a mapper to be an
admin.

# Implementation

To support multiple projects with different needs, the role &
permissions module uses a configuration file in YAML format. This
defines the roles and their permissions as they relate to the 4
primary operations used by the industry standard RBAC for access
control. These control acccess to the database tables.

* create
* update
* delete
* read

## Config File

The confg file has two primary top level tags, *domains* that list all
the tables, and *permissions*, which is where the actual settings
are. Under the permissions tags, the next level is the role of the
user or team. These are a direct match to the types defined in python
and SQL. Each tag lists the RBAC access permissions.  Since there can
be a hierarchtical relationshop between roles, a role can include the
values from other roles. This is done using the *children* tag. For
example, the *validator* can is inherits values from the *mapper*
tag. Since not all roles can access all tables, they are listed under
the *tables* tag. Since roles inherit values from their children, only
the additionalo tables the rols can access need to be listed.

	- domains:
		- teams
		- users
		- organizations
		- projects
		- tasks
		- users
		- messages
		- notications
		- campaigns

	- permissions:
		- mapper:
			- read
			- tables:
				- projects
				- tasks
				- users
				- messages
				- campaigns

	- validator:
		- update
			- children:
				- mapper
			- tables:
				- projects
				- tasks
				- users

	... more roles

## API

There are defined roles that can apply across all projects. This is
a super-set of the roles a project may support. For a project, the
roles are defined in the config file, and wil lbe a subset of these
values.

* READ_ONLY
* ORGANIZATION_ADMIN
* PROJECT_MANAGER
* ASSOCIATE_MANAGER
* VALIDATOR
* MAPPER

The API to check access permissions for a role is simple, and requires
the table name, the role, and the operation. While some operations in
the backend for a website will use the role to determine access to
other functionality, most operations require database access, so this
controls that lower level access. Most simple operations, like a
mapper locking a task to map have to update the database, so this
allows the backend to control access for most operations.

For example, this checks to make sure a mapper can read the campaigns
table. if sucessful, it returns True.

    await acl.check('campaigns', Roles.MAPPER, Operation.READ)

In this example, the mapper is trying to create a campaign, but lacks
the proper permissions to do so. In this case a False is returned.

    await acl.check('campaigns', Roles.MAPPER, Operation.CREATE)
