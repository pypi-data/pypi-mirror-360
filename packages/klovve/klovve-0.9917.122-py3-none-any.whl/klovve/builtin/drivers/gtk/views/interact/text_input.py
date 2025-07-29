#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import klovve.builtin.drivers.gtk
import klovve.ui.utils
from klovve.builtin.drivers.gtk import Gtk


class TextInput(klovve.builtin.drivers.gtk.ViewMaterialization[klovve.views.interact.TextInput]):

    def create_native(self):
        gtk_box = self.new_native(Gtk.Box, self.piece, orientation=Gtk.Orientation.VERTICAL)
        gtk_box.append(self.new_native(Gtk.Label, label=self.piece._bind.message))
        gtk_box.append(gtk_text_entry := self.new_native(Gtk.Entry, text=self.piece.suggestion))
        gtk_box.append(gtk_message_choices_box := self.new_native(Gtk.Box))
        gtk_message_choices_box.append(gtk_button_ok := self.new_native(
            Gtk.Button, label=klovve.ui.utils.tr("OK")))
        gtk_message_choices_box.append(gtk_button_cancel := self.new_native(
            Gtk.Button, label=klovve.ui.utils.tr("CANCEL")))

        gtk_button_ok.connect("clicked", lambda *_: self.piece._answer(self, gtk_text_entry.get_text()))
        gtk_button_cancel.connect("clicked", lambda *_: self.piece._answer(self, None))

        return gtk_box
