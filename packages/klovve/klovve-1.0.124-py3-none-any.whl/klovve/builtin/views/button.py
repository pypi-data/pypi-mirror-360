#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
See :py:class:`Button`.
"""
import enum

import klovve


class Button(klovve.ui.Piece):
    """
    A button.
    """

    #: The button text.
    text: str = klovve.ui.property(initial="")

    #: The name of the action that it triggers.
    action_name: str | None = klovve.ui.property()

    class Style(enum.Enum):
        """
        Button styles.
        """

        #: Normal button.
        NORMAL = enum.auto()
        #: Flat button.
        FLAT = enum.auto()
        #: Link-like button.
        LINK = enum.auto()

    #: The button style.
    style: Style = klovve.ui.property(initial=Style.NORMAL)

    horizontal_layout = klovve.ui.property(initial=klovve.ui.Layout(klovve.ui.Align.CENTER))
    vertical_layout = klovve.ui.property(initial=klovve.ui.Layout(klovve.ui.Align.CENTER))

    def _clicked(self):
        if action_name := self.action_name:
            self.trigger_event(klovve.app.BaseApplication.ActionTriggeredEvent(self, action_name))
