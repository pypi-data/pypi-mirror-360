#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import klovve.builtin.drivers.viwid
import klovve.data

import viwid


class List(klovve.builtin.drivers.viwid.ViewMaterialization[klovve.views.List]):

    def create_native(self):
        viwid_scrollable = self.new_native(viwid.widgets.scrollable.Scrollable, self.piece)  # TODO propagate_natural_height=True
        viwid_scrollable.body = viwid_list = self.new_native(viwid.widgets.list.List,
                                                             allows_multi_select=self.piece.bind.allows_multi_select)

        viwid_list.listen_property("selected_item_indexes",
                                   lambda *_: self.__handle_selection_changed_in_ui(viwid_list))
        self.piece._introspect.observe_list_property(klovve.views.List.items, self.__ListItemsObserver,
                                                     (viwid_list, self.piece),
                                                     owner=self)
        klovve.effect.activate_effect(self.__refresh_selected_item_in_ui, (viwid_list,), owner=self)

        return viwid_scrollable

    def __handle_selection_changed_in_ui(self, viwid_list):
        self.piece.selected_items = (self.piece.items[i] for i in viwid_list.selected_item_indexes)

    def __refresh_selected_item_in_ui(self, viwid_list):
        selected_item_indexes = []
        for item in self.piece.selected_items:
            try:
                selected_item_indexes.append(self.piece.items.index(item))
            except ValueError:
                pass
        viwid_list.selected_item_indexes = selected_item_indexes

    class __ListItemsObserver(klovve.data.list.List.Observer):

        def __init__(self, viwid_list, piece):
            super().__init__()
            self.__viwid_list = viwid_list
            self.__piece = piece
            self.__viwid_row_by_item = {}

        def item_added(self, index, item):
            viwid_row = viwid.widgets.list.List.Row()

            klovve.effect.activate_effect(self.__refresh_item_label_in_ui, (viwid_row, item, self.__piece),
                                          owner=viwid_row)

            self.__viwid_list.items.insert(index, viwid_row)

        def item_moved(self, from_index, to_index, item):
            self.__viwid_list.items.insert(self.__viwid_list.items.pop(from_index), to_index)

        def item_removed(self, index, item):
            self.__viwid_list.items.pop(index)

        def __refresh_item_label_in_ui(self, viwid_row, item, piece):
            viwid_row.text = piece.item_label_func(item)
