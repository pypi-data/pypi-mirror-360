#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import klovve.builtin.drivers.gtk
import klovve.data
from klovve.builtin.drivers.gtk import Gtk


class Tabbed(klovve.builtin.drivers.gtk.ViewMaterialization[klovve.views.Tabbed]):

    def create_native(self):
        gtk_notebook = self.new_native(Gtk.Notebook, self.piece)

        self.piece._introspect.observe_list_property(klovve.views.Tabbed.tabs, self.__ItemsObserver,
                                                     (self, gtk_notebook,), owner=self)

        return gtk_notebook

    class __ItemsObserver(klovve.data.list.List.Observer):

        def __init__(self, tabbed, gtk_notebook):
            super().__init__()
            self.__tabbed = tabbed
            self.__gtk_notebook = gtk_notebook

        def item_added(self, index, item):
            self.__gtk_notebook.insert_page(
                gtk_tab_body := Gtk.Box(hexpand=True, vexpand=True, hexpand_set=True, vexpand_set=True,
                                        halign=Gtk.Align.FILL, valign=Gtk.Align.FILL, layout_manager=Gtk.BinLayout()),
                gtk_tab_label_box := Gtk.Box(), index)
            gtk_tab_label_box.append(gtk_tab_label_label := Gtk.Label())
            gtk_tab_label_box.append(gtk_tab_label_close_button := Gtk.Button(
                can_focus=False, has_frame=False, icon_name="window-close"))

            gtk_tab_label_close_button.connect("clicked", lambda *_: self.__tabbed.piece.request_close(item))
            klovve.effect.activate_effect(self.__refresh_label_in_ui,
                                          (item, gtk_tab_label_label), owner=gtk_tab_label_label)
            klovve.effect.activate_effect(self.__refresh_close_button_visibility_in_ui,
                                          (item, gtk_tab_label_close_button), owner=gtk_tab_label_close_button)
            klovve.effect.activate_effect(klovve.builtin.drivers.gtk.ViewMaterialization.MaterializingViewEffect,
                                          (self.__tabbed, gtk_tab_body, lambda: item.body), owner=gtk_tab_body)

        def item_removed(self, index, item):
            self.__gtk_notebook.remove_page(index)

        def __refresh_label_in_ui(self, tab: klovve.views.Tabbed.Tab, gtk_label):
            gtk_label.set_label(tab.title)

        def __refresh_close_button_visibility_in_ui(self, tab: klovve.views.Tabbed.Tab, gtk_button):
            gtk_button.set_visible(tab.is_closable)
