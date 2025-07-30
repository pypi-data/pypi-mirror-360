#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
See :py:class:`TextBlock`.
"""
import klovve


class TextBlock(klovve.ui.Piece):
    """
    A text block that shows formatted text (encoded in a subset of HTML).
    """

    #: The formatted text.
    text: str = klovve.ui.property(initial="")
