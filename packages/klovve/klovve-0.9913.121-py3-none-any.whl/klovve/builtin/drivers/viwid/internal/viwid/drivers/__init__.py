#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
Drivers make the connection between viwid and the real world. A driver is responsible for bringing output to the screen
and for retrieving the user's input.

See :py:class:`Driver`.
"""
import abc
import asyncio
import typing as t

import viwid.app.manager
import viwid.app.screen
import viwid.canvas
import viwid.data.color


class Driver(abc.ABC):
    """
    A driver is responsible for bringing output to the screen, for retrieving the user's input, and some other things.

    At the moment, there is only one driver available. :py:class:`viwid.drivers.curses.Driver` is a driver that
    internally uses 'curses' for its duties.
    """

    def __init__(self, *, event_loop: asyncio.BaseEventLoop,
                 application_manager: "viwid.app.manager.ApplicationManager"):
        """
        :param event_loop: The event loop that will host our applications.
        :param application_manager: The application manager.
        """
        self.__event_loop = event_loop
        self.__application_manager = application_manager
        self.__refresh_lines = []
        self.__entered = False
        self.__running = False

    @property
    def event_loop(self) -> asyncio.BaseEventLoop:
        """
        The event loop that hosts our applications.
        """
        return self.__event_loop

    @property
    def apps(self) -> "viwid.app.manager.ApplicationManager":
        """
        The application manager.
        """
        return self.__application_manager

    def plain_color(self, color: viwid.data.color.TColorInput) -> viwid.PlainColor:
        """
        Determine the :py:class:`viwid.PlainColor` to use for a given :py:class:`viwid.Color`.

        The latter one contains a color for different terminal capabilities, so you can use different colors for
        terminals with only low color support.

        This function basically returns the right actual color, depending on the terminal capabilities.

        :param color: The color.
        """
        return self._color_to_plain_color(color) if isinstance(color, viwid.Color) else viwid.PlainColor.get(color)

    @abc.abstractmethod
    def determine_terminal_size(self) -> viwid.Size:
        """
        Determine and return the current terminal size.
        """

    @abc.abstractmethod
    def measure_character_width(self, char: str) -> int:
        """
        Measure the width on screen for a string that represents a single grapheme.

        In higher levels, this is used for determining the width of a :py:class:`viwid.text.Grapheme`. There could be
        characters (many emojis for example) that take one single block on the screen - but the block has double the
        usual width or even more. In this case, this function returns that high value. So, it does not only consider
        the number of blocks used by the string, but also how wide those blocks are!

        The given string must be smaller than the screen in width, and must only have a height of 1 (i.e. there must be
        no linebreaks).

        It is mostly used internally by :py:class:`viwid.text.TextMeasuring` in order to measure graphemes. Use that
        class instead!

        :param char: The string to measure.
        """

    @abc.abstractmethod
    def set_cursor(self, position: viwid.Point|None) -> None:
        """
        Set the cursor position.

        There is no program logic that depends on this cursor position. It does not change the behavior of the
        application to change it. It only shows a visual indicator, usually a blinking block or line, so the user can
        see where her/his next text input will appear.

        The cursor is basically relevant for text input fields. In most other cases, there will be no cursor at all.

        :param position: The new cursor position, or `None` for no cursor.
        """

    @abc.abstractmethod
    def refresh_screen(self, source_canvas: "viwid.canvas.Canvas", line_indexes: t.Iterable[int]) -> None:
        """
        Refresh the given lines of the screen.

        :param source_canvas: The canvas that contains the recent screen content.
        :param line_indexes: The line indexes to refresh.
        """

    @abc.abstractmethod
    def _color_to_plain_color(self, color: viwid.Color) -> viwid.PlainColor:
        """
        Determine the :py:class:`viwid.PlainColor` to use for a given :py:class:`viwid.Color`.

        Drivers have to implement this method, but all code outside of drivers should not use this method directly!
        Use :py:meth:`plain_color` instead!

        :param color: The color.
        """

    @abc.abstractmethod
    def _read_event_internals(self) -> t.Sequence["EventInternals.EventInternal"]:
        """
        Return all the "event internals" that occurred since the last call (non-blocking).

        See :py:class:`EventInternals`.
        """

    def __handle_output_canvas_repainted(self, from_line: int, to_line: int) -> None:
        if to_line > len(self.__refresh_lines):
            self.__refresh_lines += (to_line - len(self.__refresh_lines)) * (False,)
        for i in range(from_line, to_line):
            self.__refresh_lines[i] = True

    def __enter__(self):
        if self.__entered:
            return
        self.__entered = True

        self.apps.output_canvas.add_repainted_handler(self.__handle_output_canvas_repainted)

        if not self.__running:
            self.__running = True
            self.__run()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.__entered:
            return
        self.__entered = False

        self.apps.output_canvas.remove_repainted_handler(self.__handle_output_canvas_repainted)

    def __run(self) -> None:
        if self.__entered:
            self.apps.handle_event_internals(self._read_event_internals())

            screen_height = self.apps.terminal_size.height
            self.__refresh_lines, refresh_lines = [], self.__refresh_lines
            self.refresh_screen(self.apps.output_canvas,
                                [i_refresh_line for i_refresh_line, refresh_line in enumerate(refresh_lines)
                                 if refresh_line and 0 <= i_refresh_line < screen_height])

            self.event_loop.call_soon(self.__run)
        else:
            self.__running = False


def start(event_loop: asyncio.BaseEventLoop|None = None) -> "Driver":
    """
    Start a viwid driver.

    This initializes and enables the driver and then returns. After this moment, viwid is integrated into your event
    loop, so it can continuously retrieve user input and refresh the screen until you call :py:func:`stop`.

    :param event_loop: The event loop to use. It may be already running or not (in the latter case, you have to run
                       it afterward in order to make your viwid application work). If unspecified, use the one that
                       is already running for the current thread, or create a new one.
    """
    global _current

    if _current is not None:
        raise RuntimeError("there is already a current driver")

    if event_loop is None:
        try:
            event_loop = asyncio.get_running_loop()
        except RuntimeError:
            event_loop = asyncio.new_event_loop()

    import viwid.drivers.curses as curses_driver
    _current = curses_driver.Driver(event_loop)

    _current.__enter__()

    return _current


def stop() -> None:
    """
    Stop the viwid driver.
    """
    global _current

    if _current is None:
        raise RuntimeError("there is no current driver")

    _current.__exit__(None, None, None)

    _current = None


def current() -> "Driver|None":
    """
    Return the currently running viwid driver.
    """
    global _current
    return _current


_current = None


class EventInternals:
    """
    See :py:class:`EventInternals.EventInternal`.
    """

    class EventInternal:
        """
        Event internals (see also its subclasses) are a raw, premature representation of events that directly come from
        outside, like user input. These objects are generated at driver level, but get translated by the infrastructure
        to actual events (see :py:class:`viwid.event.Event`). Higher levels do not deal with event internals.
        """

    class KeyboardKeyPressedEventInternal(EventInternal):
        """
        Event internal that occurs when the user presses a keyboard key.
        """

        def __init__(self, key_code: tuple[int, ...], with_shift: bool, with_alt: bool, with_ctrl: bool):
            super().__init__()
            self.key_code = key_code
            self.with_shift = with_shift
            self.with_alt = with_alt
            self.with_ctrl = with_ctrl

    class MouseButtonDownEventInternal(EventInternal):
        """
        Event internal that occurs when the user presses a mouse button down.
        """

        def __init__(self, mouse_position: viwid.Point, button: int, with_shift: bool, with_alt: bool, with_ctrl: bool):
            super().__init__()
            self.mouse_position = mouse_position
            self.button = button
            self.with_shift = with_shift
            self.with_alt = with_alt
            self.with_ctrl = with_ctrl

    class MouseButtonUpEventInternal(EventInternal):
        """
        Event internal that occurs when the user releases a mouse button.
        """

        def __init__(self, mouse_position: viwid.Point, button: int, with_shift: bool, with_alt: bool, with_ctrl: bool):
            super().__init__()
            self.mouse_position = mouse_position
            self.button = button
            self.with_shift = with_shift
            self.with_alt = with_alt
            self.with_ctrl = with_ctrl

    class MouseScrollEventInternal(EventInternal):
        """
        Event internal that occurs when the user turns the mouse scroll wheel.
        """

        def __init__(self, mouse_position: viwid.Point, direction: int, with_shift: bool, with_alt: bool,
                     with_ctrl: bool):
            super().__init__()
            self.mouse_position = mouse_position
            self.direction = direction
            self.with_shift = with_shift
            self.with_alt = with_alt
            self.with_ctrl = with_ctrl

    class MouseMoveEventInternal(EventInternal):
        """
        Event internal that occurs when the user moves the mouse cursor.
        """

        def __init__(self, mouse_position: viwid.Point, with_shift: bool, with_alt: bool, with_ctrl: bool):
            super().__init__()
            self.mouse_position = mouse_position
            self.with_shift = with_shift
            self.with_alt = with_alt
            self.with_ctrl = with_ctrl

    class ScreenResizedEventInternal(EventInternal):
        """
        Event internal that occurs when the screen size changes.
        """

        def __init__(self):
            super().__init__()
