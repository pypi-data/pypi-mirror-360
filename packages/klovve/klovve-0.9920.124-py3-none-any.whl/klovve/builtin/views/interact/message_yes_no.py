#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import klovve.ui.utils
from klovve.builtin.views.interact.message import Message as _Message


class MessageYesNo(_Message[bool]):

    choices = klovve.ui.list_property(initial=lambda: (
        (klovve.ui.utils.tr("YES"), True),
        (klovve.ui.utils.tr("NO"), False)), is_settable=False)
