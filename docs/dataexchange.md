# Exchanging Data

Exchanging data between projects has a few issues, namely the ID of
the user, the project, and the organization are different in the
different projects. Not all fields are useful cross-project, so some
but not all of the columns in a database table are exchanged w ith
other projects. There are other issues to handle, a projet
manager/admin in Tasking Manager (TM) may only be a a mapper in the
Field Mapping Tasking Manager (FMTM) project, so the roles change, but
the rest of the user profile stays the same.

Currently all the database tables have every column used by FMTM or
TM. Since there are many application specific columns, these are
simply ignored by the application. While this does make the database
slightly larger having multiple empty columns, it's a tradeoff between
database size and simplifying the code base. A future enhancement to
the YAML config file subsystem will support using a subset of all the
database columns.

# Identifying Records

Since the ID can't be used between projects, the name or address is
the only unique field that can be used to identify a user or an
organization, etc...  For users, the best ID is their OpenStreetMap
(ODM) ID, as that is unique globally. While some support can be added
to track unique IDs across multiple projects, this can be cumbersome.

Another way to identify a record is through location. Since both
projects and tasks have an polygon area of interest, a point within a
project in one application, can be used to query a remote project to
find the project or task. For example, if a field mapper finds bad
data, the location of that data can be used to find the TM project and
task, so the task can be invalidated.

# Filtering Data

Since not all data fields are needed in each project, the YAML
configuration file supports a flag for each item in a data structure
as to whether it should be shared or not. For example, a database
query might return many columns, but only a few are usefully portable
across multiple projects.

For instance, Tasking Manager has task boundaries, in FMTM, tasks
are smaller, because it involves mappers walking. So transferrihng
exact task boundaries would be meaningless. In this usage case, the
tasks transfer from TM to FMTM would be a multi-polygon. FMTM would
create a project AOI based on the outer boundary of all the of the
tasks, and then recalulate FMTM specific tasks boundaries.

## Data Exchange Schemas

Some fields need to be in any data packet that is intended for
database queries, since the there needs to be a way to refer to an
existing record, if it exists. 

### Project Data

A project has a wide definition depending on the type of
application. Since this module is focused on Tasking Manager style
applications, all version will have at least a project name and an
Area of Interest (AOI). In addition, each tracks task usage, so the
number of tasks mapped, validated, or invalidated exists in all
tables, but has different data.

#### Field Mapping Tasking Manager

For FMTM, it uses an *odkid* column, which is used to communicate with
ODK Central. This is an example of needing to store the ID of a remote
application to exchange data for specific items. How the ID of a
remote project is stored may change in the future to handle multiple
remote applications, but for now, it's only the one for ODK Central.

FMTM also uses several columns for working with
OpenDataKit(ODK). These are the login credentials for an ODK Central
server, and an XLSForm for the project.

#### Tasking Manager

TM uses a series of columns that are used for editing OSM data. This
includes presets for several editors. 

### User Data

### Task Data

A task AOI is not usually useful between projects, as a TM task is
much larger than an FMTM task. For a Drone Tasking Manager (DTM), the
task size will also be different. Since tasks are not portable across
projects, each project maintains it's own data on the creation date,
tasks mapped, validated, invalidated, etc...

### Organization Data

### 


