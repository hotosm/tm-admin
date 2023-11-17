# Copyright (c) 2023 Humanitarian OpenStreetMap Team
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# Humanitarian OpenStreetmap Team
# 1100 13th Street NW Suite 800 Washington, D.C. 20005
# <info@hotosm.org>

PACKAGE := org.tm-admin.py
NAME := tm-admin
VERSION := 0.1.0

PROTOC = python -m grpc_tools.protoc

SQL := $(wildcard */*.sql)
PROTOS :=  $(SQL:.sql=.proto)
PBUFS := $(PROTOS:.proto=.py)
GENP := $(wildcard */*_pb2*.py*)

all: protos compile

protos: $(SQL) services.proto
	./tmadmin-manage.py -v */*.sql

compile: $(PBUFS)
	@echo "Build services"
	-@$(PROTOC) -I. --python_out=. --grpc_python_out=. services.proto

%.py: %.proto
	@echo "Converting $< to a protobuf file"
	-@$(PROTOC) -I. --python_out=. --grpc_python_out=. types.proto  $*.proto
	@# FIXME: --pyi_out= seems to have been replaced by --grpc_python_out
	@#-@$(PROTOC) -I. --python_out=. --pyi_out=. types.proto $*.proto

clean:
	@echo "Removing all generated files!"
	$(RM) -f $(GENP) $(PYI) $(PROTOS) types_pb2* types_tm.* services_pb2*

realclean: clean
	@$(RM) -f *~ */*~


.SUFFIXES: .py .sql
