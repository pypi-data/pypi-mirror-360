#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import klovve


class Form(klovve.ui.Piece):

    class Section(klovve.model.Model):

        label: str = klovve.model.property(initial="")

        body: klovve.ui.View|None = klovve.model.property()

    sections: list[Section|klovve.ui.View|str] = klovve.ui.list_property()
