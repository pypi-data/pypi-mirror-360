#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import klovve.builtin.drivers.gtk
from klovve.builtin.drivers.gtk import Gtk


class TextField(klovve.builtin.drivers.gtk.ViewMaterialization[klovve.views.TextField]):

    def create_native(self):
        return self.new_native(Gtk.Entry, self.piece, text=self.piece.bind.text,
                               placeholder_text=self.piece.bind(two_way=False).hint_text)
