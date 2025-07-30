#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import klovve.builtin.drivers.viwid

import viwid


class Pdf(klovve.builtin.drivers.viwid.ViewMaterialization[klovve.views.viewer.Pdf]):

    def create_native(self):
        return self.new_native(viwid.widgets.label.Label, self.piece, text=self.bind._label_text)

    def _(self):
        return (f"{self.piece._fallback_text}\n\nfile://{self.piece.source.absolute()}"
                if (self.piece.source is not None) else "")
    _label_text: str = klovve.ui.computed_property(_)
