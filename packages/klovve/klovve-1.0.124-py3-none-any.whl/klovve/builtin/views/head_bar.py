#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
See :py:class:`HeadBar`.
"""
import enum

import klovve


class HeadBar(klovve.ui.Piece):
    """
    A head bar.
    """

    #: The title text.
    title: str = klovve.ui.property(initial="")

    #: The current progress. If :code:`None`, no progress bar is shown.
    progress: float|None = klovve.ui.property()

    #: Additional primary views.
    primary_header_items: list[klovve.ui.View] = klovve.ui.list_property()
    #: Additional secondary views.
    secondary_header_items: list[klovve.ui.View] = klovve.ui.list_property()

    class Style(enum.Enum):
        """
        Head bar styles.
        """

        #: Neutral.
        NEUTRAL = enum.auto()
        #: Busy.
        BUSY = enum.auto()
        #: Successful.
        SUCCESSFUL = enum.auto()
        #: Successful, but with warning(s).
        SUCCESSFUL_WITH_WARNING = enum.auto()
        #: Failed.
        FAILED = enum.auto()

    #: The head bar style.
    style: Style = klovve.ui.property(initial=Style.NEUTRAL)

    vertical_layout = klovve.ui.property(initial=klovve.ui.Layout(klovve.ui.Align.START))
