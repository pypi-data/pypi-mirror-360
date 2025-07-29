# -*- coding: UTF-8 -*-
"""
:filename: whakerkit.nodes.header_node.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: HTMLNode for the header

Copyright (C) 2024-2025 Brigitte Bigi, CNRS
Laboratoire Parole et Langage, Aix-en-Provence, France

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

This banner notice must not be removed.

"""

import os

from whakerpy.htmlmaker import HTMLNode
from whakerpy.htmlmaker import HTMLHeaderNode

import whakerkit
from whakerkit import _

from .accessibility import WhakerKitAccessibilityNavNode

# ---------------------------------------------------------------------------


MSG_SKIP = _("Skip to main content")

# ---------------------------------------------------------------------------


class WhakerKitHeaderNode(HTMLHeaderNode):
    """Node for the header of the website.

    It contains the welcome message and the accessibility buttons.

    """

    def __init__(self, parent: str):
        """Create the header node.

        :param parent: (str) The parent identifier node

        """
        super(WhakerKitHeaderNode, self).__init__(parent)
        self.reset()
        self.set_attribute("id", "header-content")

    # -----------------------------------------------------------------------

    def reset(self):
        """Reset the header to its default values."""
        self.clear_children()

        # Skip button -- for accessibility
        a = HTMLNode(self.identifier, None, "a", value=MSG_SKIP)
        a.set_attribute("role", "button")
        a.set_attribute("class", "skip")
        a.set_attribute("href", "#main-content")
        self.append_child(a)

        # Header title
        header_filename = whakerkit.sg.path + "html/header.htm"
        if os.path.exists(header_filename) is True:
            with open(header_filename, encoding="utf-8") as html_file:
                self.set_value(html_file.read())

        # Color & Scheme buttons -- for accessibility
        nav = WhakerKitAccessibilityNavNode(self.identifier)
        self.append_child(nav)
