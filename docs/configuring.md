# Configuring The Data Structures

For any project that needs to transmit data between multiple projects,
there needs to be a single source of data structures and type
definitions. Otherwise there winds up being a lot of code duplication
which becomes hard to maintain.

This project also needs to manage the database tables, as well as
allow to transmit data between projects. Python enums and classes are
also generated.

# The YAML files

This file is used to generate the full SQL to create database
tables, as well as the protobuf files. The first field becomes the
name of the tables in postgres, or the message in the .proto
file. Each table is then followed by a list of fields.
Each field has a few settings, the data type, and a few settings.

For example:

	- users:
		- id:
			- int64
			- required: True
			- share: True
			- sequence: True
	 ...

## required

If this is True, then for the database table, this becomes *NOT NULL*
in the SQL schema. This is ignored when generating the protobuf file.

## sequence

If this is *True*, then this becomes an auto incrementing sequence in
SQL. This is ignored when generating the protobuf file.

## share

Not every field needs to be transfered to other projects, as some are
project specific, like how many tasks have been mapped. If this is
*True*, then it will have an entry in the protobuf message. The
default is *True*. To have a field not appear in the protobuf message,
this needs to be set to *False*.

## array

If this is *True*, then in the database schema this becomes an
array. In the protobuf file, this adds the *repeated* keyword in the
message to define this field as an array.
