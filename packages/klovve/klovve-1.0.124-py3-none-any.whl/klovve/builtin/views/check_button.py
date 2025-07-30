#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
See :py:class:`CheckButton`.
"""
import enum

import klovve


class CheckButton(klovve.ui.Piece):
    """
    A check button.
    """

    #: The button text.
    text: str = klovve.ui.property(initial="")

    #: Whether this button is checked.
    is_checked: bool = klovve.ui.property(initial=False)

    class Style(enum.Enum):
        """
        Button styles.
        """

        #: Normal button.
        NORMAL = enum.auto()
        #: Flat button.
        FLAT = enum.auto()

    #: The button style.
    style: Style = klovve.ui.property(initial=Style.NORMAL)

    horizontal_layout = klovve.ui.property(initial=klovve.ui.Layout(klovve.ui.Align.CENTER))
    vertical_layout = klovve.ui.property(initial=klovve.ui.Layout(klovve.ui.Align.CENTER))

    def _clicked(self):
        self.is_checked = not self.is_checked
