#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import enum

import klovve


class Button(klovve.ui.Piece):

    text: str = klovve.ui.property(initial="")

    action_name: str | None = klovve.ui.property()

    class Style(enum.Enum):
        NORMAL = enum.auto()
        FLAT = enum.auto()
        LINK = enum.auto()

    style: Style = klovve.ui.property(initial=Style.NORMAL)

    horizontal_layout = klovve.ui.property(initial=klovve.ui.Layout(klovve.ui.Align.CENTER))
    vertical_layout = klovve.ui.property(initial=klovve.ui.Layout(klovve.ui.Align.CENTER))

    def _clicked(self):
        if action_name := self.action_name:
            self.trigger_event(klovve.app.BaseApplication.ActionTriggeredEvent(self, action_name))
