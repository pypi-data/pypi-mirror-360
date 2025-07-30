#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
See :py:class:`Sidebar`.
"""
import klovve


class Sidebar(klovve.ui.Piece):
    """
    A sidebar.
    """

    #: The sidebar body.
    body: klovve.ui.View|None = klovve.ui.property()

    #: The sidebar width in 'em'.
    width_em: float = klovve.ui.property(initial=10)

    #: Whether this sidebar is currently collapsed.
    is_collapsed: bool = klovve.ui.property(initial=False)

    horizontal_layout = klovve.ui.property(initial=klovve.ui.Layout(klovve.ui.Align.FILL))

    def _toggle_collapsed(self):
        self.is_collapsed = not self.is_collapsed
