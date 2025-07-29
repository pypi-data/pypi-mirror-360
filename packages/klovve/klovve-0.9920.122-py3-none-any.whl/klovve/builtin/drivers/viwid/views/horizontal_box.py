#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import klovve.builtin.drivers.viwid.views._box

import viwid


class HorizontalBox(klovve.builtin.drivers.viwid.views._box.Box[klovve.views.HorizontalBox]):

    @property
    def _orientation(self):
        return viwid.Orientation.HORIZONTAL
