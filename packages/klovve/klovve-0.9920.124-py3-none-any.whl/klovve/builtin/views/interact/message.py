#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import klovve
from klovve.builtin.views.interact import _AbstractInteract


class Message[TChoice](_AbstractInteract[TChoice]):

    message: str = klovve.ui.property(initial="")

    choices: list[tuple[str, TChoice]] = klovve.ui.list_property(initial=lambda: ((klovve.ui.utils.tr("OK"), None),))
