#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import klovve.builtin.drivers.viwid

import viwid


class Placeholder(klovve.builtin.drivers.viwid.ViewMaterialization[klovve.views.Placeholder]):

    def create_native(self):
        viwid_box = self.new_native(viwid.widgets.box.Box, self.piece)

        klovve.effect.activate_effect(klovve.builtin.drivers.viwid.ViewMaterialization.MaterializingViewEffect,
                                      (self, viwid_box, lambda: self.piece.body), owner=self)

        return viwid_box
