#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import klovve


class _AbstractInteract[TAnswer](klovve.ui.Piece):

    is_answered: bool = klovve.ui.property(initial=False, is_settable=False)
    answer: TAnswer|None = klovve.ui.property(is_settable=False)

    class AnsweredEvent[TAnswer](klovve.event.Event):

        def __init__(self, triggering_view: "klovve.ui.View", answer: TAnswer):
            super().__init__()
            self.__triggering_view = triggering_view
            self.__answer = answer

        @property
        def triggering_view(self) -> "klovve.ui.View":
            return self.__triggering_view

        @property
        def answer(self) -> TAnswer:
            return self.__answer

    def _answer(self, triggering_view: "klovve.ui.View", answer: TAnswer) -> None:
        self._introspect.set_property_value(_AbstractInteract.answer, answer)
        self._introspect.set_property_value(_AbstractInteract.is_answered, True)
        self.trigger_event(_AbstractInteract.AnsweredEvent(triggering_view, answer))


from klovve.builtin.views.interact.message import Message
from klovve.builtin.views.interact.message_yes_no import MessageYesNo
from klovve.builtin.views.interact.text_input import TextInput
