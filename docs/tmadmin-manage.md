# TM Admin Manage Util

This utility program is the standalone interface to the tm-admin
project. It is responsible for creating the database and the tables,
and generating the [protobuf](https://protobuf.dev/) files for
[gRPC](https://grpc.io/).

Initially it is used to generate the SQL files for creating the
database and it's tables. These are created from a [YAML
based](https://yaml.org/) config file. That file is described in more
detail [in this document](configuring.md). This same YAML file is also
used to generate all the protobuf files that define each gRPC message,
and the python wrappers.

Once the SQL files have been generated, this program imports them into
the database. It can also handle database schema migrations.

	usage: config [-h] -v -d DIFF -u URI YAML files
	options:
	-h, --help            show this help message and exit
	-v [VERBOSE], --verbose [VERBOSE] verbose output
	-d DIFF, --diff DIFF  SQL file diff for migrations
	-u URI, --uri URI     Database URI

The Database URI defaults to *localhost/tm_admin*.
