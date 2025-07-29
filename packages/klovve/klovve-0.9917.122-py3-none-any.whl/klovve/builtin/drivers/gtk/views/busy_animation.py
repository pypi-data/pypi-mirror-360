#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import klovve.builtin.drivers.gtk
from klovve.builtin.drivers.gtk import Gtk


class BusyAnimation(klovve.builtin.drivers.gtk.ViewMaterialization[klovve.views.BusyAnimation]):

    def create_native(self):
        gtk_box = self.new_native(Gtk.Box, self.piece, orientation=self.bind._gtk_orientation)
        gtk_box.append(self.new_native(Gtk.Spinner, spinning=self.piece.bind.is_active, hexpand=True, vexpand=True,
                                       valign=Gtk.Align.FILL, halign=Gtk.Align.FILL))
        gtk_box.append(self.new_native(Gtk.Label, hexpand=True, vexpand=True,
                                       label=self.piece.bind(two_way=False)._text_str,
                                       visible=self.piece.bind(two_way=False)._has_text))

        return gtk_box

    def _(self):
        return {
            klovve.views.BusyAnimation.Orientation.HORIZONTAL: Gtk.Orientation.HORIZONTAL,
            klovve.views.BusyAnimation.Orientation.VERTICAL: Gtk.Orientation.VERTICAL,
        }[self.piece.orientation]
    _gtk_orientation: Gtk.Orientation = klovve.ui.computed_property(_)
