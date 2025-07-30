#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import klovve.builtin.drivers.viwid

import viwid


class Image(klovve.builtin.drivers.viwid.ViewMaterialization[klovve.views.viewer.Image]):

    def create_native(self):
        return self.new_native(viwid.widgets.label.Label, self.piece)
