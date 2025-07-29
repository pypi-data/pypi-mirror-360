#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import klovve.builtin.drivers.gtk
from klovve.builtin.drivers.gtk import Gtk


class ProgressBar(klovve.builtin.drivers.gtk.ViewMaterialization[klovve.views.ProgressBar]):

    def create_native(self):
        return self.new_native(Gtk.ProgressBar, self.piece, fraction=self.piece.bind.value)
