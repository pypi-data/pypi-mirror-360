#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import klovve.builtin.drivers.gtk
from klovve.builtin.drivers.gtk import Gtk


class MultilineTextField(klovve.builtin.drivers.gtk.ViewMaterialization[klovve.views.MultilineTextField]):

    def create_native(self):
        gtk_text_view = self.new_native(Gtk.TextView, self.piece, wrap_mode=Gtk.WrapMode.WORD_CHAR)
        gtk_text = gtk_text_view.get_buffer()

        klovve.effect.activate_effect(self.__refresh_text_in_ui, (gtk_text,), owner=self)
        gtk_text.connect("changed", lambda *_: self.__refresh_text_in_piece(gtk_text))

        return gtk_text_view

    def __refresh_text_in_ui(self, gtk_text):
        if self.piece.text != gtk_text.get_text(gtk_text.get_start_iter(), gtk_text.get_end_iter(), False):
            gtk_text.set_text(self.piece.text)

    def __refresh_text_in_piece(self, gtk_text):
        self.piece.text = gtk_text.get_text(gtk_text.get_start_iter(), gtk_text.get_end_iter(), False)
