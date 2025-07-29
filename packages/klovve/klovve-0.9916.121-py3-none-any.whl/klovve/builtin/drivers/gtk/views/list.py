#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import klovve.builtin.drivers.gtk
import klovve.data
from klovve.builtin.drivers.gtk import Gtk


class List(klovve.builtin.drivers.gtk.ViewMaterialization[klovve.views.List]):  # TODO at the beginning, gtk automatically selects the first item. that's not ideal.

    def create_native(self):
        gtk_scrolled = self.new_native(Gtk.ScrolledWindow, self.piece, hscrollbar_policy=Gtk.PolicyType.NEVER,
                                       propagate_natural_height=True)
        gtk_scrolled.set_child(gtk_list_box := self.new_native(Gtk.ListBox))
        ignore_selection_flag = []

        gtk_list_box.connect("row-activated", lambda _, gtk_row: self.__handle_row_activated(gtk_row))
        gtk_list_box.connect("selected-rows-changed", lambda *_: self.__selected_rows_changed(gtk_list_box,
                                                                                              ignore_selection_flag))
        self.piece._introspect.observe_list_property(klovve.views.List.items, self.__ListItemsObserver,
                                                     (gtk_list_box, self.piece, ignore_selection_flag), owner=self)
        klovve.effect.activate_effect(self.__refresh_selected_item_in_ui,
                                      (gtk_list_box, ignore_selection_flag), owner=self)

        return gtk_scrolled

    def __handle_row_activated(self, gtk_row):
        if self.piece.allows_multi_select:
            if gtk_row:
                checked = gtk_row.get_child().get_first_child().get_active()
                idx = gtk_row.get_index()
                if idx >= 0:
                    item = self.piece.items[idx]
                    if checked:
                        self.piece.selected_items.remove(item)
                    else:
                        self.piece.selected_items.append(item)

    def __selected_rows_changed(self, gtk_list_box, ignore_selection_flag):
        if ignore_selection_flag:
            return
        if self.piece.allows_multi_select:
            return

        for selected_row in gtk_list_box.get_selected_rows():
            idx = selected_row.get_index()
            if idx >= 0:
                self.piece.selected_items = (self.piece.items[idx],)
                return
        self.piece.selected_items = ()

    def __refresh_selected_item_in_ui(self, gtk_list_box, ignore_selection_flag):
        ignore_selection_flag.append(1)
        try:
            if self.piece.allows_multi_select:
                selected_idxs = set()
                for item in self.piece.selected_items:
                    try:
                        selected_idxs.add(self.piece.items.index(item))
                    except ValueError:
                        pass

                for i_item in range(len(self.piece.items)):
                    gtk_checkbutton = gtk_list_box.get_row_at_index(i_item).get_child().get_first_child()
                    gtk_checkbutton.set_active(i_item in selected_idxs)

            else:
                gtk_list_box.unselect_all()

                for item in self.piece.selected_items:
                    gtk_row = None
                    try:
                        gtk_row = gtk_list_box.get_row_at_index(self.piece.items.index(item))
                    except ValueError:
                        pass

                    gtk_list_box.select_row(gtk_row)

        finally:
            ignore_selection_flag.pop()

    class __ListItemsObserver(klovve.data.list.List.Observer):

        def __init__(self, gtk_list_box, piece, ignore_selection_flag):
            super().__init__()
            self.__gtk_list_box = gtk_list_box
            self.__piece = piece
            self.__ignore_selection_flag = ignore_selection_flag
            self.__gtk_item_box_by_item = {}

        def item_added(self, index, item):
            gtk_item_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            gtk_item_box.append(gtk_item_check := Gtk.CheckButton(can_focus=False, margin_end=3))
            gtk_item_box.append(gtk_item_label := Gtk.Label(xalign=0, visible=True))
            self.__gtk_list_box.insert(gtk_item_box, index)

            gtk_item_check.connect("toggled", lambda *_: self.__check_toggled(gtk_item_check))
            klovve.effect.activate_effect(self.__refresh_item_check_visibility_in_ui,
                                          (gtk_item_check,), owner=gtk_item_box)
            klovve.effect.activate_effect(self.__refresh_item_label_in_ui, (gtk_item_label, item, self.__piece),
                                          owner=gtk_item_box)

            self.__gtk_item_box_by_item[item] = gtk_item_box

        def item_moved(self, from_index, to_index, item):
            gtk_item_box = self.__gtk_item_box_by_item[self.__piece.items[from_index]]
            self.__gtk_list_box.remove(gtk_row := gtk_item_box.get_parent())
            gtk_row.set_child(None)
            self.__gtk_list_box.insert(gtk_item_box, to_index)

        def item_removed(self, index, item):  # TODO noh this is broken if the item is in the list more than once?!
            self.__gtk_list_box.remove(self.__gtk_item_box_by_item.pop(item).get_parent())

        def __check_toggled(self, gtk_item_check):
            if not self.__ignore_selection_flag:
                self.__ignore_selection_flag.append(1)
                try:
                    if (idx := gtk_item_check.get_parent().get_parent().get_index()) >= 0:
                        item = self.__piece.items[idx]

                        if gtk_item_check.get_active():
                            self.__piece.selected_items.append(item)
                        else:
                            self.__piece.selected_items.remove(item)
                finally:
                    self.__ignore_selection_flag.pop()

        def __refresh_item_check_visibility_in_ui(self, gtk_checkbutton):
            gtk_checkbutton.set_visible(self.__piece.allows_multi_select)

        def __refresh_item_label_in_ui(self, gtk_item_label, item, piece):
            gtk_item_label.set_label(piece.item_label_func(item))
