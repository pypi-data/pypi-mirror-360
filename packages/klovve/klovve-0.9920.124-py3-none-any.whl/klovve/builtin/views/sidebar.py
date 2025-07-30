#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import klovve


class Sidebar(klovve.ui.Piece):

    body: klovve.ui.View|None = klovve.ui.property()

    width_em: float = klovve.ui.property(initial=10)

    is_collapsed: bool = klovve.ui.property(initial=False)

    horizontal_layout = klovve.ui.property(initial=klovve.ui.Layout(klovve.ui.Align.FILL))

    def _toggle_collapsed(self):
        self.is_collapsed = not self.is_collapsed
