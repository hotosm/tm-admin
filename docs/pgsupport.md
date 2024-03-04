# pgsupport.py

This class has support for managing the database tables, and is
derived from the *PostgresClient* class. It is a wrapper on top of
pgasync, and focused on the client side of the internal API. It has
helper functions for commen queries, as well as providing a simpiler
interface for querying and updating data than raw SQL. It uses the
generated __*_class.py__ files that define each database table as the
primary data structure. This class gets instantiated for each table in
the data getting frequent access. It also uses all of the enums
defined in the generated *types_tm.py* file.

One of the primary functions of this class is handling all the
datatype conversion. When using jsonb columns in postgres, there is no
datatype information. For strings and numbers this is fine, but not
for jsonb columns. Since the jsonb columns are also defined by the
same yaml config files all the other tables use, it's possible to get
the datatype of each value in the jsonb array. This will then contain
the string name of the Enum. If querying the table directly, this will
be returned as an string value. If querying with the API defined in
each table's *api.py* file, the value is returned as a Python Enum.

Python dictionaries are heavily used as a parameter. All of the
generated data structures use a similar naming convention, so all the
data structures are very dynamic. Any change to the yaml config files
gets propogated to all the language bindings. Enum values are used
everywhere, improving the code readability.

To support prepared SQL statements, most of the API functions take a
list or a dictionary of multiple entries. The functions for querying
or updating data take two parameters.

## Inserting A Record

For example, to insert or update a record in the *projects* table,
use the generated **ProjectsTable** class. *The insertRecords()*
method takes a list of *Table* classes. The *id* column is a sequence
variable, so will auto-increment if no *id* is specified. If the *id*
is specifed in the Table data structure, then that is the value used
for the record. Inserting a record with an id is only used when
importing data from the Tasking Manager. This function returns the
*id* column of the just inserted record.

In this example, **GRID**, **DRAFT**, and **INTERMEDIATE** are
all enums. The *teams* column in this example is a jsonb column in the
table, so defined by a dictionary. Updating a record uses the same
class, which directly maps to the table schema.

	from tm_admin.projects.projects_class import ProjectsTable

    teams = {"team_id": 2, "role": "TEAM_MAPPER"}
    pt = ProjectsTable(author_id=1, geometry=geom, centroid=center,
                        created='2022-10-15 09:58:02.672236',
                        task_creation_mode='GRID', status='DRAFT',
                        mapping_level='INTERMEDIATE', teams=teams)
    id = await pgs.insertRecords([pt])

## Querying The Database

As the database schema is reasonably complex, with a mix of arrays and
jsob columns, the API supports basic querying operations. Much
database accesss is querying or changing a single colum. There some
helper functions for common querying by the *id* or *name* of a
project, user, etc...

These following examples are for accessing the data for a column. More
than one column can be specifed to be in the output data. By default,
all the records for the specified columns is returned. It is also
possible to specify a clause for *WHERE*. This can be a value, or **IS
NULL**. A dictionary is used for the conditional. When multiple
conditionals are used, the default is to **OR** between them.

For example, get all the records in a table:

    data = await pgs.getColumns(['id', 'teams'])

Get the team with an ID of 144:

    foo = {'id': 144}
    data = await pgs.getColumns(['id', 'teams'], [foo])

Get the columns in the team where the role is *TEAM_READ_ONLY* and the
team ID is 144. This queries a jsonb column:

    foo = {'teams': {"role": tm_admin.types_tm.Teamroles.TEAM_READ_ONLY, "team_id": 144}}
    data = await pgs.getColumns(['id', 'teams'], [foo])

### Getting Data

The first parameter is the columns to return from query. The second is
the conditions for the WHERE clause in SQL. If there is no second
parameter, then all the data in the requested columns is returned.

This example returns the list of teams and roles for this
project. Multiple conditions for WHERE can be specified, when
converted to SQL they use an *OR* betweeen them. If *"null"* is used
as the value, then in SQL this becomes *"IS NOT NULL"*. The returned
data is always a list, even if it contains only a single entry.

	project_id = 15173
	data = await projects.getColumns(['teams', 'name'],  [{"id": project_id}])

### Updating a Table

Updating a record is more complicated since some columns are JSONB or
arrays. This function takes two dictionaries. The first parameter
defines the column to update, the second is the WHERE clause. This
function returns the *id* column of the just update record, or zero if
no records match the WHERE criteria.

If there is no WHERE clause, then all the records in the table are
updated.

    foo = {"featured": "true"}
    data = await projects.updateColumns(foo)

Enums are also supported, as they are used heavily in this project as
opposed to just the numerical value. This makes the code and the table
data more readable.

    foo = {"featured": "true", "difficulty": tm_admin.types_tm.Projectdifficulty.CHALLENGING}
	project_id = 1
	data = await projects.updateColumns(foo, {"id": project_id})
