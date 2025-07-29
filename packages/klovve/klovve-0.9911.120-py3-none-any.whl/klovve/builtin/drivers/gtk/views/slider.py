#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import klovve.builtin.drivers.gtk
from klovve.builtin.drivers.gtk import Gtk


class Slider(klovve.builtin.drivers.gtk.ViewMaterialization[klovve.views.Slider]):

    def create_native(self):
        gtk_scale = self.new_native(Gtk.Scale, self.piece)

        klovve.effect.activate_effect(self.__refresh_ui, (gtk_scale,), owner=self)
        gtk_scale.connect("value_changed", lambda *_: self.__refresh_piece(gtk_scale))

        return gtk_scale

    def __refresh_ui(self, gtk_scale):
        gtk_scale.set_range(self.piece.min_value, self.piece.max_value)
        gtk_scale.set_increments(self.piece.value_step_size, 0)
        gtk_scale.set_value(self.piece.value)

    def __refresh_piece(self, gtk_scale):
        self.piece.value = gtk_scale.get_value()
