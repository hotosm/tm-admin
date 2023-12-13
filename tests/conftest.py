# Copyright (c) 2022, 2023 Humanitarian OpenStreetMap Team
#
# This file is part of tm-admin.
#
#     tm-admin is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     tm-admin is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with tm-admin.  If not, see <https:#www.gnu.org/licenses/>.
#
"""Configuration and fixtures for PyTest."""

import logging
import pytest


log = logging.getLogger(__name__)


def pytest_configure(config):
    """Configure pytest runs."""
    # Stop sqlalchemy logs
    sqlalchemy_log = logging.getLogger("sqlalchemy")
    sqlalchemy_log.propagate = False
