#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import abc

import klovve.builtin.drivers.viwid

import viwid


class Box[_T](klovve.builtin.drivers.viwid.ViewMaterialization[_T], abc.ABC):

    @property
    @abc.abstractmethod
    def _orientation(self) -> viwid.Orientation:
        pass

    def create_native(self):
        viwid_box = self.new_native(viwid.widgets.box.Box, self.piece, orientation=self._orientation)

        self.piece._introspect.observe_list_property(
            self.piece._introspect.property_by_name("items"),
            self.MaterializingViewsInViwidBoxObserver, (self, viwid_box), owner=self)

        return viwid_box
