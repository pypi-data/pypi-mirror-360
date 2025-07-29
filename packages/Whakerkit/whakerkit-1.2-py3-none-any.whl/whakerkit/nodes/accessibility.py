# -*- coding: UTF-8 -*-
"""
:filename: whakerkit.nodes.accessibility.py
:author: Brigitte Bigi
:contact: contact@sppas.org
:summary: HTMLNode for the accessibility buttons

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

from whakerpy.htmlmaker import HTMLNode

import whakerkit
from whakerkit import _

# ---------------------------------------------------------------------------


MSG_ALT_CONTRAST = _("Contrast")
MSG_ALT_THEME = _("Color scheme")

# ---------------------------------------------------------------------------


class WhakerKitAccessibilityNavNode(HTMLNode):
    """Node for the accessibility nav of the website.

    """

    def __init__(self, parent: str):
        """Create the 'nav' node.

        :param parent: (str) The parent identifier node

        """
        super(WhakerKitAccessibilityNavNode, self).__init__(parent, "accessibility_nav", "nav")
        self.reset()

    # -----------------------------------------------------------------------

    def reset(self):
        """Reset the header to its default values."""
        self.clear_children()

        # Contrast Button
        button_contrast = HTMLNode(self.identifier, None, "button",
                                   attributes={"role": "menuitem",
                                               "onclick": "accessibility_manager.switch_contrast_scheme();"})
        self.append_child(button_contrast)
        img_contrast = HTMLNode(button_contrast.identifier, None, "img",
                                attributes={"src": whakerkit.sg.whakerexa + "icons/contrast_switcher.jpg",
                                            "alt": MSG_ALT_CONTRAST,
                                            "id": "img-contrast"})
        button_contrast.append_child(img_contrast)

        # Color Theme Button
        button_theme = HTMLNode(self.identifier, None, "button",
                                attributes={"role": "menuitem",
                                            "onclick": "accessibility_manager.switch_color_scheme();"})
        self.append_child(button_theme)
        img_theme = HTMLNode(button_theme.identifier, None, "img",
                             attributes={"src": whakerkit.sg.whakerexa + "icons/theme_switcher.png",
                                         "alt": MSG_ALT_THEME,
                                         "id": "img-theme"})
        button_theme.append_child(img_theme)
