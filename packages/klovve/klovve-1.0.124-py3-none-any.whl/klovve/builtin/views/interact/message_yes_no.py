#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
See :py:class:`MessageYesNo`.
"""
import klovve.ui.utils
from klovve.builtin.views.interact.message import Message as _Message


class MessageYesNo(_Message[bool]):
    """
    Same as :py:class:`klovve.builtin.views.interact.message.Message`, but with the two choices "Yes" (:code:`True`) and
    "No" (:code:`False`).
    """

    choices = klovve.ui.list_property(initial=lambda: (
        (klovve.ui.utils.tr("YES"), True),
        (klovve.ui.utils.tr("NO"), False)), is_settable=False)
