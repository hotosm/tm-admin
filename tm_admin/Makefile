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

all: generate compile

# The SQL files are now generated from YAML based config files
generate: $(OUTSQL)

compile: $(PBUFS)
	@echo "Build services"
	-@$(PROTOC) -I. --python_out=. $(GRPC) types_tm.proto services.proto
	#-@$(PROTOC) -I. --python_out=. --pyi_out=. services.proto
	# --plugin=protoc-gen-grpc_python=/usr/local/bin/grpc_python_plugin

docs:
	-$(PROTOC) --doc_out=../docs --doc_opt=html,protos-api.html services.proto types_tm.proto * */*.proto
	#protoc --doc_out=./foo --doc_opt=html,index.html services.proto */*.proto


%.sql: %.yaml
	@echo "Generating $@ file for postgres"
	-@./generator.py $<

%.py: %.proto
	@echo "Converting $< to a protobuf python stubs file"
	-@$(PROTOC) -I. --python_out=. $(GRPC) types_tm.proto  $*.proto
	@# FIXME: --pyi_out= seems to have been replaced by --grpc_python_out
	@#-@$(PROTOC) -I. --python_out=. --pyi_out=. types.proto $*.proto

clean:
	@echo "Removing all generated files!"
	$(RM) -f $(GENP) $(PYI) $(PROTOS) $(SQL) types_tm* services_pb2* */*_proto.py */*_class.py 

realclean: clean
	@$(RM) -f *~ */*~ rm -fr __pycache__/ */rm -fr __pycache__/


# Developer only! This requires a Tasking Manager database running on your local machine.
# This is used to update the test data if any changes to the TM database schema are made.
tmtestdata:
	@echo "Generating test data for users table..."
	-@ogr2ogr ../tests/tmusers.sql PG:'dbname=tm4' -sql "SELECT * FROM users LIMIT 10"
	-@sed -i -e '/ALTER/d' -e '/TABLE/d'  -e '/BEGIN/d' tmusers.sql
	@echo "Generating test data for projects table..."
	-@ogr2ogr ../tests/tmprojects.sql PG:'dbname=tm4' -sql "SELECT * FROM projects LIMIT 10"
	-@sed -i -e '/ALTER/d' -e '/TABLE/d'  -e '/BEGIN/d' -e '/CREATE/d' ../tests/tmprojects.sql
	@echo "Generating test data for organizations table..."
	-@ogr2ogr ../tests/tmorganizations.sql PG:'dbname=tm4' -sql "SELECT * FROM organisations LIMIT 10"
	-@sed -i -e '/ALTER/d' -e '/TABLE/d'  -e '/BEGIN/d' -e '/CREATE/d' ../tests/tmorganizations.sql
	@echo "Generating test data for tasks table..."
	-@ogr2ogr ../tests/tmtasks.sql PG:'dbname=tm4' -sql "SELECT * FROM tasks LIMIT 10"
	-@sed -i -e '/ALTER/d' -e '/TABLE/d'  -e '/BEGIN/d' -e '/SELECT/d'  -e '/CREATE/d' ../tests/tmtasks.sql
	@echo "Generating test data for teams table..."
	-@ogr2ogr ../tests/tmteams.sql PG:'dbname=tm4' -sql "SELECT * FROM teams LIMIT 10"
	-@sed -i -e '/ALTER/d' -e '/TABLE/d'  -e '/BEGIN/d' -e '/SELECT/d'  -e '/CREATE/d' ../tests/tmteams.sql

.SUFFIXES: .py .sql .yaml .proto

force:
