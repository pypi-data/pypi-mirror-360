#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import klovve.builtin.drivers.gtk
import klovve.data
from klovve.builtin.drivers.gtk import Gtk


class DropDown(klovve.builtin.drivers.gtk.ViewMaterialization[klovve.views.DropDown]):

    def create_native(self):
        # TODO# use Gtk.DropDown as soon as it does not instantly auto-select the first item anymore
        gtk_combo_box = self.new_native(Gtk.ComboBox, self.piece, model=(gtk_tree_store := Gtk.TreeStore(str)))
        cell_renderer = Gtk.CellRendererText(text=0)
        gtk_combo_box.pack_start(cell_renderer, True)
        gtk_combo_box.add_attribute(cell_renderer, "text", 0)

        self.piece._introspect.observe_list_property(klovve.views.DropDown.items, self.__MaterializingItemsObserver,
                                                     (self, gtk_tree_store), owner=self)
        klovve.effect.activate_effect(self.__refresh_selection_in_ui, (gtk_combo_box,), owner=self)
        gtk_combo_box.connect("changed", lambda *_: self.__handle_ui_selected_item_changed(gtk_combo_box))

        return gtk_combo_box

    class __MaterializingItemsObserver(klovve.data.list.List.Observer):

        def __init__(self, dropdown, gtk_tree_store):
            self.__dropdown = dropdown
            self.__gtk_tree_store = gtk_tree_store
            self.__refresh_item_label_in_ui_effects = []

        def item_added(self, index, item):
            gtk_row_reference = Gtk.TreeRowReference.new(
                self.__gtk_tree_store, self.__gtk_tree_store.get_path(self.__gtk_tree_store.insert(None, index, [""])))
            self.__refresh_item_label_in_ui_effects.insert(index, klovve.effect.activate_effect(
                self.__refresh_item_label_in_ui, (gtk_row_reference, item), owner=None))

        def item_removed(self, index, item):
            self.__gtk_tree_store.remove(self.__gtk_tree_store.iter_nth_child(None, index))
            klovve.effect.stop_effect(self.__refresh_item_label_in_ui_effects.pop(index))

        def __refresh_item_label_in_ui(self, gtk_row_reference, item):
            if gtk_row_path := gtk_row_reference.get_path():
                if gtk_iter := self.__gtk_tree_store.get_iter(gtk_row_path):
                    self.__gtk_tree_store.set_value(gtk_iter, 0, self.__dropdown.piece.item_label_func(item))

    def __handle_ui_selected_item_changed(self, gtk_combo_box):
        x = None
        idx = gtk_combo_box.get_active()
        if idx >= 0:
            x = idx
        self.piece.selected_item = self.piece.items[x] if (x is not None) else None

    def __refresh_selection_in_ui(self, gtk_combo_box):
        gtk_combo_box.set_active(-1 if (self.piece.selected_item is None)
                                 else self.piece.items.index(self.piece.selected_item))
