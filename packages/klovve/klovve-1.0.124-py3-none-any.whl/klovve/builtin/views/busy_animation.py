#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
See :py:class:`BusyAnimation`.
"""
import enum

import klovve


class BusyAnimation(klovve.ui.Piece):
    """
    A busy animation.
    """

    class Orientation(enum.Enum):
        """
        The orientation.
        """

        #: Horizontal orientation.
        HORIZONTAL = enum.auto()
        #: Vertical orientation.
        VERTICAL = enum.auto()

    #: The orientation (of the animation itself and the text).
    orientation: Orientation = klovve.ui.property(initial=Orientation.VERTICAL)

    #: The text.
    text: str|None = klovve.ui.property(initial=None)

    #: Whether the animation is currently active (or paused).
    is_active: bool = klovve.ui.property(initial=True)

    def _(self):
        return self.text or ""
    _text_str: str = klovve.ui.computed_property(_)

    def _(self):
        return len(self._text_str) > 0
    _has_text: bool = klovve.ui.computed_property(_)
