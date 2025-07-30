#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import klovve


class Placeholder(klovve.ui.Piece):

    body: klovve.ui.View | None = klovve.ui.property()
