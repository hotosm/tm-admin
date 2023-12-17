# REST API Endpoints

# Users

Endpoints for managing User profiles.

| Tasking Manager | FMTM|
|-----------------|-----|
|Get paged list of all usernames|Get Users|
|Registers users without OpenStreetMap account||
|Updates user info||
|Resends the verification email token to the logged in user||
|Get paged lists of users matching OpenStreetMap username filter||
|Get user information by OpenStreetMap username||
|Get stats about users registered within a period of time||
|Get user information by id|Get User by ID|
|Get a list of tasks a user has interacted with||
|Allows user to enable or disable expert mode||
|Allows PMs to set a user's mapping level||
|Allows PMs to set a user's role|Create User role|
|Get details from OpenStreetMap for a specified username||
|Get recommended projects for a user||
|Get detailed stats about a user by OpenStreetMap username||
||Get User Roles|

# Organizations

Endpoints for managing Organization profiles.

| Tasking Manager | FMTM|
|-----------------|-----|
| List all organisations|Get Organization||
| Creates a new organisation|Create Organization||
| Deletes an organisation|Delete Organizations||
| Retrieves an organisation|Get Organization Detail||
| Updates an organisation|Update Organization||
| Return statistics about projects and active tasks of an organisation||

# Projects

Endpoints for managing projects.

| Tasking Manager | FMTM|
|-----------------|-----|
|List and search for projects|Read Projects|
|Creates a tasking-manager project|Create Project|
|List and search projects by bounding box||
|Get featured projects||
|Get all projects for logged in admin||
|Get popular projects||
|Get similar projects||
|Gets projects user has mapped||
|Deletes a Tasking-Manager project|Delete Project|
|Get a specified project including it's area|Get Project Details|
|Updates a Tasking-Manager project|Update Project|
|Set a project as featured||
|Send message to all contributors of a project||
|Unset a project as featured||
|Transfers a project to a new user||
|Get all user activity on a project||
|Get latest user activity on all of project task||
|Get all user contributions on a project||
|Get contributions by day for a project||
|Get AOI of Project||
||Upload Custom XLSForm|
||Project Partial Update|
||Upload Multi Project Boundary|
||Task Split|
||Upload Project Boundary|
||Edit Project Boundary|
||Update Odk Credentials|
||Validate Form|
||Generate Files|
||Get Data Extracts|
||Update Project Form|
||Get Project Features|
||Generate Log|
||Get Categories|
||Preview Tasks|
||Add Features|
||Download Form|
||Update Project Category|
||Download Template|
||Download Project Boundary|
||Download Task Boundaries|
||Download Features|
||Generate Project Tiles|
||Tiles List|
||Download Tiles|
||Download Task Boundary Osm|
||Project Centroid|

# Tasks

Endpoints for managing tasks in a project.

| Tasking Manager | FMTM|
|-----------------|-----|
|Delete a list of tasks from a project||
|Get all tasks for a project as JSON|Read Tasks|
|Extends duration of locked tasks||
|Invalidate all validated tasks on a project||
|Locks a task for mapping||
|Lock tasks for validation||
|Map all tasks on a project||
|Set all bad imagery tasks as ready for mapping||
|Reset all tasks on project back to ready, preserving history||
|Revert tasks by a specific user in a project||
|Split a task||
|Unlock a task that is locked for mapping resetting it to its last status||
|Unlock tasks that are locked for validation resetting them to their last status||
|Undo a task's mapping status|Update Task Status|
|Set a task as mapped|Update Task Status|
|Set tasks as validated|Update Task Status|
|Validate all mapped tasks on a project|Update Task Status|
|Get task tiles intersecting with the aoi provided||
|Get all tasks for a project as GPX||
|Get all mapped tasks for a project grouped by username||
|Get all tasks for a project as OSM XML||
|Get a task's metadata|Get Task|
|Get invalidated tasks either mapped by user or invalidated by user||
|Get Task Stats||
||Get Qr Code List|
||Edit Task Boundary|
||Task Features Count|
