#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import enum

import klovve


class BusyAnimation(klovve.ui.Piece):

    class Orientation(enum.Enum):
        HORIZONTAL = enum.auto()
        VERTICAL = enum.auto()

    orientation: Orientation = klovve.ui.property(initial=Orientation.VERTICAL)

    text: str|None = klovve.ui.property(initial=None)

    is_active: bool = klovve.ui.property(initial=True)

    def _(self):
        return self.text or ""
    _text_str: str = klovve.ui.computed_property(_)

    def _(self):
        return len(self._text_str) > 0
    _has_text: bool = klovve.ui.computed_property(_)
