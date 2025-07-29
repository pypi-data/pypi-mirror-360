#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import enum

import klovve


class Label(klovve.ui.Piece):

    text: str = klovve.ui.property(initial="")

    class Style(enum.Enum):
        NORMAL = enum.auto()
        HEADER = enum.auto()
        SMALL = enum.auto()
        HIGHLIGHTED = enum.auto()
        WARNING = enum.auto()
        ERROR = enum.auto()

    style: Style = klovve.ui.property(initial=Style.NORMAL)

    horizontal_layout = klovve.ui.property(initial=klovve.ui.Layout(klovve.ui.Align.FILL))
    vertical_layout = klovve.ui.property(initial=klovve.ui.Layout(klovve.ui.Align.FILL))
