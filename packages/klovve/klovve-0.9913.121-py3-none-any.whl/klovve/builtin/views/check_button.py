#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import enum

import klovve


class CheckButton(klovve.ui.Piece):

    text: str = klovve.ui.property(initial="")

    is_checked: bool = klovve.ui.property(initial=False)

    class Style(enum.Enum):
        NORMAL = enum.auto()
        FLAT = enum.auto()

    style: Style = klovve.ui.property(initial=Style.NORMAL)

    horizontal_layout = klovve.ui.property(initial=klovve.ui.Layout(klovve.ui.Align.CENTER))
    vertical_layout = klovve.ui.property(initial=klovve.ui.Layout(klovve.ui.Align.CENTER))

    def _clicked(self):
        self.is_checked = not self.is_checked
