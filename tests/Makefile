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

SQL := $(wildcard *.sql)
TESTS := $(wildcard test_*.py)

# Developer only! This requires a Tasking Manager database running on your local machine.
# This is used to update the test data if any changes to the TM database schema are made.
# As we want to use the existing table, we only insert data, and not create and columns.
DB=tm_admin
tmtestdata:
	@echo "Generating test data for users table..."
	-ogr2ogr /tmp/tm.sql PG:'dbname=$(DB)' -sql "SELECT * FROM users WHERE id='4606673'"
	-grep "INSERT INTO" /tmp/tm.sql | sed -e s/'"public"."sql_statement"'/users/ > tmusers.sql
	@echo "Generating test data for projects table..."
	-@ogr2ogr /tmp/tm.sql PG:'dbname=$(DB)' -sql "SELECT * FROM projects LIMIT 10"
	-@grep "INSERT INTO" /tmp/tm.sql | sed -e s/'"public"."sql_statement"'/projects/ > tmprojects.sql
	@echo "Generating test data for organizations table..."
	-@ogr2ogr /tmp/tm.sql PG:'dbname=$(DB)' -sql "SELECT * FROM organizations LIMIT 10"
	-@grep "INSERT INTO" /tmp/tm.sql | sed -e s/'"public"."sql_statement"'/organizations/ > tmorganizations.sql
	@echo "Generating test data for tasks table..."
	-@ogr2ogr /tmp/tm.sql PG:'dbname=$(DB)' -sql "SELECT * FROM tasks WHERE (invalidation_history).mapper_id IS NOT NULL"
	-@grep "INSERT INTO" /tmp/tm.sql | sed -e s/'"public"."sql_statement"'/tasks/ > tmtasks.sql
	@echo "Generating test data for teams table..."
	-@ogr2ogr /tmp/tm.sql PG:'dbname=$(DB)' -sql "SELECT * FROM teams LIMIT 10"
	-@grep "INSERT INTO" /tmp/tm.sql | sed -e s/'"public"."sql_statement"'/teams/ > tmteams.sql
	@echo "Generating test data for campaigns table..."
	-@ogr2ogr /tmp/tm.sql PG:'dbname=$(DB)' -sql "SELECT * FROM campaigns LIMIT 10"
	-@grep "INSERT INTO" /tmp/tm.sql | sed -e s/'"public"."sql_statement"'/campaigns/ > tmcampaigns.sql
	@echo "Generating test data for messages table..."
	-@ogr2ogr /tmp/tm.sql PG:'dbname=$(DB)' -sql "SELECT * FROM messages LIMIT 10"
	-@grep "INSERT INTO" /tmp/tm.sql | sed -e s/'"public"."sql_statement"'/messages/ > tmmessages.sql

lint:
	-@pylint test_*.py

import:
	-for i in $(SQL); do \
		echo "Importing $${i} into testdata"; \
		psql -d testdata -f $${i}; \
	done

check:
	for test in $(TESTS); do \
         echo "Running test $${test}..."; \
	    ./$${test} ; \
	done
force:
