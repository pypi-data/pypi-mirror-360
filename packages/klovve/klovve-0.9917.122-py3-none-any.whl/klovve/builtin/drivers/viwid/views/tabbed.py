#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import functools

import klovve.builtin.drivers.viwid
import klovve.data

import viwid


class Tabbed(klovve.builtin.drivers.viwid.ViewMaterialization[klovve.views.Tabbed]):

    def create_native(self):
        viwid_tabbed = self.new_native(viwid.widgets.tabbed.Tabbed, self.piece)

        self.piece._introspect.observe_list_property(klovve.views.Tabbed.tabs, self.__ItemsObserver,
                                                     (self, viwid_tabbed,), owner=self)

        return viwid_tabbed

    class __ItemsObserver(klovve.data.list.List.Observer):

        def __init__(self, tabbed: "Tabbed", viwid_tabbed: viwid.widgets.tabbed.Tabbed):
            super().__init__()
            self.__tabbed = tabbed
            self.__viwid_tabbed = viwid_tabbed

        def item_added(self, index, item):
            viwid_tab = viwid.widgets.tabbed.Tabbed.Tab()
            self.__viwid_tabbed.tabs.insert(index, viwid_tab)

            viwid_tab.listen_event(viwid.widgets.tabbed.Tabbed.Tab.RequestCloseEvent,
                                   functools.partial(self.__handle_request_close_tab, item))
            klovve.effect.activate_effect(self.__refresh_label_in_ui, (item, viwid_tab), owner=viwid_tab)
            klovve.effect.activate_effect(self.__refresh_close_button_visibility_in_ui, (item, viwid_tab), owner=viwid_tab)
            klovve.effect.activate_effect(klovve.builtin.drivers.viwid.ViewMaterialization.MaterializingViewEffect,
                                          (self.__tabbed, viwid_tab, lambda: item.body), owner=viwid_tab)

        def item_removed(self, index, item):
            self.__viwid_tabbed.tabs.pop(index)

        def __handle_request_close_tab(self, tab, event):
            self.__tabbed.piece.request_close(tab)
            event.stop_handling()

        def __refresh_label_in_ui(self, tab: klovve.views.Tabbed.Tab, viwid_tab):
            viwid_tab.title = tab.title

        def __refresh_close_button_visibility_in_ui(self, tab: klovve.views.Tabbed.Tab, viwid_tab):
            viwid_tab.is_closable_by_user = tab.is_closable
