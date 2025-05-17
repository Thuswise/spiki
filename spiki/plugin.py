#!/usr/bin/env python
#   encoding: utf-8

# Copyright (C) 2025 D E Haynes
# This file is part of spiki.

# Spiki is free software: you can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.
#
# Spiki is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even
# the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with spiki.
# If not, see <https://www.gnu.org/licenses/>.


import argparse
import enum


class Phase(enum.Enum):
    SURVEY = "Discovering topology"
    ASSETS = "Identifying media"
    ENRICH = "Attaching metadata"
    RENDER = "Generating document"


class Plugin:

    def __init__(self, args: argparse.Namespace = None):
        self.args = args or argparse.Namespace()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False

    def __call__(self, node: dict, phase: Phase, **kwargs):
        return True
