# TM Admin

<!-- markdownlint-disable -->
<p align="center">
  <img src="https://github.com/hotosm/fmtm/blob/main/images/hot_logo.png?raw=true" style="width: 200px;" alt="HOT"></a>
</p>
<p align="center">
  <em>Administrative modules for Tasking Manager style projects.</em>
</p>
<p align="center">
  <a href="https://github.com/hotosm/tm-admin/actions/workflows/build.yml" target="_blank">
      <img src="https://github.com/hotosm/tm-admin/actions/workflows/build.yml/badge.svg" alt="Build">
  </a>
  <a href="https://github.com/hotosm/tm-admin/actions/workflows/build-ci.yml" target="_blank">
      <img src="https://github.com/hotosm/tm-admin/actions/workflows/build-ci.yml/badge.svg" alt="CI Build">
  </a>
  <a href="https://github.com/hotosm/tm-admin/actions/workflows/docs.yml" target="_blank">
      <img src="https://github.com/hotosm/tm-admin/actions/workflows/docs.yml/badge.svg" alt="Publish Docs">
  </a>
  <a href="https://github.com/hotosm/tm-admin/actions/workflows/publish.yml" target="_blank">
      <img src="https://github.com/hotosm/tm-admin/actions/workflows/publish.yml/badge.svg" alt="Publish">
  </a>
  <a href="https://github.com/hotosm/tm-admin/actions/workflows/pytest.yml" target="_blank">
      <img src="https://github.com/hotosm/tm-admin/actions/workflows/pytest.yml/badge.svg" alt="Test">
  </a>
  <a href="https://pypi.org/project/tm-admin" target="_blank">
      <img src="https://img.shields.io/pypi/v/tm-admin?color=%2334D058&label=pypi%20package" alt="Package version">
  </a>
  <a href="https://pypistats.org/packages/tm-admin" target="_blank">
      <img src="https://img.shields.io/pypi/dm/tm-admin.svg" alt="Downloads">
  </a>
  <a href="https://github.com/hotosm/tm-admin/blob/main/LICENSE" target="_blank">
      <img src="https://img.shields.io/github/license/hotosm/tm-admin.svg" alt="License">
  </a>
</p>

---

📖 **Documentation**: <a href="https://hotosm.github.io/tm-admin/" target="_blank">https://hotosm.github.io/tm-admin/</a>

🖥️ **Source Code**: <a href="https://github.com/hotosm/tm-admin" target="_blank">https://github.com/hotosm/tm-admin</a>

---

<!-- markdownlint-enable -->

This is a complicated project as it involves parsing and outputting
multiple file formats. This project uses [gRPC](https://grpc.io/) for
the low-level communication layer, which is below the REST API. This
way it can be used by multiple other project REST APIs for exchanging
data without massive refactoring of an existing API.

The database schema is based on the ones in use in the
[FMTM](https://hotosm.github.io/fmtm/) project, which were
originally based on the ones used by the [HOT Tasking
Manager](https://tasks.hotosm.org/). The schemas have years of
improvements on the data requirements of Tasking Manager style
projects. Not every column in a database table will be needed by each
project, they can be ignored. It should be entirely possible to use a
custom configuration file, but this is currently unsupported. (would
love a patch for this)

This project generates multiple files at runtime, so each is
organized into a sub-directory, one for each table. The program that
processes each configuration file is *generator.py*, which is part of
this project. This reads in a configuration file in YAML format, and
generates the output files for this configuration file. There is also a
class **Generator** that can be used by other projects.

These are the current modules supported by this project.

* users
* projects
* tasks
* organizations
* teams

## tmadmin-manage

The tmadmin-manage program is for higher-level data management. While
each class can be run standalone, that's more for testing &
development. This program is also both a standalone program, and a
class that can be used by other projects. This program will create the
database and tables for each module.

## Datatypes

Each database table has it's own configuration file. There is also a
top level one, *types.yaml* that generates the type definitions that
all the other files depend on. This becomes types_tm.sql,
types_tm.proto, and types_tm.py, and needs to be imported before the
other files.

## .yaml files

The YAML based config files are where everything gets defined. This
way a single configuration file can be used to generate multiple
output formats. In the case of this projects, that's SQL files for a
local postgres database, protobuf files for gRPC, and python source
files for data type definitions. There is more information on the
[configuration files here](configuring.md)

## .proto files

These define the messages used by gRPC, and are also generated from
the configuration files. Not every column in the database tables is in
a message. The fields that get send and received are defined in the
configuration file by adding *share: True* as a setting.

The .proto files then have to be compiled using
[protoc](https://grpc.io/docs/protoc-installation/), which 
generates the client and server stubs.

## .sql files

These define the messages used by gRPC, and are also generated from
the configuration files. These can be executed in postgres to create
the tables. The *tmadmin-manage* program uses these to create the
database tables.

