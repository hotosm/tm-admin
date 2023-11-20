# Inter Project Communication

While there are data structures for all the columns in the database,
not all of the data fields need to be used for inter project
communication. Some field data is project specific, for example, tasks
in the HOT Tasking Manager(TM) are not the same as tasks in 
the nHOT Field Mapping Tasking Manager(FMTM), but most of the fields
are used for tasks in both.

With any project that is designed to be embedded into other projects,
there is a risk of duplicate data structures that can become a
maintainance nightmare in the future, since any changes will need to
be in multiple places. Each data structure is represented in the
database schemas, python, and gRPC. To reduce future maintainance
headaches, a single configuration file is used to generate multiple
output formats. More information on that process is [documented
here](configuring).

All communication is bi-directional. Projects can send data, or handle
a request for data. For any data that is sent, the response is a
simple SUCCESS/FAILURE message. FAILURE message also return an error
message and error code.

It seems that most of the projects start with TM. In some cases TM may
need to notify a fAIr project to process drone imagery. Then TM would
start the remote mapping project. After critical tasks are mapped,
they then could be migrated to FMTM for field data collection.

It's entirely possible that FMTM field mappers would find issues
with the data extract of OSM buildings, and want to notify the TM
project manager to invalidate some tasks and remap them.

## TM sends user profile to other project

Since a user may be contributing to multiple projects, it should be
possible to clone a users profile between projects. For example, when
a Tasking Manager (TM) is being worked on, some users may also be
using the Field Mapping Tasking Manager (FMTM) to ground-truth the
data. Or they may want to use [fAIr](https://github.com/hotosm/fAIr)
to process the drone imagery they just collected.

### User profiles

These are the data fields that need to be in this message to create or
replace a user profile in the database.

* id
* username
* city
* country
* is_email_verified
* is_expert
* mapping_level 
* password

#### Receiving project decides, update or create ?

When this message is received, it should update the database for this
user, and send the response acknowledgment.

## TM sends project profile

It is entirely likely that for disaster response, an area may be
remotely mapped with TM, and then will be field mapped with FMTM as a 
follow-up. The instructions would be very different, so aren't
needed. The tasks won't be sent either, as a TM task is much largerr
than an FMTM task. FMTM mappers are walking when mapping.

* id
* name
* outline
* description
* location_str
* organisation_id (*spelling depends on country*)
* priority
* centroid

A project transferred to FMTM has no project manager, so these are
initially only an AOI and draft project description.
