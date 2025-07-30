#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import klovve


class TextBlock(klovve.ui.Piece):

    text: str = klovve.ui.property(initial="")
