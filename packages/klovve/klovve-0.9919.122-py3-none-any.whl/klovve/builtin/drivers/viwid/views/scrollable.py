#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import klovve.builtin.drivers.viwid

import viwid


class Scrollable(klovve.builtin.drivers.viwid.ViewMaterialization[klovve.views.Scrollable]):

    def create_native(self):
        viwid_scrollable = self.new_native(viwid.widgets.scrollable.Scrollable, self.piece)

        klovve.effect.activate_effect(klovve.builtin.drivers.viwid.ViewMaterialization.MaterializingViewEffect,
                                      (self, viwid_scrollable, lambda: self.piece.body), owner=self)

        return viwid_scrollable
