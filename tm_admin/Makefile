# Copyright (c) 2020, 2021 Humanitarian OpenStreetMap Team
#
# This file is part of Osm-RawData.
#
#     Osm-RawData is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     Osm-RawData is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with Osm-RawData.  If not, see <https:#www.gnu.org/licenses/>.
#

PACKAGE := org.tm-admin.py
NAME := tm-admin
VERSION := 0.1.0

PROTOC = protoc
SQL := $(wildcard */*.sql)
PROTOS :=  $(SQL:.sql=.proto)
PBUFS := $(PROTOS:.proto=.py)
GENP := $(wildcard */*_pb2.py)

all: protos compile
protos: $(SQL)
	./tmadmin-manage.py -v

compile: $(PBUFS)

%.py: %.proto
	@echo "Converting $< to a protobuf file"
	-@$(PROTOC) -I. --python_out=. types.proto $*.proto

clean:
	@echo "Removing all generated files!"
	$(RM) -f $(GENP) $(PROTOS) types_pb2.py types.proto

.SUFFIXES: .py .sql
