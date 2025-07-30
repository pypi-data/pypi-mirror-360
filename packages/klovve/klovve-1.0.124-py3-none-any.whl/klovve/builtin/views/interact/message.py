#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
See :py:class:`Message`.
"""
import klovve
from klovve.builtin.views.interact import AbstractInteract


class Message[TChoice](AbstractInteract[TChoice]):
    """
    An interact view with a message and some choices to pick from.
    """

    #: The message.
    message: str = klovve.ui.property(initial="")

    #: The choices. It is a list of :code:`str,TChoice` tuple (a textual representation and an arbitrary answer value).
    #: The default is just "OK" with an answer value of :code:`None` as only choice.
    choices: list[tuple[str, TChoice]] = klovve.ui.list_property(initial=lambda: ((klovve.ui.utils.tr("OK"), None),))
