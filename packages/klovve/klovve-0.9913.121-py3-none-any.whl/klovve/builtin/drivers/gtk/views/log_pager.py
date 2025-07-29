#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import klovve.builtin.drivers.gtk
import klovve.data
import klovve.variable
from klovve.builtin.drivers.gtk import Gtk


class LogPager(klovve.builtin.drivers.gtk.ViewMaterialization[klovve.views.LogPager]):

    def create_native(self):
        gtk_scrolled = self.new_native(Gtk.ScrolledWindow, self.piece)
        gtk_unfiltered_tree_store = Gtk.TreeStore(str, str, str, bool)
        gtk_filtered_tree_store = gtk_unfiltered_tree_store.filter_new()
        gtk_scrolled.set_child(gtk_treeview := self.new_native(
            Gtk.TreeView, headers_visible=False, hexpand=True, vexpand=True, model=gtk_filtered_tree_store))
        gtk_treeview.append_column(Gtk.TreeViewColumn("", Gtk.CellRendererText(), text=0))
        gtk_treeview.append_column(Gtk.TreeViewColumn("", Gtk.CellRendererText(), text=1))
        gtk_treeview.append_column(Gtk.TreeViewColumn("", Gtk.CellRendererText(), text=2))
        stick_scrolled_to_bottom_flag = [True]

        gtk_filtered_tree_store.set_visible_func(
            lambda _, gtk_iter, __: self.__is_log_entry_visible(gtk_unfiltered_tree_store, gtk_iter))
        klovve.effect.activate_effect(self.__refresh_show_verbose_in_ui, (gtk_filtered_tree_store,), owner=self)
        self.piece._introspect.observe_list_property(klovve.views.LogPager.entries, self.__EntriesObserver,
                                                     (gtk_treeview, gtk_unfiltered_tree_store, None), owner=self)
        gtk_scrolled.get_vadjustment().connect(
            "changed", lambda *_: self.__stick_scrolled_to_bottom(gtk_scrolled, stick_scrolled_to_bottom_flag))
        gtk_scrolled.get_vadjustment().connect(
            "value-changed", lambda *_: self.__handle_scrolled(gtk_scrolled, stick_scrolled_to_bottom_flag))

        return gtk_scrolled

    def __refresh_show_verbose_in_ui(self, gtk_filtered_tree_store):
        _ = self.piece.show_verbose
        gtk_filtered_tree_store.refilter()

    def __is_log_entry_visible(self, gtk_unfiltered_tree_store, gtk_iter):
        with klovve.variable.no_dependency_tracking():
            return (not gtk_unfiltered_tree_store.get_value(gtk_iter, 3)) or self.piece.show_verbose

    def __handle_scrolled(self, gtk_scrolled, stick_scrolled_to_bottom_flag):
        adjustment = gtk_scrolled.get_vadjustment()
        stick_scrolled_to_bottom_flag[0] = (adjustment.get_upper() - adjustment.get_page_size()
                                            - adjustment.get_value()) < 5

    def __stick_scrolled_to_bottom(self, gtk_scrolled, stick_scrolled_to_bottom_flag):
        gtk_adjustment = gtk_scrolled.get_vadjustment()
        if stick_scrolled_to_bottom_flag[0]:
            gtk_adjustment.set_value(gtk_adjustment.get_upper())

    class __EntriesObserver(klovve.data.list.List.Observer):

        def __init__(self, gtk_treeview, gtk_unfiltered_tree_store, gtk_row_reference):
            self.__gtk_treeview = gtk_treeview
            self.__gtk_unfiltered_tree_store = gtk_unfiltered_tree_store
            self.__gtk_row_reference = gtk_row_reference
            self.__effects = []
            self.__list_observers = []

        def item_added(self, index, item):
            gtk_self_iter = self.__gtk_row_reference_to_gtk_iter(self.__gtk_unfiltered_tree_store,
                                                                 self.__gtk_row_reference)
            gtk_new_item_iter = self.__gtk_unfiltered_tree_store.insert(gtk_self_iter, index,
                                                                        ["", "", "", item.only_verbose])

            gtk_new_item_row_reference = Gtk.TreeRowReference.new(
                self.__gtk_unfiltered_tree_store, self.__gtk_unfiltered_tree_store.get_path(gtk_new_item_iter))

            self.__effects.insert(index, effects := [])
            effects.append(klovve.effect.activate_effect(self.__refresh_began_at_in_ui,
                                                         (item, gtk_new_item_row_reference), owner=None))
            effects.append(klovve.effect.activate_effect(self.__refresh_ended_at_in_ui,
                                                         (item, gtk_new_item_row_reference), owner=None))
            effects.append(klovve.effect.activate_effect(self.__refresh_message_in_ui,
                                                         (item, gtk_new_item_row_reference), owner=None))
            self.__list_observers.insert(index, item._introspect.observe_list_property(
                klovve.views.LogPager.Entry.entries, type(self),
                (self.__gtk_treeview, self.__gtk_unfiltered_tree_store, gtk_new_item_row_reference), owner=None))

            if gtk_self_iter and self.__gtk_unfiltered_tree_store.iter_n_children(gtk_self_iter) == 1:
                self.__gtk_treeview.expand_row(self.__gtk_unfiltered_tree_store.get_path(gtk_self_iter), open_all=False)

        def item_removed(self, index, item):
            gtk_self_iter = self.__gtk_row_reference_to_gtk_iter(self.__gtk_unfiltered_tree_store,
                                                                 self.__gtk_row_reference)
            self.__gtk_unfiltered_tree_store.remove(
                self.__gtk_unfiltered_tree_store.iter_nth_child(gtk_self_iter, index))
            for effect in self.__effects.pop(index):
                klovve.effect.stop_effect(effect)
            item._introspect.stop_observe_list_property(klovve.views.LogPager.Entry.entries,
                                                        self.__list_observers.pop(index))

        def __refresh_began_at_in_ui(self, entry, gtk_row_reference):
            gtk_iter = self.__gtk_row_reference_to_gtk_iter(self.__gtk_unfiltered_tree_store, gtk_row_reference)
            self.__gtk_unfiltered_tree_store.set_value(gtk_iter, 0, entry._began_at_str)

        def __refresh_ended_at_in_ui(self, entry, gtk_row_reference):
            gtk_iter = self.__gtk_row_reference_to_gtk_iter(self.__gtk_unfiltered_tree_store, gtk_row_reference)
            self.__gtk_unfiltered_tree_store.set_value(gtk_iter, 1, entry._ended_at_str)

        def __refresh_message_in_ui(self, entry, gtk_row_reference):
            gtk_iter = self.__gtk_row_reference_to_gtk_iter(self.__gtk_unfiltered_tree_store, gtk_row_reference)
            self.__gtk_unfiltered_tree_store.set_value(gtk_iter, 2, entry.message)

        @staticmethod
        def __gtk_row_reference_to_gtk_iter(gtk_model, gtk_row_reference):
            if gtk_row_reference:
                if gtk_row_path := gtk_row_reference.get_path():
                    return gtk_model.get_iter(gtk_row_path)
