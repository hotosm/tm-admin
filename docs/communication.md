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
here](configuring.md).

All communication is bi-directional. Projects can send data, or handle
a request for data. For any data that is sent, the response is a
simple SUCCESS/FAILURE message. FAILURE message also return an error
message and error code.

It seems that most of the projects start with TM. After critical tasks
are mapped, they then could be migrated to FMTM for field data
collection. The FMTM mappers would also be ground truthing the remote
mapping. It's entirely possible that FMTM field mappers would find
issues with the data extract of OSM buildings, and want to notify the
TM project manager to invalidate some tasks and remap them.

## Notifications

Some messages have nothing to do with the database, they're for
communicating other types of requests. Other than just doing database
updates, this is the core of an end to end data flow.

Examples of some notifications are:

* Underpass would notify TM or fAIr of a data quality issue
* An FMTM project manager would notify TM to invalidate a task
* fAIr would notify an FMTM project manager that the imagery has been
  processed so a data extract could be made
* fAIr would notify OAM that drone imagery is needed for an AOI
* OAM would notify fAIr when drone imagery is ready to be processed

## Projects exchange user profiles

Since a user may be contributing to multiple projects, it should be
possible to clone a users profile between projects. For example, when
a Tasking Manager (TM) is being worked on, some users may also be
using the Field Mapping Tasking Manager (FMTM) to ground-truth the
data. Or they may want to use [fAIr](https://github.com/hotosm/fAIr)
to process the drone imagery they just collected.

### User profiles

These are the data fields that need to be in this message to create a
user profile in the database. The user ID in TM or FMTM won't be the
same, since each project will have different teams of mappers. Instead
of the ID, the username will be used to refer to a mapper.

* username
* name
* city
* country
* email_address
* is_email_verified
* is_expert
* mapping_level 
* password

#### Receiving project decides, update or create ?

When this message is received, it should update the database for this
user unless the username already exists, and send the response
acknowledgment.

## TM sends project profile

It is entirely likely that for disaster response, an area may be
remotely mapped with TM, and then will be field mapped with FMTM as a 
follow-up. The instructions would be very different, so aren't
needed. The tasks won't be sent either, as a TM task is much largerr
than an FMTM task. FMTM mappers are walking when mapping. The project
ID is also not transmitted, as it'll be different in different
projects. There may also be occassions where a project would be sent
to fAIr, Export Tool, or Underpass.

* name
* outline
* description
* location_str
* organisation_id (*spelling depends on country*)
* priority
* centroid

A project transferred to FMTM has no project manager, so these are
initially only an AOI and draft project description. FMTM would need
the ability to search for an unassigned project, ie... no
manager. Then when there is a project manager it would be assigned to
them.

#### Receiving project decides, update or create ?

When this message is received, it should update the database for this
project, and send the response acknowledgment.

## TM sends organization profile

Organizations may be using multiple HOT projects, so this would sync
organization data between projects so it wouldn't have to be manually
edited for each poroject like it is now.

* name
* description
* url
* logo
* type

#### Receiving project decides, update or create ?

When this message is received, it should update the database for this
organization, and send the response acknowledgment.
