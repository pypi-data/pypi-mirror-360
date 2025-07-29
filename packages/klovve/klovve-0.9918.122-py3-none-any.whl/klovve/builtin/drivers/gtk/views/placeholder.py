#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import klovve.builtin.drivers.gtk
import klovve.ui.utils
from klovve.builtin.drivers.gtk import Gtk


class Placeholder(klovve.builtin.drivers.gtk.ViewMaterialization[klovve.views.Placeholder]):

    def create_native(self):
        gtk_box = self.new_native(Gtk.Box, self.piece, layout_manager=Gtk.BinLayout())

        klovve.effect.activate_effect(klovve.builtin.drivers.gtk.ViewMaterialization.MaterializingViewEffect,
                                      (self, gtk_box, lambda: self.piece.body), owner=self)

        return gtk_box
