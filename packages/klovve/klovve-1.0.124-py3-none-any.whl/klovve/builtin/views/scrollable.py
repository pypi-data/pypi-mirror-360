#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
See :py:class:`Scrollable`.
"""
import klovve


class Scrollable(klovve.ui.Piece):
    """
    A scrollable area.
    """

    #: The body view.
    body: klovve.ui.View | None = klovve.ui.property()
