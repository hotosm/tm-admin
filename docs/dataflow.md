# TM-Admin Data Flow

## Generated files

This project attempts to minimise code duplication. It is designed to
be a module for use in other projects. Because this project works with
but gRPC messages and a postgres database, and changes to any of the
data structures would require making changes in multiple
places. Instead a single file in YAML format is used to generate all
the other formats. This way changes only have to be made in one place. 

It does make the code more complicated, lots of layers of generated
code stubs to dig through when debugging. I've also tried to avoid
hacks in the code, and make it flexible to changes. That often
involves lots of looping through various data, but it's still pretty
fast. 

### Generating the files

To generate the files, there is a standalone python class, which also
has a simple command line interface and can be run offline. The
*generate.py* file reads in the YAML config files, and creates an
internal data structure for that file. More information on the config file
[is here](configuring.md).

The actual database schemas are created from the generated SQL
files. The *tmadmin-manage.py* file has a class that also runs
standalone and generates all the SQL, python, and protobuf files using
the *Generate* class. Once it generates the SQL files, it creates the
database and tables.

The protobuf files need to be compiled using **protoc**. This is
easiest done using the *Makefile*. since it has to include the types
for the complication to succeed.

Since there are a lot of generated files, they are all in a
subdirectory. Each directory is for each table in the database, and
all generated files go there.

### Datatypes

There are multiple shared enums, and are defined in the *types.yaml*
file. These become enums for postgres, python, and protobuf. After
generating the files, there is *types_tm.sql*, *types_tm.py*, and a
*types_tm.proto* for the protobuf files gRPC uses. These can be included
in any of the other classes that create data types. Having portable
data strucures that can be shared is critical. Otherwise any changes
would require editing multiple places. Having a single definition
reduces maintaince.

### The Python files

There are python source files generated for each database table. These
define all the data structures so they are easily accessible. The
enums are in the *types_tm.py* file.

The other two files are classes that define the full data for SQL
queries, as well as the reduced dataset used in inter-project data
exchange using gRPC. Using the table name, these become *table*Table
or *table*Message. The class files are for storing the data for a
table. The *table*Message classes are the reduced datasets for
exchanging data. Not all data in a database is useful in multiple
projects, so this uses a setting in the YAML config file to not have
all columns in the gRPC message.

Each table also has a class designed for accessing the database. This
file is not generated. This uses the other generated python files for
the data structures. This handles creating the entries for the tables,
and also has a few common queries, like search by ID. Most of the
higher level processing will be handled by the project importing this
module since it's possible to get the full data for furthur
processing. This is to make it a less painful refactoring of an
existing project backend. Many projects have existing tests of the
values in the database columns, so this is still possible.

#### Instantiating an object

The generated python files allow for default values for all the
database tables, and conditional parameters in python. With each top
level class for a tables, 

For example:
	ut = UsersTable(name='fixme', mapping_level='BEGINNER')

Creates a dictionary in the class with all of the keywords from the
YAML file. but will set these two columns to these values. This is
used for both creating entries in the database, but also for updating
them. This handles multiple optional parameters allowing this data
object to be used for data exchange in a consistent fashion.

### SQL files

The SQL files are designed to work with postgres for creating the
database, and it's tables and data types. The config file format
allows for setting each column as an auto incrementing column (good
for IDs), setting thst are required, so become 'NOT NULL'. And also a
unique columns, which is used for an INSERT that may trigger a
conflict. This is useful to update existing data.

### Protobuf files

The protobuf files are used by gRPC to exchange data. The *protoc*
compiler produces other wrappers as python code for the data
structures. These also use the table name as the prefix, and creates
*table*_pb2.py or *table*_pb2_grpc.py. These are used with gRPC. The
other generated python class are designed to interface with these,
since they need data structures to exchange.
