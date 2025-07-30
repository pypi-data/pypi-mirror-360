#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import typing as t
import klovve.data


class List[T](klovve.ui.Piece):

    items: list[T] = klovve.ui.list_property()

    selected_item: T|None = klovve.ui.property()
    selected_items: list[T] = klovve.ui.list_property()
    allows_multi_select: bool = klovve.ui.property(initial=False)

    item_label_func: t.Callable[[T], str] = klovve.ui.property(initial=lambda: str)

    def __init_object__(self):
        self._introspect.observe_list_property(List.items, self.__RemoveSelectedItemWhenItemRemoved,
                                               (self,), owner=self)
        klovve.effect.activate_effect(self.__fix_selected_items_for_non_multi_select, owner=self)
        klovve.effect.activate_effect(self.__refresh_selected_item_by_selected_items, owner=self)
        klovve.effect.activate_effect(self.__refresh_selected_items_by_selected_item, owner=self)

    class __RemoveSelectedItemWhenItemRemoved(klovve.data.list.List.Observer):

        def __init__(self, list_):
            self.__list = list_

        def item_added(self, index, item):
            pass

        def item_removed(self, index, item):
            try:
                self.__list.selected_items.remove(item)
            except ValueError:
                pass

    def __fix_selected_items_for_non_multi_select(self):
        if len(self.selected_items) > 1 and not self.allows_multi_select:
            self.selected_items = [self.selected_items[0]]

    def __refresh_selected_item_by_selected_items(self):
        selected_items = self.selected_items
        self.selected_item = selected_items[0] if (selected_items and len(selected_items) > 0) else None

    def __refresh_selected_items_by_selected_item(self):
        _ = self.allows_multi_select
        selected_item = self.selected_item
        self.selected_items = [selected_item] if (selected_item is not None) else []
