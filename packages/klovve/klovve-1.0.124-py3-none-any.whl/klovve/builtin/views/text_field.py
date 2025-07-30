#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
See :py:class:`TextField`.
"""
import klovve


class TextField(klovve.ui.Piece):
    """
    An editable single-line text field.
    """

    #: The current text.
    text: str = klovve.ui.property(initial="")

    #: The hint text. This is displayed (in a modest colouring) when the text field is empty.
    hint_text: str | None = klovve.ui.property()

    vertical_layout = klovve.ui.property(initial=klovve.ui.Layout(klovve.ui.Align.CENTER))
