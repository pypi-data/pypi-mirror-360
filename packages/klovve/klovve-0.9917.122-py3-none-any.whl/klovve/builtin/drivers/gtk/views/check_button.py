#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import klovve.builtin.drivers.gtk
from klovve.builtin.drivers.gtk import Gtk


class CheckButton(klovve.builtin.drivers.gtk.ViewMaterialization[klovve.views.CheckButton]):

    def create_native(self):
        gtk_box = self.new_native(Gtk.Box, self.piece)

        gtk_box.append(self.new_native(
            Gtk.ToggleButton, label=self.piece.bind.text, active=self.piece.bind.is_checked,
            hexpand=True, vexpand=True, halign=Gtk.Align.FILL, valign=Gtk.Align.FILL,
            visible=self.bind._is_toggle_button_visible))
        gtk_box.append(self.new_native(
            Gtk.CheckButton, label=self.piece.bind.text, active=self.piece.bind.is_checked,
            hexpand=True, vexpand=True, halign=Gtk.Align.FILL, valign=Gtk.Align.FILL,
            visible=self.bind._is_check_button_visible))

        return gtk_box

    def _(self):
        return self.piece.style == klovve.views.CheckButton.Style.NORMAL
    _is_toggle_button_visible: bool = klovve.ui.computed_property(_)

    def _(self):
        return self.piece.style == klovve.views.CheckButton.Style.FLAT
    _is_check_button_visible: bool = klovve.ui.computed_property(_)
