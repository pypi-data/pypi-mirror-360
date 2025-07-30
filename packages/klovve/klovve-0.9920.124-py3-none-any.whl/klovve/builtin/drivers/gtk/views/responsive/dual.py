#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import typing as t

import klovve.builtin.drivers.gtk
import klovve.driver
import klovve.variable
from klovve.builtin.drivers.gtk import Gtk


class Dual(klovve.builtin.drivers.gtk.ViewMaterialization[klovve.views.responsive.Dual]):

    def create_native(self):
        gtk_box = self.new_native(Gtk.Box, self.piece,
                                   orientation=Gtk.Orientation.VERTICAL)
        gtk_box.append(gtk_inline_control_box := self.new_native(
            Gtk.Box, orientation=Gtk.Orientation.VERTICAL))
        gtk_box.append(gtk_inline_control_resize_canary := self.new_native(Gtk.DrawingArea))
        gtk_box.append(gtk_paned := self.new_native(Dual.Paned, _item_gtk_widgets_func=self.__item_gtk_widgets,
                                                    shrink_start_child=False, shrink_end_child=False))

        self.piece._introspect.set_property_value(klovve.views.responsive.Dual._splitter_width_em,
                                                  3/klovve.builtin.drivers.gtk.em_to_px(1))
        klovve.effect.activate_effect(self.__item_materializing_effect, (gtk_paned, "start", 1), owner=self)
        klovve.effect.activate_effect(self.__item_materializing_effect, (gtk_paned, "end", 2), owner=self)
        klovve.effect.activate_effect(self.__set_control, (gtk_inline_control_box,), owner=self)
        gtk_inline_control_resize_canary.connect(
            "resize", lambda *_: klovve.driver.Driver.get().loop.enqueue(self.__handle_resized(gtk_paned)))

        return gtk_box

    def __item_materializing_effect(self, gtk_paned, gtk_item_child_name, item_no):
        set_child_func = getattr(gtk_paned, f"set_{gtk_item_child_name}_child")
        if getattr(self.piece, f"is_showing_item_{item_no}") and (item := getattr(self.piece, f"item_{item_no}")):
            gtk_item_widget = self.materialize_child(item).native
            set_child_func(gtk_item_widget)
            getattr(gtk_paned, f"set_resize_{gtk_item_child_name}_child")(
                gtk_item_widget.compute_expand(Gtk.Orientation.HORIZONTAL))
            return

        set_child_func(None)

    async def __handle_resized(self, gtk_paned):
        gtk_widget_1, gtk_widget_2 = self.__item_gtk_widgets()
        height = gtk_paned.get_height()  # more correct would be to use gtk_box; but this behaves nicer
        item_1_current_width = gtk_widget_1.measure(Gtk.Orientation.HORIZONTAL, height)[0] if gtk_widget_1 else 0
        item_2_current_width = gtk_widget_2.measure(Gtk.Orientation.HORIZONTAL, height)[0] if gtk_widget_2 else 0
        with klovve.variable.pause_refreshing():
            self.piece._introspect.set_property_value(klovve.views.responsive.Dual._item_1_current_width_em,
                                                      item_1_current_width / klovve.builtin.drivers.gtk.em_to_px(1))
            self.piece._introspect.set_property_value(klovve.views.responsive.Dual._item_2_current_width_em,
                                                      item_2_current_width / klovve.builtin.drivers.gtk.em_to_px(1))
            self.piece._introspect.set_property_value(klovve.views.responsive.Dual._own_width_em,
                                                      gtk_paned.get_width() / klovve.builtin.drivers.gtk.em_to_px(1))

    def __item_gtk_widgets(self):
        return ((self.piece.item_1._materialization.native
                 if (self.piece.item_1 and self.piece.item_1._materialization) else None),
                (self.piece.item_2._materialization.native
                 if (self.piece.item_2 and self.piece.item_2._materialization) else None))

    def __set_control(self, gtk_inline_control_box):
        while gtk_old_child := gtk_inline_control_box.get_first_child():
            gtk_inline_control_box.remove(gtk_old_child)

        if self.piece._show_internal_toggle_button:
            gtk_inline_control_box.append(gtk_control_button := self.new_native(
                Gtk.Button, icon_name="media-playlist-repeat",
                halign=Gtk.Align.END))
            gtk_control_button.connect("clicked", lambda *_: self.piece._toggle_visibilities())

    class Paned(Gtk.Paned):

        def __init__(self, *args, _item_gtk_widgets_func, **kwargs):
            super().__init__(*args, **kwargs)
            self.__item_gtk_widgets_func = _item_gtk_widgets_func

        def do_get_request_mode(self):
            gtk_widget_1, gtk_widget_2 = self.__item_gtk_widgets_func()

            if gtk_widget_1 or gtk_widget_2:
                if gtk_widget_1 and gtk_widget_2:
                    mode_1 = gtk_widget_1.get_request_mode()
                    mode_2 = gtk_widget_2.get_request_mode()
                    if mode_1 == mode_2:
                        return mode_1
                else:
                    return (gtk_widget_1 or gtk_widget_2).get_request_mode()

            return Gtk.SizeRequestMode.CONSTANT_SIZE

        def do_measure(self, orientation, for_size):
            gtk_widget_1, gtk_widget_2 = self.__item_gtk_widgets_func()

            if gtk_widget_1 or gtk_widget_2:
                if gtk_widget_1 and gtk_widget_2:
                    measure_result_1 = gtk_widget_1.measure(orientation, for_size)
                    measure_result_2 = gtk_widget_2.measure(orientation, for_size)
                    return (max(measure_result_1[0], measure_result_2[0]),
                            max(measure_result_1[1], measure_result_2[1]), -1, -1)
                else:
                    return (gtk_widget_1 or gtk_widget_2).measure(orientation, for_size)

            return 0, 0, -1, -1


class DualControlButton(klovve.builtin.drivers.gtk.ViewMaterialization[klovve.views.responsive.DualControlButton]):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__refresh_ui_effect = None

    def create_native(self):
        gtk_box = self.new_native(Gtk.Box, self.piece)
        gtk_box.append(gtk_button := self.new_native(Gtk.Button))
        gtk_button.connect("clicked", lambda *_: self.piece.controller.toggle())

        klovve.effect.activate_effect(self.__connect_controller_effect, (gtk_box, gtk_button), owner=gtk_button)

        return gtk_box

    def __connect_controller_effect(self, gtk_box, gtk_button):
        if self.piece.controller:
            with klovve.variable.no_dependency_tracking():
                self.piece.controller._connect()
        if self.__refresh_ui_effect:
            klovve.effect.stop_effect(self.__refresh_ui_effect)
        self.__refresh_ui_effect = klovve.effect.activate_effect(
            self.__refresh_ui, (gtk_box, gtk_button, self.piece._connected_dual), owner=self)

    def __refresh_ui(self, gtk_box, gtk_button, dual):
        gtk_box.set_visible(dual and not dual.is_showing_both_items)
        gtk_button.set_label(
            self.piece.showing_item_1_text if (dual and dual.is_showing_item_1) else self.piece.showing_item_2_text)
