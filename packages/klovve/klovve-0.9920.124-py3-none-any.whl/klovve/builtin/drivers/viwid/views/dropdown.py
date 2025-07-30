#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import klovve.builtin.drivers.viwid
import klovve.data

import viwid


class DropDown(klovve.builtin.drivers.viwid.ViewMaterialization[klovve.views.DropDown]):

    def create_native(self):
        viwid_drop_down = self.new_native(viwid.widgets.dropdown.DropDown, self.piece)

        self.piece._introspect.observe_list_property(klovve.views.DropDown.items, self.__MaterializingItemsObserver,
                                                     (self, viwid_drop_down), owner=self)

        klovve.effect.activate_effect(self.__refresh_selection_in_ui, (viwid_drop_down,), owner=self)
        viwid_drop_down.listen_property("selected_index", lambda: self.__handle_ui_selected_item_changed(viwid_drop_down))

        return viwid_drop_down

    class __MaterializingItemsObserver(klovve.data.list.List.Observer):

        def __init__(self, dropdown, viwid_drop_down):
            self.__dropdown = dropdown
            self.__viwid_drop_down = viwid_drop_down
            self.__refresh_item_label_in_ui_effects = []

        def item_added(self, index, item):
            self.__viwid_drop_down.items.insert(index, "")
            self.__refresh_item_label_in_ui_effects.insert(index, klovve.effect.activate_effect(
                self.__refresh_item_label_in_ui, (item,), owner=None))

        def item_removed(self, index, item):
            self.__viwid_drop_down.items.pop(index)
            klovve.effect.stop_effect(self.__refresh_item_label_in_ui_effects.pop(index))

        def __refresh_item_label_in_ui(self, item):
            try:
                index = self.__dropdown.piece.items.index(item)
            except ValueError:
                return
            self.__viwid_drop_down.items[index] = self.__dropdown.piece.item_label_func(item)

    def __handle_ui_selected_item_changed(self, viwid_drop_down):
        idx = viwid_drop_down.selected_index
        x = idx if idx is not None else None
        self.piece.selected_item = self.piece.items[x] if (x is not None) else None

    def __refresh_selection_in_ui(self, viwid_drop_down):
        index = None
        if self.piece.selected_item is not None:  # TODO not ideal?!
            try:
                index = self.piece.items.index(self.piece.selected_item)
            except ValueError:
                pass

        viwid_drop_down.selected_index = index
