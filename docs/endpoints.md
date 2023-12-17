# REST API Endpoints

# Users

Endpoints for managing User profiles.

| Tasking Manager | FMTM|TM Admin|
|-----------------|-----|--------|
|Get paged list of all usernames|Get Users|UsersDB.getAll()|
|Registers users without OpenStreetMap account||
|Updates user info||UsersDB.updateTable()|
|Resends the verification email token to the logged in user||
|Get paged lists of users matching OpenStreetMap username filter||
|Get user information by OpenStreetMap username|UsersDB.getByName()|
|Get stats about users registered within a period of time||
|Get user information by id|Get User by ID|UsersDB.getByID()|
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

| Tasking Manager | FMTM|TM Admin|
|-----------------|-----|--------|
| List all organisations|Get Organization|OrganizationsDB.getAll()|
| Creates a new organisation|Create Organization|OrganizationsDB.createTable()|
| Deletes an organisation|Delete Organizations|||
| Retrieves an organisation|Get Organization Detail|OrganizationsDB.getByID()|
| Updates an organisation|Update Organization|OrganizationsDB.updateTable()|
| Return statistics about projects and active tasks of an organisation||

# Projects

Endpoints for managing projects.

| Tasking Manager | FMTM|TM Admin|
|-----------------|-----|--------|
|List and search for projects|Read Projects|projectsDB.getAll()|
|Creates a tasking-manager project|Create Project|projectsDB.createTable()|
|List and search projects by bounding box||projectsDB.getByLocation()||
|Get featured projects||projectsDB.updateTable()|
|Get all projects for logged in admin||projectsDB.getByWhere()|
|Get popular projects||projectsDB.getByWhere()|
|Get similar projects||projectsDB.getByWhere()|
|Gets projects user has mapped||projectsDB.getByWhere()|
|Deletes a Tasking-Manager project|Delete Project|
|Get a specified project including it's area|Get Project Details|projectsDB.getByID()|
|Updates a Tasking-Manager project|Update Project|projectsDB.updataTable()|
|Set a project as featured||projectsDB.updateTable()|
|Send message to all contributors of a project||
|Unset a project as featured||projectsDB.updateTable()|
|Transfers a project to a new user||projectsDB.updateTable()|
|Get all user activity on a project||projectsDB.getByWhere()|
|Get latest user activity on all of project task||projectsDB.getByWhere()|
|Get all user contributions on a project||projectsDB.getByWhere()|
|Get contributions by day for a project||projectsDB.getByWhere()|
|Get AOI of Project||projectsDB.getByID()|
||Upload Custom XLSForm|
||Project Partial Update|
||Upload Multi Project Boundary|
||Task Split||
||Upload Project Boundary||
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

| Tasking Manager | FMTM|TM Admin|
|-----------------|-----|--------|
|Delete a list of tasks from a project||
|Get all tasks for a project as JSON|Read Tasks|tasksDB.getAll()|
|Extends duration of locked tasks||tasksDB.getByWhere()|
|Invalidate all validated tasks on a project|||
|Locks a task for mapping||tasksDB.updateTable()|
|Lock tasks for validation||tasksDB.updateTable()|
|Map all tasks on a project||
|Set all bad imagery tasks as ready for mapping||tasksDB.updateTable()|
|Reset all tasks on project back to ready, preserving history||tasksDB.updateTable()|
|Revert tasks by a specific user in a project||
|Split a task||
|Unlock a task that is locked for mapping resetting it to its last status||tasksDB.updateTable()|
|Unlock tasks that are locked for validation resetting them to their last status||tasksDB.updateTable()|
|Undo a task's mapping status|Update Task Status|tasksDB.updateTable()|
|Set a task as mapped|Update Task Status|tasksDB.updateTable()|
|Set tasks as validated|Update Task Status|tasksDB.updateTable()|
|Validate all mapped tasks on a project|Update Task Status|tasksDB.updateTable()|
|Get task tiles intersecting with the aoi provided||tasksDB.getByLocation()|
|Get all tasks for a project as GPX||tasks.getAll()|
|Get all mapped tasks for a project grouped by username||
|Get all tasks for a project as OSM XML||
|Get a task's metadata|Get Task|
|Get invalidated tasks either mapped by user or invalidated by user||
|Get Task Stats||
||Get Qr Code List|
||Edit Task Boundary|
||Task Features Count|
