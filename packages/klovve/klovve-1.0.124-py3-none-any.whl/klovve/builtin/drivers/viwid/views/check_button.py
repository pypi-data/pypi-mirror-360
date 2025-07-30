#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import klovve.builtin.drivers.viwid

import viwid


class CheckButton(klovve.builtin.drivers.viwid.ViewMaterialization[klovve.views.CheckButton]):

    def create_native(self):
        return self.new_native(viwid.widgets.check_button.CheckButton, self.piece, text=self.piece.bind.text,
                               is_checked=self.piece.bind.is_checked)

    # TODO style
