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

import logging

from spiki.plugin import Phase
from spiki.plugin import Plugin


class Indexer(Plugin):

    def __call__(self, node: dict, phase: Phase, **kwargs) -> bool:
        logger = logging.getLogger("indexer")
        logger.info(node["registry"]["node"], extra=dict(phase=phase))
        return False
