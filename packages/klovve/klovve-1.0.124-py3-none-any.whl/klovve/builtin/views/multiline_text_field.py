#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
See :py:class:`MultilineTextField`.
"""
import klovve


class MultilineTextField(klovve.ui.Piece):
    """
    An editable multi-line text field.
    """

    #: The current text.
    text: str = klovve.ui.property(initial="")

    #: Whether to prefer monospaced rendering.
    is_monospaced: bool = klovve.ui.property(initial=True)
