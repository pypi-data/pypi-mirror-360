#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
See :py:class:`Dual`.
"""
import klovve.variable


class Dual(klovve.ui.Piece):
    """
    A responsive view that shows two child views. If there is enough space, it shows them side by side, with a movable
    splitter between them. If space is low, it only shows one of them and allows the user to switch between them.

    The UI for switching (mostly a simple button) can be either the inline one, or an external
    :py:class:`DualControlButton` that can be placed anywhere.
    """

    #: The 1st (i.e. right) child.
    item_1: klovve.ui.View|None = klovve.ui.property()
    #: The 2nd (i.e. left) child.
    item_2: klovve.ui.View|None = klovve.ui.property()

    #: Optional fixed minimal width for showing the child views side by side.
    show_both_items_min_width_em: int = klovve.ui.property(initial=0)

    #: Whether this view is currently showing :py:attr:`item_1`.
    is_showing_item_1: bool = klovve.ui.property(initial=False, is_settable=False)
    #: Whether this view is currently showing :py:attr:`item_2`.
    is_showing_item_2: bool = klovve.ui.property(initial=False, is_settable=False)

    def _(self):
        return self.is_showing_item_1 and self.is_showing_item_2
    #: Whether this view is currently showing both items.
    is_showing_both_items: bool = klovve.ui.computed_property(_)

    #: The controller. Used e.g. by :py:class:`DualControlButton`.
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
    """
    An external control button for switching between views of a :py:class:`Dual`.
    """

    #: The Dual controller. See :py:attr:`Dual.controller`.
    controller: Dual.Controller|None = klovve.ui.property()

    #: The button text when the 2nd item is currently shown (it would switch to the 1st one then).
    showing_item_1_text: str = klovve.ui.property(initial="switch view")
    #: The button text when the 1st item is currently shown (it would switch to the 2nd one then).
    showing_item_2_text: str = klovve.ui.property(initial="switch view")

    def _(self):
        return self.controller.dual if self.controller else None
    _connected_dual: Dual|None = klovve.ui.computed_property(_)
