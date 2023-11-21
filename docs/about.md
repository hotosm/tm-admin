# TM-Admin

Administrative functions for Tasking Manager style projects. There is
a lot of shared functionality between Tasking Manager style projects,
so rather than having duplicate implementations, the goal of this
project is to provide that functionality in a way it can be shared
across multiple projects.

These are implemented as python modules, and can be used in the
backend of a Tasking Manager style website. While it is possible to
have multiple projects access a single database, there is also support
to exchange data between projects if they are all using their own
database. There is more detail on the inter-project
[communication](communication.md).

## User Management

Handles user profiles. While it is recommended, it is not required for
all users to have an OSM ID. With an OSM ID, AUTH2 works, so users
only have to login once, but can use multipe projects.

## Organization Management

Handles organization profiles. Some organizations use multiple
projects, so this just shares the profile data so it doesn't have to
be entered multiple times.

## Project Management

Handles the project. A project in it's simplest form is an area of
interest as a polygon, the name, the description, and a project
manager. In addition it can access the tasks table for task specific
data.

## Task Management

Handles the tasks. A task is a polygon within the project area of
interest.

## Team Management

Handles OSM Teams profiles. 
