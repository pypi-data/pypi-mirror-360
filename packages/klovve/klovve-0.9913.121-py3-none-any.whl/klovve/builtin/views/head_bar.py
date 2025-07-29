#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import enum

import klovve


class HeadBar(klovve.ui.Piece):

    title: str = klovve.ui.property(initial="")

    progress: float|None = klovve.ui.property()

    primary_header_items: list[klovve.ui.View] = klovve.ui.list_property()
    secondary_header_items: list[klovve.ui.View] = klovve.ui.list_property()

    class Style(enum.Enum):
        NEUTRAL = enum.auto()
        BUSY = enum.auto()
        SUCCESSFUL = enum.auto()
        SUCCESSFUL_WITH_WARNING = enum.auto()
        FAILED = enum.auto()

    style: Style = klovve.ui.property(initial=Style.NEUTRAL)

    vertical_layout = klovve.ui.property(initial=klovve.ui.Layout(klovve.ui.Align.START))
