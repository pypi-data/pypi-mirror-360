#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import klovve.builtin.drivers.viwid

import viwid


class TextField(klovve.builtin.drivers.viwid.ViewMaterialization[klovve.views.TextField]):

    def create_native(self):
        return self.new_native(viwid.widgets.entry.Entry, self.piece, text=self.piece.bind.text,
                               hint_text=self.piece.bind(two_way=False).hint_text)
