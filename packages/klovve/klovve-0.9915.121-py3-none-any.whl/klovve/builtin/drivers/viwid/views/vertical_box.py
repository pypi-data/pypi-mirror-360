#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import klovve.builtin.drivers.viwid.views._box

import viwid


class VerticalBox(klovve.builtin.drivers.viwid.views._box.Box[klovve.views.VerticalBox]):

    @property
    def _orientation(self):
        return viwid.Orientation.VERTICAL
