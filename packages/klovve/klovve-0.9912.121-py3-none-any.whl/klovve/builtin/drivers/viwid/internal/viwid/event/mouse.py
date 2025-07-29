#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
Events related to mouse input.
"""
import typing as t

import viwid
from viwid.event import Event as _BaseEvent

if t.TYPE_CHECKING:
    import viwid.widgets.widget


class _Event(_BaseEvent):

    #: The left mouse button.
    BUTTON_LEFT = 0
    #: The middle mouse button.
    BUTTON_MIDDLE = 1
    #: The right mouse button.
    BUTTON_RIGHT = 2

    def __init__(self, grab_mouse_func, touched_widget: "viwid.widgets.widget.Widget|None",
                 screen_position: viwid.Point, pressed_buttons: t.Iterable[bool], with_shift: bool, with_alt: bool,
                 with_ctrl: bool):
        super().__init__()
        self.__touched_widget = touched_widget
        self.__screen_position = screen_position
        self.__pressed_buttons = tuple(pressed_buttons)
        self.__grab_mouse_func = grab_mouse_func
        self.__with_shift = with_shift
        self.__with_alt = with_alt
        self.__with_ctrl = with_ctrl

    @property
    def touched_widget(self) -> "viwid.widgets.widget.Widget|None":
        """
        The widget that was touched by this mouse event (the innermost one).
        """
        return self.__touched_widget

    @property
    def _pressed_buttons(self) -> tuple[bool, ...]:
        return self.__pressed_buttons

    @property
    def screen_position(self) -> viwid.Point:
        """
        The screen position of the mouse cursor.
        """
        return self.__screen_position

    @property
    def with_shift(self) -> bool:
        """
        Whether 'shift' was pressed while the event occurred.
        """
        return self.__with_shift

    @property
    def with_alt(self) -> bool:
        """
        Whether 'alt' was pressed while the event occurred.
        """
        return self.__with_alt

    @property
    def with_ctrl(self) -> bool:
        """
        Whether 'ctrl' was pressed while the event occurred.
        """
        return self.__with_ctrl

    def is_button_pressed(self, i: int) -> bool:
        """
        Return whether a given mouse button was down while the event occurred.

        :param i: The button index.
        """
        return i < len(self.__pressed_buttons) and self.__pressed_buttons[i]

    @property
    def is_left_button_pressed(self) -> bool:
        """
        Return whether the left mouse button was down while the event occurred.
        """
        return self.is_button_pressed(_Event.BUTTON_LEFT)

    @property
    def is_middle_button_pressed(self) -> bool:
        """
        Return whether the middle mouse button was down while the event occurred.
        """
        return self.is_button_pressed(_Event.BUTTON_MIDDLE)

    @property
    def is_right_button_pressed(self) -> bool:
        """
        Return whether the right mouse button was down while the event occurred.
        """
        return self.is_button_pressed(_Event.BUTTON_RIGHT)

    def grab_mouse(self, widget: "viwid.widgets.widget.Widget") -> t.ContextManager[None]:
        """
        Grab the mouse. This returns a context manager. As long as this context is entered, all mouse events will
        consider the given widget as the touched one, even when the cursor actually touches another one.

        This is used for mouse based move operation, e.g. internally for splitters and movable window title bars.

        :param widget: The widget to consider as the touched one.
        """
        return self.__grab_mouse_func(widget)


class _ButtonEvent(_Event):

    def __init__(self, grab_mouse_func, touched_widget: "viwid.widgets.widget.Widget|None",
                 screen_position: viwid.Point, pressed_buttons: t.Iterable[bool], subject_button: int, with_shift: bool,
                 with_alt: bool, with_ctrl: bool):
        super().__init__(grab_mouse_func, touched_widget, screen_position, pressed_buttons, with_shift, with_alt,
                         with_ctrl)
        self.__subject_button = subject_button

    @property
    def subject_button(self) -> int:
        return self.__subject_button


class MoveEvent(_Event):
    """
    Event that occurs when the user moves the mouse cursor.
    """

    def __init__(self, grab_mouse_func, touched_widget: "viwid.widgets.widget.Widget|None",
                 screen_position: viwid.Point, pressed_buttons: t.Iterable[bool], with_shift: bool, with_alt: bool,
                 with_ctrl: bool):
        super().__init__(grab_mouse_func, touched_widget, screen_position, pressed_buttons, with_shift, with_alt,
                         with_ctrl)


class ButtonDownEvent(_ButtonEvent):
    """
    Event that occurs when the user presses a mouse button down.

    See also :py:class:`ClickEvent`.
    """

    def __init__(self, grab_mouse_func, touched_widget: "viwid.widgets.widget.Widget|None",
                 screen_position: viwid.Point, pressed_buttons: t.Iterable[bool], subject_button: int, with_shift: bool,
                 with_alt: bool, with_ctrl: bool):
        super().__init__(grab_mouse_func, touched_widget, screen_position, pressed_buttons, subject_button, with_shift,
                         with_alt, with_ctrl)


class ButtonUpEvent(_ButtonEvent):
    """
    Event that occurs when the user releases a mouse button.

    See also :py:class:`ClickEvent`.
    """

    def __init__(self, grab_mouse_func, touched_widget: "viwid.widgets.widget.Widget|None",
                 screen_position: viwid.Point, pressed_buttons: t.Iterable[bool], subject_button: int, with_shift: bool,
                 with_alt: bool, with_ctrl: bool):
        super().__init__(grab_mouse_func, touched_widget, screen_position, pressed_buttons, subject_button, with_shift,
                         with_alt, with_ctrl)


class ClickEvent(_ButtonEvent):
    """
    Event that occurs when the user presses and releases a mouse button without moving the cursor meanwhile.
    """

    def __init__(self, grab_mouse_func, touched_widget: "viwid.widgets.widget.Widget|None",
                 screen_position: viwid.Point, pressed_buttons: t.Iterable[bool], subject_button: int, with_shift: bool,
                 with_alt: bool, with_ctrl: bool):
        super().__init__(grab_mouse_func, touched_widget, screen_position, pressed_buttons, subject_button, with_shift,
                         with_alt, with_ctrl)


class ScrollEvent(_Event):
    """
    Event that occurs when the user turns the mouse scroll wheel.
    """

    def __init__(self, grab_mouse_func, touched_widget: "viwid.widgets.widget.Widget|None",
                 screen_position: viwid.Point, pressed_buttons: t.Iterable[bool], direction: int, with_shift: bool,
                 with_alt: bool, with_ctrl: bool):
        super().__init__(grab_mouse_func, touched_widget, screen_position, pressed_buttons, with_shift, with_alt,
                         with_ctrl)
        self.__direction = direction

    @property
    def direction(self) -> int:
        """
        The scroll direction. Positive values mean upward scrolling and negative ones mean downward scrolling.
        """
        return self.__direction
