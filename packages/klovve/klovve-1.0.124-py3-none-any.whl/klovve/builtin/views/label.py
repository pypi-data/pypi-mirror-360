#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
See :py:class:`Label`.
"""
import enum

import klovve


class Label(klovve.ui.Piece):
    """
    A label.
    """

    #: The label text.
    text: str = klovve.ui.property(initial="")

    class Style(enum.Enum):
        """
        Label styles.
        """

        #: Normal.
        NORMAL = enum.auto()
        #: Header.
        HEADER = enum.auto()
        #: Small.
        SMALL = enum.auto()
        #: Highlighted.
        HIGHLIGHTED = enum.auto()
        #: Warning.
        WARNING = enum.auto()
        #: Error.
        ERROR = enum.auto()

    #: The label style.
    style: Style = klovve.ui.property(initial=Style.NORMAL)

    horizontal_layout = klovve.ui.property(initial=klovve.ui.Layout(klovve.ui.Align.FILL))
    vertical_layout = klovve.ui.property(initial=klovve.ui.Layout(klovve.ui.Align.FILL))
