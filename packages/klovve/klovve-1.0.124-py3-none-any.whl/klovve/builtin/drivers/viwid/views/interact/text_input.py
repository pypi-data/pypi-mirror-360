#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import klovve.builtin.drivers.viwid
import klovve.ui.utils

import viwid


class TextInput(klovve.builtin.drivers.viwid.ViewMaterialization[klovve.views.interact.TextInput]):

    def create_native(self):
        viwid_box = self.new_native(viwid.widgets.box.Box, self.piece,
                                    orientation=viwid.Orientation.VERTICAL)
        viwid_box.children.append(self.new_native(viwid.widgets.label.Label, text=self.piece._bind.message))
        viwid_box.children.append(viwid_text_entry := self.new_native(viwid.widgets.entry.Entry,
                                                                      text=self.piece.suggestion))
        viwid_box.children.append(viwid_message_choices_box := self.new_native(viwid.widgets.box.Box))
        viwid_message_choices_box.children.append(viwid_button_ok := self.new_native(
            viwid.widgets.button.Button, text=klovve.ui.utils.tr("OK")))
        viwid_message_choices_box.children.append(viwid_button_cancel := self.new_native(
            viwid.widgets.button.Button, text=klovve.ui.utils.tr("CANCEL")))

        viwid_button_ok.listen_event(viwid.widgets.button.Button.TriggeredEvent,
                                     lambda *_: self.piece._answer(self, viwid_text_entry.text))
        viwid_button_cancel.listen_event(viwid.widgets.button.Button.TriggeredEvent,
                                         lambda *_: self.piece._answer(self, None))

        return viwid_box
