#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import pathlib

import klovve.ui.utils


class Pdf(klovve.ui.Piece):

    source: pathlib.Path|None = klovve.ui.property()

    @property
    def _fallback_text(self) -> str:
        return klovve.ui.utils.tr("PLEASE_FIND_THE_DOCUMENT_HERE")
