#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import klovve.builtin.drivers.viwid

import viwid


class ProgressBar(klovve.builtin.drivers.viwid.ViewMaterialization[klovve.views.ProgressBar]):

    def create_native(self):
        return self.new_native(viwid.widgets.progress_bar.ProgressBar, self.piece, value=self.piece.bind.value)
