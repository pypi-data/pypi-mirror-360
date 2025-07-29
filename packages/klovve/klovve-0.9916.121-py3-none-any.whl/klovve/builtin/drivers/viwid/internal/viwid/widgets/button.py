#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
See :py:class:`Button`.
"""
import enum
import typing as t

import viwid.event.widget
import viwid.widgets
from viwid.widgets.widget import Widget as _Widget


class Decoration(enum.Enum):
    DEFAULT = enum.auto()
    NONE = enum.auto()


class Button(_Widget):
    """
    A button.

    It can be triggered by keyboard (navigate to it and press Enter) and by mouse and will trigger
    :py:class:`Button.TriggeredEvent` then.
    """

    def __init__(self, **kwargs):
        super().__init__(**{**dict(is_focusable=True, class_style_name="control",
                                   horizontal_alignment=viwid.Alignment.CENTER,
                                   vertical_alignment=viwid.Alignment.CENTER), **kwargs})

        self.__measure_input_text = None
        self.__left_border_text = self.__right_border_text = None

    text: str
    @_Widget.Property(default=lambda: "")
    def text(self, _):
        """
        The button text. Empty string by default.
        """
        self.__measure_input_text = self._text_measuring.text(_)
        self._request_resize_and_repaint()

    action: t.Any
    @_Widget.Property()
    def action(self, _):
        """
        The button action. `None` by default.

        This is an arbitrary object passed to the :py:class:`Button.TriggeredEvent` when the user has triggered this
        button.
        """

    decoration: t.Any
    @_Widget.Property(default=lambda: Decoration.DEFAULT)
    def decoration(self, _):
        """
        The button decoration mode. :py:attr:`Decoration.DEFAULT` by default.
        """
        self._request_resize_and_repaint()

    def _compute_width(self, minimal) -> int:
        decoration_width = 2 if (self.decoration == Decoration.DEFAULT) else 0
        return self._text_measuring.text_width(self.__measure_input_text) + decoration_width

    def _compute_height(self, width: int, minimal) -> int:
        decoration_width = 2 if (self.decoration == Decoration.DEFAULT) else 0
        return self._text_measuring.text_height(self.__measure_input_text, for_width=width-decoration_width) or 1

    def _materialize(self):
        super()._materialize()

        self.__left_border_text = self._text_measuring.text("▐")
        self.__right_border_text = self._text_measuring.text("▌")

        self.listen_event(viwid.event.mouse.ClickEvent, self.__handle_mouse_clicked, implements_default_behavior=True)
        self.listen_event(viwid.event.keyboard.KeyPressEvent, self.__handle_keyboard_key_pressed,
                          implements_default_behavior=True)

    def _dematerialize(self):
        self.unlisten_event(self.__handle_mouse_clicked)
        self.unlisten_event(self.__handle_keyboard_key_pressed)

        super()._dematerialize()

    def _paint(self, canvas):
        if self.decoration == Decoration.DEFAULT:
            canvas.fill(self._style(self.layer_style.control_shades),
                        rectangle=viwid.Rectangle(viwid.Point.ORIGIN, viwid.Size(1, self.size.height)))
            canvas.fill(self._style(self.layer_style.control_shades),
                        rectangle=viwid.Rectangle(viwid.Point(self.size.width-1, 0), viwid.Size(1, self.size.height)))

            for y in range(self.size.height):
                canvas.draw_text(self.__left_border_text,
                                 rectangle=viwid.Rectangle(viwid.Point(0, y), viwid.Size(1, 1)))
                canvas.draw_text(self.__right_border_text,
                                 rectangle=viwid.Rectangle(viwid.Point(self.size.width-1, y), viwid.Size(1, 1)))

        decoration_left = 1 if (self.decoration == Decoration.DEFAULT) else 0
        decoration_right = 1 if (self.decoration == Decoration.DEFAULT) else 0

        rendered_text = self.__measure_input_text.render(width=self.size.width-decoration_left-decoration_right)
        text_width = self.__measure_input_text.width()
        text_height = self.__measure_input_text.height()

        canvas.draw_text(rendered_text,
                         rectangle=viwid.Rectangle(
                             viwid.Point(
                                 decoration_left + max(0, int((self.size.width - decoration_left - decoration_right - text_width) / 2)),
                                 max(0, int((self.size.height - text_height) / 2))),
                             viwid.Size(text_width, text_height)))

    def __handle_mouse_clicked(self, event):
        if event.subject_button == viwid.event.mouse.ClickEvent.BUTTON_LEFT:
            self.screen_layer.trigger_event(self, Button.TriggeredEvent(self, self.action))
            self._is_activated = True

    def __handle_keyboard_key_pressed(self, event):
        if event.char and event.char in " \n":
            self.screen_layer.trigger_event(self, Button.TriggeredEvent(self, self.action))
            self._is_activated = True

    class TriggeredEvent(viwid.event.Event):
        """
        Event that occurs when the user triggers a button, either by clicking on it or pressing Enter when focused.
        """

        def __init__(self, button: "Button", action: object):
            super().__init__()
            self.__button = button
            self.__action = action

        @property
        def button(self) -> "Button":
            """
            The button that has triggered the action.
            """
            return self.__button

        @property
        def action(self) -> object:
            """
            The action of the triggered button. See :py:attr:`Button.action`.
            """
            return self.__action
