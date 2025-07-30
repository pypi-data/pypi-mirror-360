#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import klovve.builtin.drivers.viwid

import viwid


class Button(klovve.builtin.drivers.viwid.ViewMaterialization[klovve.views.Button]):

    def create_native(self):
        viwid_button = self.new_native(viwid.widgets.button.Button, self.piece, text=self.piece.bind.text)

        viwid_button.listen_event(viwid.widgets.button.Button.TriggeredEvent, lambda *_: self.piece._clicked())

        return viwid_button

    # TODO style
