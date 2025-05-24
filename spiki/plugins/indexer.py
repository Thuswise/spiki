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
from collections import defaultdict
import itertools
import logging
from pathlib import Path
import tomllib

from spiki.pathfinder import Pathfinder
from spiki.plugin import Phase
from spiki.plugin import Plugin


class Indexer(Plugin):

    def __init__(self, visitor):
        super().__init__(visitor)
        self.logger = logging.getLogger("indexer")
        self.indexes = {}

    def do_survey(self, path: Path = None, node: dict = None, doc: str = None, **kwargs) -> bool:
        if path.name == self.visitor.index_name:
            self.logger.info(node["registry"]["path"], extra=dict(phase=self.phase))
            key = node["registry"]["node"]
            self.indexes[key] = node
            return True
        else:
            return False

    def end_survey(self, path: Path = None, node: dict = None, doc: str = None, **kwargs) -> bool:
        return False

    def do_enrich(self, path: Path = None, node: dict = None, doc: str = None, **kwargs) -> bool:
        ancestors = self.visitor.ancestors(path)
        root_path = ancestors[0]
        home_path = ancestors[-1]

        try:
            root_node = self.visitor.nodes[root_path]
            root_url = self.visitor.url_of(root_node)
            home_node = self.visitor.nodes[home_path]
            home_url = self.visitor.url_of(home_node)
            text = f"""
            [doc.html.body.nav]
            config = {{tag_mode = "pair"}}
            [doc.html.body.nav.header.ul]
            [[doc.html.body.nav.header.ul.li]]
            attrib = {{class = "spiki root", href = "/{root_url}"}}
            a = "{root_node['metadata']['title']}"
            [[doc.html.body.nav.header.ul.li]]
            attrib = {{class = "spiki home", href = "/{home_url}"}}
            a = "{home_node['metadata']['title']}"
            [doc.html.body.nav.ul]
            [doc.html.body.nav.footer.ul]
            """
            data = tomllib.loads(text)
            self.visitor.nodes[path] = self.visitor.combine(data, node)
            return True
        except (KeyError, StopIteration) as error:
            return False

    def end_enrich(self, path: Path = None, node: dict = None, doc: str = None, **kwargs) -> bool:
        rv = False

        def key(node):
            "Sort nodes by path parts"
            return node["registry"]["node"]

        # TODO
        # Inter-index links
        # Sibling links
        for k, group in itertools.groupby(sorted(self.visitor.nodes.values(), key=key), key=key):
            siblings = {i["registry"]["path"].name: i for i in group}
            index_node = siblings.pop(self.visitor.index_name, None)

            if index_node is not None:
                # Add down link to ancestor of index node
                try:
                    down_url = self.visitor.url_of(index_node)
                    path = index_node["registry"]["path"]
                    ancestors = self.visitor.ancestors(path)
                    back_path = ancestors[-2]
                    back_node = self.visitor.nodes[back_path]
                    back_url = self.visitor.url_of(back_node)
                    text = f"""
                    [doc.html.body.nav]
                    config = {{tag_mode = "pair"}}
                    [doc.html.body.nav.header.ul]
                    [doc.html.body.nav.ul]
                    [doc.html.body.nav.footer.ul]
                    [[doc.html.body.nav.footer.ul.li]]
                    attrib = {{class = "spiki down", href = "/{down_url}"}}
                    a = "{index_node['metadata']['title']}"
                    """
                    data = tomllib.loads(text)
                    self.visitor.nodes[back_path] = self.visitor.combine(data, back_node)
                    rv = True
                except IndexError:
                    # No ancestor for index
                    pass
                except (KeyError, StopIteration) as error:
                    self.logger.warning(error, extra=dict(phase=phase), exc_info=True)

            for n, node in enumerate(siblings.values()):
                path = node["registry"]["path"]
                ancestors = self.visitor.ancestors(path)

                # Add node link to back index
                try:
                    here_url = self.visitor.url_of(node)
                    back_path = ancestors[-1]
                    back_node = self.visitor.nodes[back_path]
                    text = f"""
                    [doc.html.body.nav]
                    config = {{tag_mode = "pair"}}
                    [[doc.html.body.nav.ul.li]]
                    attrib = {{class = "spiki here", href = "/{here_url}"}}
                    a = "{node['metadata']['title']}"
                    """
                    data = tomllib.loads(text)
                    if back_path != path:
                        self.visitor.nodes[back_path] = self.visitor.combine(data, back_node)
                        rv = True
                except (KeyError, StopIteration) as error:
                    self.logger.warning(error, extra=dict(phase=phase), exc_info=True)

                # Add sibling links to node
                try:
                    l_node = siblings[list(siblings)[n - 1]]
                    l_url = self.visitor.url_of(l_node)
                    r_node = siblings[list(siblings)[(n + 1) % len(siblings)]]
                    r_url = self.visitor.url_of(r_node)
                    text = f"""
                    [doc.html.body.nav]
                    config = {{tag_mode = "pair"}}
                    [[doc.html.body.nav.ul.li]]
                    attrib = {{class = "spiki here", href = "/{l_url}"}}
                    a = "{l_node['metadata']['title']}"
                    """

                    if l_url != r_url:
                        text += f"""
                        [[doc.html.body.nav.ul.li]]
                        attrib = {{class = "spiki here", href = "/{r_url}"}}
                        a = "{r_node['metadata']['title']}"
                        """
                    data = tomllib.loads(text)
                    if len(siblings) > 1:
                        self.visitor.nodes[path] = self.visitor.combine(data, node)
                        rv = True
                except (KeyError, StopIteration) as error:
                    self.logger.warning(error, extra=dict(phase=phase), exc_info=True)

        return rv

    def do_report(self, path: Path = None, node: dict = None, doc: str = None, **kwargs) -> bool:
        self.logger.info(f"{list(self.indexes)=}", extra=dict(phase=phase))
        return False

    def end_report(self, path: Path = None, node: dict = None, doc: str = None, **kwargs) -> bool:
        return False
        return rv

    def do_report(self, path: Path = None, node: dict = None, doc: str = None, **kwargs) -> bool:
        self.logger.info(f"{list(self.indexes)=}", extra=dict(phase=phase))
        return False

    def end_report(self, path: Path = None, node: dict = None, doc: str = None, **kwargs) -> bool:
        return False
