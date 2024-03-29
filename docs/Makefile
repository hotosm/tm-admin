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

DRAW := $(wildcard E2E/*.odt)
PNGS := $(DRAW:.odt=.png)
PDFS := $(DRAW:.odt=.pdf)

# Automate the building of pngs and pdfs from the libreoffice draw
# source files, insted of having to commit both to git after
# any changes.
all: pngs pdfs
	@echo "$(DRAW)"

pngs: $(PNGS)

pdfs: $(PDFS)

apidoc:
	-@doxygen

%.png: %.odt
	@echo "Generating $@ file for use in Markdown files"
	-libreoffice --draw --headless --convert-to png "$<"
	# -@mv *Profile.png images/

%.pdf: %.odt
	@echo "Generating $@ file for use in Markdown files"
	-libreoffice --draw --headless --convert-to pdf "$<"
	# -@mv *Profile.png images

clean:
	-$(RM) *.png *.pdf

force:
