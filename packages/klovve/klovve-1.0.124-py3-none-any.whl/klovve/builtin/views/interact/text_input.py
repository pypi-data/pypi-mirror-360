#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
See :py:class:`TextInput`.
"""
import klovve
from klovve.builtin.views.interact import AbstractInteract


class TextInput(AbstractInteract[str|None]):
    """
    An interact view with a message and a text field.

    The answer is the entered text, or :code:`None` if it was cancelled.
    """

    #: The message.
    message: str = klovve.ui.property(initial="")

    #: The suggestion text. This is the text that the text field is pre-filled with.
    suggestion: str = klovve.ui.property(initial="")
