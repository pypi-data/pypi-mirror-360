#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import xml.etree.ElementTree

import klovve.builtin.drivers.gtk
from klovve.builtin.drivers.gtk import Gtk


class TextBlock(klovve.builtin.drivers.gtk.ViewMaterialization[klovve.views.TextBlock]):

    def create_native(self):
        gtk_text_view = self.new_native(Gtk.TextView, self.piece, editable=False, cursor_visible=False,
                                        wrap_mode=Gtk.WrapMode.WORD_CHAR)
        gtk_text = gtk_text_view.get_buffer()
        # TODO;  maybe also needed somewhere below: src_node.tag.lower()
        gtk_text.create_tag("body")
        gtk_text.create_tag("h1", pixels_above_lines=10, left_margin=20,
                            size=klovve.builtin.drivers.gtk.Pango.SCALE * 25)
        gtk_text.create_tag("ul")
        gtk_text.create_tag("li")
        gtk_text.create_tag("foo", size=klovve.builtin.drivers.gtk.Pango.SCALE * 15)

        klovve.effect.activate_effect(self.__refresh_text_in_ui, (gtk_text,), owner=self)

        return gtk_text_view

    def __refresh_text_in_ui(self, gtk_text):
        gtk_text.set_text("")
        self.__put(xml.etree.ElementTree.fromstring("<body>" + self.piece.text + "</body>"), gtk_text)

    def __put(self, src_node, gtk_text):
        start_mark = gtk_text.create_mark("", gtk_text.get_end_iter(), True)

        if src_node.tag.lower() in ["ul", "li"]:
            gtk_text.insert(gtk_text.get_end_iter(), "\n")

        gtk_text.insert(gtk_text.get_end_iter(), src_node.text or "")
        for src_child_node in src_node:
            self.__put(src_child_node, gtk_text)

        if src_node.tag.lower() in ["h1", "ul", "li"]:
            gtk_text.insert(gtk_text.get_end_iter(), "\n")

        gtk_text.apply_tag_by_name(src_node.tag.lower(), gtk_text.get_iter_at_mark(start_mark), gtk_text.get_end_iter())
        gtk_text.insert(gtk_text.get_end_iter(), src_node.tail or "")
