#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import klovve.builtin.drivers.gtk
import klovve.ui.utils
from klovve.builtin.drivers.gtk import Gtk


class Sidebar(klovve.builtin.drivers.gtk.ViewMaterialization[klovve.views.Sidebar]):

    def create_native(self):
        gtk_sidebar_box = self.new_native(Gtk.Box, self.piece, orientation=Gtk.Orientation.VERTICAL,
                                          css_classes=("klv_sidebar",))
        gtk_sidebar_box.append(gtk_collapse_expand_button := self.new_native(
            Gtk.Button, halign=Gtk.Align.END, has_frame=False, can_focus=False,
            css_classes=("klv_sidebar_collapse_expand_button", "flat")))
        gtk_sidebar_box.append(gtk_sidebar_body_box := self.new_native(Gtk.Box))

        klovve.effect.activate_effect(self.__collapse_effect,
                                      (gtk_sidebar_body_box, gtk_collapse_expand_button), owner=self)
        klovve.effect.activate_effect(self.__width_effect, (gtk_sidebar_body_box,), owner=self)
        klovve.effect.activate_effect(klovve.builtin.drivers.gtk.ViewMaterialization.MaterializingViewEffect,
                                      (self, gtk_sidebar_body_box, lambda: self.piece.body), owner=self)
        gtk_collapse_expand_button.connect("clicked", lambda *_: self.piece._toggle_collapsed())

        return gtk_sidebar_box

    def __collapse_effect(self, gtk_sidebar_body_box, gtk_collapse_expand_button):
        gtk_sidebar_body_box.set_visible(not self.piece.is_collapsed)
        gtk_collapse_expand_button.set_icon_name("go-next" if self.piece.is_collapsed else "go-previous")

    def __width_effect(self, gtk_sidebar_body_box):
        gtk_sidebar_body_box.set_size_request(klovve.builtin.drivers.gtk.em_to_px(self.piece.width_em), -1)
