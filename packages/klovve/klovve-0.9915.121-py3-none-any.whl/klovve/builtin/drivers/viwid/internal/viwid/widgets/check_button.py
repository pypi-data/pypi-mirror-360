#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
See :py:class:`CheckButton`.
"""
import viwid.event
import viwid.layout
import viwid.widgets
from viwid.widgets.widget import Widget as _Widget


class CheckButton(_Widget):
    """
    A checkable button with a text label.
    """

    def __init__(self, **kwargs):
        super().__init__(**{**dict(layout=viwid.layout.GridLayout(viwid.layout.GridLayout.HORIZONTAL_PARTITIONER),
                                   horizontal_alignment=viwid.Alignment.CENTER,
                                   vertical_alignment=viwid.Alignment.CENTER),
                            **kwargs})
        self.__button = viwid.widgets.button.Button()
        self.__label = viwid.widgets.label.Label()
        self._children = [self.__button, self.__label]

    def _materialize(self):
        super()._materialize()

        self.__label.listen_event(viwid.event.mouse.ClickEvent, self.__handle_mouse_clicked,
                                  implements_default_behavior=True)
        self.__button.listen_event(viwid.widgets.button.Button.TriggeredEvent, self.__handle_button_triggered,
                                   implements_default_behavior=True)

    def _dematerialize(self):
        self.__label.unlisten_event(self.__handle_mouse_clicked)
        self.__button.unlisten_event(self.__handle_button_triggered)

        super()._dematerialize()

    is_checked: bool
    @_Widget.Property(default=lambda: False)
    def is_checked(self, _):
        """
        Whether this check button is checked. `False` by default.
        """
        self.__button.text = "x" if _ else " "

    text: str
    @_Widget.Property(default=lambda: "")
    def text(self, _: str):
        """
        The label text. Empty string by default.
        """
        self.__label.text = _

    _is_uncheckable_by_user: bool
    @_Widget.Property(default=lambda: True)
    def _is_uncheckable_by_user(self, _: bool):
        """
        Whether this check button is uncheckable by the user. `True` by default.

        This is primarily used internally for the radio button implementation.
        """

    def __handle_mouse_clicked(self, event):
        if event.subject_button == viwid.event.mouse.ClickEvent.BUTTON_LEFT:
            self.__handle_button_triggered(event)
            self.__button.try_focus()
        event.stop_handling()

    def __handle_button_triggered(self, event):
        self.is_checked = not self.is_checked or not self._is_uncheckable_by_user
        event.stop_handling()
