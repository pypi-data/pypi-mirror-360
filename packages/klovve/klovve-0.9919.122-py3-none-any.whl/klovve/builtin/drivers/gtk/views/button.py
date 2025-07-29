#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import typing as t

import klovve.builtin.drivers.gtk
from klovve.builtin.drivers.gtk import Gtk


class Button(klovve.builtin.drivers.gtk.ViewMaterialization[klovve.views.Button]):

    def create_native(self):
        gtk_button = self.new_native(Gtk.Button, self.piece, label=self.piece.bind.text,
                                     css_classes=self.bind._css_classes)

        gtk_button.connect("clicked", lambda *_: self.piece._clicked())

        return gtk_button

    def _(self):
        if self.piece.style == klovve.views.Button.Style.FLAT:
            return ("flat",)
        elif self.piece.style == klovve.views.Button.Style.LINK:
            return ("flat", "klv_button_link")
        return ()
    _css_classes: t.Iterable[str] = klovve.ui.computed_property(_)
