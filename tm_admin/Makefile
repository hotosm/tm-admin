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
YAML := $(wildcard */*.yaml)
OUTSQL := $(YAML:.yaml=.sql)

GRPC = --grpc_python_out=. --plugin=protoc-gen-grpc_python=/usr/bin/grpc_python_plugin

all:  support generate create

# The SQL files are now generated from YAML based config files
generate: support $(OUTSQL)

support: $(PBUFS)
	@echo "Generating the types files"
	-@./generator.py types.yaml -v
	@echo "Build services"
	-@$(PROTOC) -I. --python_out=. $(GRPC) services.proto

#-@$(PROTOC) -I. --python_out=. --pyi_out=. services.proto
# --plugin=protoc-gen-grpc_python=/usr/local/bin/grpc_python_plugin

docs:
	-$(PROTOC) --doc_out=../docs --doc_opt=html,protos-api.html  --proto_path . services.proto types_tm.proto */*.proto
#protoc --doc_out=./foo --doc_opt=html,index.html services.proto */*.proto
#-@cd .. && make apidoc

%.sql: %.yaml
	@echo "Generating $@ file for postgres"
	-@./generator.py $<

%.py: %.proto
	@echo "Converting $< to a protobuf python stubs file"
	-@$(PROTOC) -I. --python_out=. $(GRPC) types_tm.proto  $*.proto
# @FIXME: --pyi_out= seems to have been replaced by --grpc_python_out
# @-@$(PROTOC) -I. --python_out=. --pyi_out=. types.proto $*.proto

# Note that this requires the person running make has access to
# postgres without a user name or password required.
create:
	@echo "Creating the tm_admin database"
	-@createdb tm_admin
	-@./tmadmin_manage.py -v -c create */*.sql

# Note that this can take considerable time, like hours or days, so
# plan ahead.
import:
	dirs="`find -type d`"; \
	for i in $$dirs; do \
		if test -e $$i/$$i.yaml; then \
			./tmdb.py -v -i localhost/tm4 -o localhost/tm_admin -t $$i; \"; \
		fi; \
	done

clean:
	@echo "Removing all generated files!"
	$(RM) -f $(GENP) $(PYI) $(PROTOS) $(SQL) types_tm* services_pb2* */*_proto.py */*_class.py */*.cover

realclean: clean
	@$(RM) -f *~ */*~ rm -fr __pycache__/ */rm -fr __pycache__/

datafiles:
	-pg_dump -d tm4 -t licenses --inserts > licenses.sql
	-pg_dump -d tm4 -t interests --inserts > interests.sql

force:
