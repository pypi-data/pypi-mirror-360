#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import klovve.builtin.drivers.viwid

import viwid


class Slider(klovve.builtin.drivers.viwid.ViewMaterialization[klovve.views.Slider]):

    def create_native(self):
        viwid_slider = self.new_native(viwid.widgets.slider.Slider, self.piece)

        klovve.effect.activate_effect(self.__refresh_ui, (viwid_slider,), owner=self)
        viwid_slider.listen_property("value", lambda: self.__refresh_piece(viwid_slider))

        return viwid_slider

    def __refresh_ui(self, viwid_slider):
        viwid_slider.value_range = viwid.NumericValueRange(min_value=self.piece.min_value,
                                                           max_value=self.piece.max_value,
                                                           step_size=self.piece.value_step_size)
        viwid_slider.value = self.piece.value

    def __refresh_piece(self, viwid_slider):
        self.piece.value = viwid_slider.value
