#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import klovve.builtin.drivers.gtk.views._box
from klovve.builtin.drivers.gtk import Gtk


class VerticalBox(klovve.builtin.drivers.gtk.views._box.Box[klovve.views.VerticalBox]):

    @property
    def _orientation(self):
        return Gtk.Orientation.VERTICAL
