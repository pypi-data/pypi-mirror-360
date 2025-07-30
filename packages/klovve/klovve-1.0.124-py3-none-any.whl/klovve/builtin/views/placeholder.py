#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
See :py:class:`Placeholder`.
"""
import klovve


class Placeholder(klovve.ui.Piece):
    """
    A placeholder.

    It has no own representation and no own behavior, but displays its body view (or nothing, if there is none).
    """

    #: The body view.
    body: klovve.ui.View | None = klovve.ui.property()
