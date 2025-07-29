#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import klovve.builtin.drivers.gtk
from klovve.builtin.drivers.gtk import Gtk


class Label(klovve.builtin.drivers.gtk.ViewMaterialization[klovve.views.Label]):

    def create_native(self):
        return self.new_native(Gtk.Label, self.piece, wrap=True, label=self.piece.bind.text,
                               css_classes=self.bind(two_way=False)._css_classes)

    def _(self):
        result = []
        match self.piece.style:
            case klovve.views.Label.Style.HEADER:
                result.append("klv_label__header")
            case klovve.views.Label.Style.SMALL:
                result.append("klv_label__small")
            case klovve.views.Label.Style.HIGHLIGHTED:
                result.append("klv_label__highlighted")
            case klovve.views.Label.Style.WARNING:
                result.append("klv_label__warning")
            case klovve.views.Label.Style.ERROR:
                result.append("klv_label__error")
        return result
    _css_classes = klovve.ui.computed_property(_)
