#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import klovve


class Image(klovve.ui.Piece):

    source: bytes|None = klovve.ui.property()
