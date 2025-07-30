#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import klovve.builtin.drivers.gtk
import klovve.data
import klovve.ui.utils
from klovve.builtin.drivers.gtk import Gtk


class Form(klovve.builtin.drivers.gtk.ViewMaterialization[klovve.views.Form]):

    def create_native(self):
        gtk_grid = self.new_native(Gtk.Grid, self.piece, row_spacing=4, column_spacing=8)

        self.piece._introspect.observe_list_property(klovve.views.Form.sections, self.__ItemsObserver,
                                                     (self, gtk_grid,), owner=self)

        return gtk_grid

    class __ItemsObserver(klovve.data.list.List.Observer):

        def __init__(self, form, gtk_grid):
            super().__init__()
            self.__form = form
            self.__gtk_grid = gtk_grid

        def item_added(self, index, item):
            self.__gtk_grid.insert_row(index)
            if isinstance(item, str):
                self.__gtk_grid.attach(Gtk.Label(label=item), 1, index, 1, 1)
            elif isinstance(item, klovve.ui.View):
                self.__gtk_grid.attach(self.__form.materialize_child(item).native, 1, index, 1, 1)
            else:
                self.__gtk_grid.attach(gtk_section_label := Gtk.Label(), 0, index, 1, 1)
                self.__gtk_grid.attach(gtk_section_body := Gtk.Box(layout_manager=Gtk.BinLayout()), 1, index, 1, 1)
                klovve.effect.activate_effect(self.__refresh_label_in_ui,
                                              (item, gtk_section_label), owner=gtk_section_label)
                klovve.effect.activate_effect(klovve.builtin.drivers.gtk.ViewMaterialization.MaterializingViewEffect,
                                              (self.__form, gtk_section_body, lambda: item.body),
                                              owner=gtk_section_body)

        def item_removed(self, index, item):
            self.__gtk_grid.remove_row(index)

        def __refresh_label_in_ui(self, section: klovve.views.Form.Section, gtk_label):
            gtk_label.set_label(section.label)
