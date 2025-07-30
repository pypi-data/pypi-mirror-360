#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import klovve.builtin.drivers.gtk
from klovve.builtin.drivers.gtk import Gtk


class Message(klovve.builtin.drivers.gtk.ViewMaterialization[klovve.views.interact.Message]):

    def create_native(self):
        gtk_box = self.new_native(Gtk.Box, self.piece, orientation=Gtk.Orientation.VERTICAL)
        gtk_box.append(self.new_native(Gtk.Label, label=self.piece._bind.message))
        gtk_box.append(gtk_message_choices_box := self.new_native(Gtk.Box))

        self.piece._introspect.observe_list_property(
            klovve.views.interact.Message.choices,
            klovve.builtin.drivers.gtk.ViewMaterialization.MaterializingViewsInGtkBoxObserver,
            (self, gtk_message_choices_box, self.__gtk_button_for_choice), owner=self)

        return gtk_box

    def __gtk_button_for_choice(self, choice):
        gtk_choice_button = self.new_native(Gtk.Button, label=choice[0])
        gtk_choice_button.connect("clicked", lambda *_: self.piece._answer(self, choice[1]))
        return gtk_choice_button
