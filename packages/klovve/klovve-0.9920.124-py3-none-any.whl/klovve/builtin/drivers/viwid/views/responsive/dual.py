#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import typing as t

import klovve.builtin.drivers.viwid
import klovve.driver
import klovve.variable

import viwid


class Dual(klovve.builtin.drivers.viwid.ViewMaterialization[klovve.views.responsive.Dual]):

    def create_native(self):
        viwid_box = self.new_native(viwid.widgets.box.Box, self.piece,
                                    orientation=viwid.Orientation.VERTICAL)
        viwid_box.children.append(viwid_inline_control_box := self.new_native(
            viwid.widgets.box.Box, orientation=viwid.Orientation.VERTICAL, vertical_alignment=viwid.Alignment.START))
        viwid_box.children.append(viwid_split := self.new_native(viwid.widgets.split.Split))

        self.piece._introspect.set_property_value(klovve.views.responsive.Dual._splitter_width_em, 0.5)  # TODO do in an effect (it depends on the orientation)
        klovve.effect.activate_effect(self.__item_materializing_effect, (viwid_split, 1), owner=self)
        klovve.effect.activate_effect(self.__item_materializing_effect, (viwid_split, 2), owner=self)
        klovve.effect.activate_effect(self.__set_control, (viwid_inline_control_box,), owner=self)
        viwid_box.listen_event(
            viwid.event.widget.ResizeEvent,
            lambda event: klovve.driver.Driver.get().loop.enqueue(self.__handle_resized(viwid_split)))

        return viwid_box

    def __item_materializing_effect(self, viwid_split, item_no):
        viwid_item_child_name = f"item_{item_no}"
        if getattr(self.piece, f"is_showing_item_{item_no}") and (item := getattr(self.piece, f"item_{item_no}")):
            setattr(viwid_split, viwid_item_child_name, self.materialize_child(item).native)
        else:
            setattr(viwid_split, viwid_item_child_name, None)

    async def __handle_resized(self, viwid_split):
        viwid_widget_1, viwid_widget_2 = self.__item_viwid_widgets()
        height = viwid_split.size.height  # more correct would be to use viwid_box; but this behaves nicer
        item_1_current_width = viwid_widget_1.width_demand_for_height(height) if viwid_widget_1 else 0
        item_2_current_width = viwid_widget_2.width_demand_for_height(height) if viwid_widget_2 else 0
        with klovve.variable.pause_refreshing():
            self.piece._introspect.set_property_value(
                klovve.views.responsive.Dual._item_1_current_width_em,
                item_1_current_width / klovve.builtin.drivers.viwid.em_to_block_count(1, "horizontal"))
            self.piece._introspect.set_property_value(
                klovve.views.responsive.Dual._item_2_current_width_em,
                item_2_current_width / klovve.builtin.drivers.viwid.em_to_block_count(1, "horizontal"))
            self.piece._introspect.set_property_value(
                klovve.views.responsive.Dual._own_width_em,
                0.5 / klovve.builtin.drivers.viwid.em_to_block_count(1, "horizontal"))

    def __item_viwid_widgets(self):
        return ((self.piece.item_1._materialization.native
                 if (self.piece.item_1 and self.piece.item_1._materialization) else None),
                (self.piece.item_2._materialization.native
                 if (self.piece.item_2 and self.piece.item_2._materialization) else None))

    def __set_control(self, viwid_inline_control_box):
        viwid_inline_control_box.children = ()

        if self.piece._show_internal_toggle_button:
            viwid_inline_control_box.children.append(viwid_control_button := self.new_native(
                viwid.widgets.button.Button, text="<->", horizontal_alignment=viwid.Alignment.END))
            viwid_control_button.listen_event(viwid.widgets.button.Button.TriggeredEvent,
                                              lambda *_: self.piece._toggle_visibilities())


class DualControlButton(klovve.builtin.drivers.viwid.ViewMaterialization[klovve.views.responsive.DualControlButton]):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__refresh_ui_effect = None

    def create_native(self):
        viwid_box = self.new_native(viwid.widgets.box.Box, self.piece)
        viwid_box.children.append(viwid_button := self.new_native(viwid.widgets.button.Button))
        viwid_button.listen_event(viwid.widgets.button.Button.TriggeredEvent,
                                  lambda *_: self.piece.controller.toggle())

        klovve.effect.activate_effect(self.__connect_controller_effect, (viwid_box, viwid_button), owner=viwid_button)

        return viwid_box

    def __connect_controller_effect(self, viwid_box, viwid_button):
        if self.piece.controller:
            with klovve.variable.no_dependency_tracking():
                self.piece.controller._connect()
        if self.__refresh_ui_effect:
            klovve.effect.stop_effect(self.__refresh_ui_effect)
        self.__refresh_ui_effect = klovve.effect.activate_effect(
            self.__refresh_ui, (viwid_box, viwid_button, self.piece._connected_dual), owner=self)

    def __refresh_ui(self, viwid_box, viwid_button, dual):
        viwid_box.set_visible(dual and not dual.is_showing_both_items)
        viwid_button.set_label(
            self.piece.showing_item_1_text if (dual and dual.is_showing_item_1) else self.piece.showing_item_2_text)
