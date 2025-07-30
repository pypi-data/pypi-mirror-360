#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import klovve.builtin.drivers.viwid
import klovve.data
import klovve.variable

import viwid


class LogPager(klovve.builtin.drivers.viwid.ViewMaterialization[klovve.views.LogPager]):

    def create_native(self):
        viwid_scrollable = self.new_native(viwid.widgets.scrollable.Scrollable, self.piece)
        viwid_scrollable.body = viwid_tree = self.new_native(viwid.widgets.tree.Tree)

        stick_scrolled_to_bottom_flag = [True]

        item_for_row = {}
        klovve.effect.activate_effect(self.__refresh_show_verbose_in_ui, (viwid_tree, item_for_row), owner=self)
        self.piece._introspect.observe_list_property(klovve.views.LogPager.entries, self.__EntriesObserver,
                                                     (self, viwid_tree, None, item_for_row), owner=self)
        viwid_scrollable.listen_event(
            viwid.widgets.scrollable.Scrollable.OffsetChangedEvent,
            lambda *_: self.__handle_scrolled(viwid_scrollable, stick_scrolled_to_bottom_flag))
        viwid_tree.listen_event(
            viwid.event.widget.ResizeEvent,
            lambda *_: self.__stick_scrolled_to_bottom(viwid_scrollable, stick_scrolled_to_bottom_flag))

        return viwid_scrollable

    def __refresh_show_verbose_in_ui(self, viwid_tree, item_for_row):
        show_verbose = self.piece.show_verbose
        rows = list(viwid_tree.items)
        while rows:
            row = rows.pop(0)
            rows += row.items
            item = item_for_row.get(row)
            row.is_visible = item and (show_verbose or not item.only_verbose)

    def __is_log_entry_visible(self, gtk_unfiltered_tree_store, gtk_iter):
        with klovve.variable.no_dependency_tracking():
            return (not gtk_unfiltered_tree_store.get_value(gtk_iter, 3)) or self.piece.show_verbose

    def __handle_scrolled(self, viwid_scrollable, stick_scrolled_to_bottom_flag):
        stick_scrolled_to_bottom_flag[0] = (viwid_scrollable.vertical_scroll_current_offset
                                            == viwid_scrollable.vertical_scroll_max_offset)

    def __stick_scrolled_to_bottom(self, viwid_scrollable, stick_scrolled_to_bottom_flag):
        if stick_scrolled_to_bottom_flag[0]:
            viwid_scrollable.scroll_to(viwid.Offset(0, viwid_scrollable.vertical_scroll_max_offset))

    class __EntriesObserver(klovve.data.list.List.Observer):

        def __init__(self, log_pager, viwid_tree, viwid_row, item_for_row):
            self.__log_pager = log_pager
            self.__viwid_tree = viwid_tree
            self.__viwid_row = viwid_row
            self.__item_for_row = item_for_row
            self.__effects = []
            self.__list_observers = []

        def item_added(self, index, item):
            new_viwid_row = viwid.widgets.tree.Tree.Row(is_visible=item and (self.__log_pager.piece.show_verbose
                                                                             or not item.only_verbose))
            self.__item_for_row[new_viwid_row] = item
            (self.__viwid_row or self.__viwid_tree).items.insert(index, new_viwid_row)

            self.__effects.insert(index, effects := [])
            effects.append(klovve.effect.activate_effect(self.__refresh_item_in_ui,
                                                         (item, new_viwid_row), owner=None))
            self.__list_observers.insert(index, item._introspect.observe_list_property(
                klovve.views.LogPager.Entry.entries, type(self),
                (self.__log_pager, self.__viwid_tree, new_viwid_row, self.__item_for_row), owner=None))

            if self.__viwid_row and len(self.__viwid_row.items) == 1:
                self.__viwid_tree.set_row_expanded(self.__viwid_row, True)

        def item_removed(self, index, item):
            self.__viwid_row.items.pop(index)
            self.__item_for_row.pop(item)
            for effect in self.__effects.pop(index):
                klovve.effect.stop_effect(effect)
            item._introspect.stop_observe_list_property(klovve.views.LogPager.Entry.entries,
                                                        self.__list_observers.pop(index))

        def __refresh_item_in_ui(self, entry, viwid_row):
            viwid_row.text = f"{entry._began_at_str.ljust(14)}  {entry._ended_at_str.ljust(14)}  {entry.message}"
