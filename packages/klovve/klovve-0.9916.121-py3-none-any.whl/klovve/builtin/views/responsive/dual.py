#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import klovve.variable


class Dual(klovve.ui.Piece):

    item_1: klovve.ui.View|None = klovve.ui.property()
    item_2: klovve.ui.View|None = klovve.ui.property()

    show_both_items_min_width_em: int = klovve.ui.property(initial=0)

    is_showing_item_1: bool = klovve.ui.property(initial=False, is_settable=False)
    is_showing_item_2: bool = klovve.ui.property(initial=False, is_settable=False)

    def _(self):
        return self.is_showing_item_1 and self.is_showing_item_2
    is_showing_both_items: bool = klovve.ui.computed_property(_)

    controller: "Controller" = klovve.ui.property(is_settable=False)

    _last_single_item_shown: int = klovve.ui.property(initial=0, is_settable=False)

    _is_controller_connected: bool = klovve.ui.property(initial=False, is_settable=False)

    _item_1_current_width_em: int = klovve.ui.property(initial=0, is_settable=False)
    _item_2_current_width_em: int = klovve.ui.property(initial=0, is_settable=False)
    _splitter_width_em: int = klovve.ui.property(initial=0, is_settable=False)
    _own_width_em: int = klovve.ui.property(initial=0, is_settable=False)

    def _(self):
        return not self._is_controller_connected and not self.is_showing_both_items and self.item_1 and self.item_2
    _show_internal_toggle_button: bool = klovve.ui.computed_property(_)

    class Controller:

        def __init__(self, dual: "Dual"):
            self.__dual = dual

        @property
        def dual(self) -> "Dual":
            return self.__dual

        def toggle(self):
            self.__dual._toggle_visibilities()

        def _connect(self):
            self.__dual._introspect.set_property_value(klovve.views.responsive.Dual._is_controller_connected, True)

    def __init_object__(self):
        self._introspect.set_property_value(Dual.controller, Dual.Controller(self))
        klovve.effect.activate_effect(self.__refresh_item_visibilities, owner=self)

    def __refresh_item_visibilities(self):
        with klovve.variable.pause_refreshing():
            if self.item_1 and self.item_2:

                if self._own_width_em < max(
                        (self._item_1_current_width_em + self._item_2_current_width_em + self._splitter_width_em),
                        self.show_both_items_min_width_em):
                    self._introspect.set_property_value(klovve.views.responsive.Dual.is_showing_item_1,
                                                        self._last_single_item_shown==0)
                    self._introspect.set_property_value(klovve.views.responsive.Dual.is_showing_item_2,
                                                        self._last_single_item_shown==1)
                    return

            self._introspect.set_property_value(klovve.views.responsive.Dual.is_showing_item_1, True)
            self._introspect.set_property_value(klovve.views.responsive.Dual.is_showing_item_2, True)

    def _toggle_visibilities(self):
        with klovve.variable.pause_refreshing():
            self._introspect.set_property_value(Dual._last_single_item_shown, (self._last_single_item_shown + 1) % 2)
            self._introspect.set_property_value(klovve.views.responsive.Dual.is_showing_item_1,
                                                not self.is_showing_item_1)
            self._introspect.set_property_value(klovve.views.responsive.Dual.is_showing_item_2,
                                                not self.is_showing_item_2)


class DualControlButton(klovve.ui.Piece):

    controller: Dual.Controller|None = klovve.ui.property()

    showing_item_1_text: str = klovve.ui.property(initial="switch view")
    showing_item_2_text: str = klovve.ui.property(initial="switch view")

    def _(self):
        return self.controller.dual if self.controller else None
    _connected_dual: Dual|None = klovve.ui.computed_property(_)
