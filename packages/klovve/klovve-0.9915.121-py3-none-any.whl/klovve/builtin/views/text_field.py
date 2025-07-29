#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import klovve


class TextField(klovve.ui.Piece):

    text: str = klovve.ui.property(initial="")

    hint_text: str | None = klovve.ui.property()

    vertical_layout = klovve.ui.property(initial=klovve.ui.Layout(klovve.ui.Align.CENTER))
