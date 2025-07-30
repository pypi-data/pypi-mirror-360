#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import klovve


class VerticalBox(klovve.ui.Piece):

    items: list[klovve.ui.View] = klovve.ui.list_property()
