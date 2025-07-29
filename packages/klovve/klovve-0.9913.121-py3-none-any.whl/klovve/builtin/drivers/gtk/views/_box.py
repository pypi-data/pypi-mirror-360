#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import abc

import klovve.builtin.drivers.gtk
import klovve.ui.utils
from klovve.builtin.drivers.gtk import Gtk


class Box[_T](klovve.builtin.drivers.gtk.ViewMaterialization[_T], abc.ABC):

    @property
    @abc.abstractmethod
    def _orientation(self) -> Gtk.Orientation:
        pass

    def create_native(self):
        gtk_box = self.new_native(Gtk.Box, self.piece, orientation=self._orientation)

        self.piece._introspect.observe_list_property(
            self.piece._introspect.property_by_name("items"),
            self.MaterializingViewsInGtkBoxObserver, (self, gtk_box), owner=self)

        return gtk_box
