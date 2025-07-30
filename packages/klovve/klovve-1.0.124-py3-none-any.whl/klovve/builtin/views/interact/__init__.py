#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
See :py:class:`AbstractInteract`.
"""
import klovve


class AbstractInteract[TAnswer](klovve.ui.Piece):
    """
    Base class for a view that allows the user to 'give an answer' (e.g. by choosing one of several buttons or entering
    some text) and so can be used in simple dialogs.

    When the user has answered this interaction, :py:class:`AbstractInteract.AnsweredEvent` gets triggered.
    """

    #: Whether the user has already given an answer.
    is_answered: bool = klovve.ui.property(initial=False, is_settable=False)
    #: The answer that the user has given.
    answer: TAnswer|None = klovve.ui.property(is_settable=False)

    class AnsweredEvent[TAnswer](klovve.event.Event):
        """
        Event that occurs when the user has answered an interaction.
        """

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
        """
        Called by implementations when the user has answered this interaction.

        :param triggering_view: The triggering view.
        :param answer: The answer.
        """
        self._introspect.set_property_value(AbstractInteract.answer, answer)
        self._introspect.set_property_value(AbstractInteract.is_answered, True)
        self.trigger_event(AbstractInteract.AnsweredEvent(triggering_view, answer))


from klovve.builtin.views.interact.message import Message
from klovve.builtin.views.interact.message_yes_no import MessageYesNo
from klovve.builtin.views.interact.text_input import TextInput
