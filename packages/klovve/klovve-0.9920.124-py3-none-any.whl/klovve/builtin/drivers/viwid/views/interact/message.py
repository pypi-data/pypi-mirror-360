#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import klovve.builtin.drivers.viwid

import viwid


class Message(klovve.builtin.drivers.viwid.ViewMaterialization[klovve.views.interact.Message]):

    def create_native(self):
        viwid_box = self.new_native(viwid.widgets.box.Box, self.piece,
                                    orientation=viwid.Orientation.VERTICAL)
        viwid_box.children.append(self.new_native(viwid.widgets.label.Label, text=self.piece._bind.message))
        viwid_box.children.append(viwid_message_choices_box := self.new_native(viwid.widgets.box.Box))

        self.piece._introspect.observe_list_property(
            klovve.views.interact.Message.choices,
            klovve.builtin.drivers.viwid.ViewMaterialization.MaterializingViewsInViwidBoxObserver,
            (self, viwid_message_choices_box, self.__viwid_button_for_choice), owner=self)

        return viwid_box

    def __viwid_button_for_choice(self, choice):
        viwid_choice_button = self.new_native(viwid.widgets.button.Button, text=choice[0])
        viwid_choice_button.listen_event(viwid.widgets.button.Button.TriggeredEvent,
                                         lambda *_: self.piece._answer(self, choice[1]))
        return viwid_choice_button
