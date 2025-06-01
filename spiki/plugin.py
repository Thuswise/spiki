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


import dataclasses
import enum
from pathlib import Path


class Phase(enum.Enum):
    CONFIG = "Configuring framework"
    SURVEY = "Discovering topology"
    FILTER = "Selecting sources"
    ENRICH = "Attaching metadata"
    ASSETS = "Preparing media"
    RENDER = "Generating content"
    EXPORT = "Finalizing output"
    REPORT = "Summary"


@dataclasses.dataclass
class Event:
    object: object  = None
    phase:  Phase   = None
    path:   Path    = None
    text:   str     = None
    node:   dict    = None
    doc:    str     = None
    edits:  int     = 0


class Plugin:

    def __init__(self, visitor: "Pathfinder" = None):
        self.visitor = visitor
        self.phase = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False

    def __call__(self, phase: Phase, *, path: Path = None, node: dict = None, doc: str = None, **kwargs) -> Event:
        self.phase = phase
        if path is None:
            method = getattr(self, f"end_{phase.name.lower()}", None)
        else:
            method = getattr(self, f"do_{phase.name.lower()}", None)

        if method:
            return method(path=path, node=node, doc=doc, **kwargs)
        else:
            return False

    def register(self, visitor: "Pathfinder"):
        self.visitor = visitor
        return self
