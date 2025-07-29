#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import klovve.builtin.drivers.gtk
from klovve.builtin.drivers.gtk import Gtk


class Window(klovve.builtin.drivers.gtk.ViewMaterialization[klovve.views.Window]):

    def create_native(self):
        gtk_window = self.new_native(Gtk.Window, title=self.piece.bind(two_way=False).title)

        klovve.effect.activate_effect(klovve.builtin.drivers.gtk.ViewMaterialization.MaterializingViewEffect,
                                      (self, gtk_window, lambda: self.piece.body), owner=self)
        klovve.effect.activate_effect(self.__remove_native_window_when_closed, (gtk_window,), owner=self)
        gtk_window.connect("close-request", lambda *_: self.__trigger_request_close())

        return gtk_window

    def __remove_native_window_when_closed(self, gtk_window):
        if self.piece._is_closed:
            gtk_window.destroy()

    def __trigger_request_close(self):
        self.piece.request_close()
        return True
