#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import klovve.builtin.drivers.gtk
from klovve.builtin.drivers.gtk import Gtk


class Scrollable(klovve.builtin.drivers.gtk.ViewMaterialization[klovve.views.Scrollable]):

    def create_native(self):
        gtk_scrolled = self.new_native(Gtk.ScrolledWindow, self.piece, hscrollbar_policy=Gtk.PolicyType.NEVER)

        klovve.effect.activate_effect(klovve.builtin.drivers.gtk.ViewMaterialization.MaterializingViewEffect,
                                      (self, gtk_scrolled, lambda: self.piece.body), owner=self)

        return gtk_scrolled
