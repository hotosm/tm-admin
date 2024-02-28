# pgsupport.py

This class is a wrapper on top of pgasync, and focued on the client
side of the internal API. It has helper functions for commen queries,
as well as providing a simpiler interface for querying and updating
data than raw SQL. It uses the generated __*_class.py__ files that
define each database table as the primary data structure. This class
gets instantiated for each table in the data getting frequent access.

One of the primary functions of this class is handling all the
datatype conversion. When using jsonb columns in postgres, there is no
datatype information. For strings and numbers this is fine, but not
for jsonb columns. Since the jsonb columns are also defined by the
same yaml config files all the other tables use, it's possible to get
the datatype of each value in the jsonb array. Normally this would be
unnecessary, but enums get lost in a jsonb column. The conversion
process when querying for data can optionally convert all of the
integer values for the enums to their string equivalant.

## Database Functions

This class has support for managing the database tables. This includes
creating, updating, or deleting record in a table. Common queries for
quering by ID or name are also included, so they can be shared amongst
the *api.py* modules.

Python dictionaries are heavily used as a parameter. All of the
generated data structures use a similar naming convention, so all the
data structures are very dynamic. Any change to the yaml config files
gets propogated to all the language bindings. Enum values are used
everywhere, improving the code readability.

## Inserting A Record

For example, to insert or update a record in the *projects* table,
use the generated **ProjectsTable** class. The *insertRecords()*
function can take a list of new records, but our examples just passes
one. In this example, **GRID**, **DRAFT**, and **INTERMEDIATE** are
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

## Quering The Database

As the database schema is reasonably complex, with a mix of arrays and
jsob columns, the API supports basic querying operations. Much
database accesss is querying or changing a single colum, so any
handling of enum conversion is in the lower level. It is possible to
get the raw output as well with no conversion at all. In that case it
has to be handled by calling code.

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
team ID is 144:

    foo = {'teams': {"role": tm_admin.types_tm.Teamroles.TEAM_READ_ONLY, "team_id": 144}}
    data = await pgs.getColumns(['id', 'teams'], [foo])

## Updating a Record

Updating a record is similar to insterting one, the same data
structure is used. Only the columns that need to be updated have to be
specified. And of course a WHERE condtion to limit what gets updates.

