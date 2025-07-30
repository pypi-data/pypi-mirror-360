#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import klovve
from klovve.builtin.views.interact import _AbstractInteract


class TextInput(_AbstractInteract[str|None]):

    message: str = klovve.ui.property(initial="")

    suggestion: str = klovve.ui.property(initial="")
