#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import klovve.builtin.drivers.viwid

import viwid


class Label(klovve.builtin.drivers.viwid.ViewMaterialization[klovve.views.Label]):

    def create_native(self):
        return self.new_native(viwid.widgets.label.Label, self.piece, text=self.piece.bind.text,
                               foreground=self.bind(two_way=False)._foreground)

    def _(self):
        match self.piece.style:
            case klovve.views.Label.Style.HEADER:
                return "#000"
            case klovve.views.Label.Style.SMALL:
                return "#555"
            case klovve.views.Label.Style.HIGHLIGHTED:
                return "#00f"
            case klovve.views.Label.Style.WARNING:
                return "#a50"
            case klovve.views.Label.Style.ERROR:
                return "#c00"
    _foreground = klovve.ui.computed_property(_)
