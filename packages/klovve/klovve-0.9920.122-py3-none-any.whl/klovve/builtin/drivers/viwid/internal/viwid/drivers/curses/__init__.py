#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
Implementation for a viwid driver based on 'curses'.
"""
import asyncio
import curses
import locale

import viwid.drivers.curses.colors
import viwid.drivers.curses.event
import viwid.app.manager
import viwid.event
import viwid.text


class Driver(viwid.drivers.Driver):
    """
    A viwid driver based on 'curses'.
    """

    def __init__(self, event_loop: asyncio.BaseEventLoop|None):
        self.__cursor = None
        self.__curses_screen_window = None
        self.__curses_colors = None
        self.__measurement_curses_attributes = None
        self.__event_controller = viwid.drivers.curses.event.EventInternalSource()
        self.__use_fallback_colors = None
        super().__init__(event_loop=event_loop, application_manager=viwid.app.manager.ApplicationManager(self))
        self.__stripped_character_placeholder = self.apps.text_measuring.grapheme("´")

    def __enter__(self):
        self.__curses_screen_window = self.__create_curses_screen_window()
        self.__curses_colors = viwid.drivers.curses.colors.CursesColors(self)
        self.__use_fallback_colors = self.__curses_colors.color_mode == viwid.drivers.curses.colors.CursesColors.Mode.COLORS_8
        self.__measurement_curses_attributes = curses.color_pair(self.__curses_colors.color_pair("#000", "#000"))
        self.__event_controller.set_curses_screen_window(self.__curses_screen_window)
        self.__stripped_character_placeholder = self.apps.text_measuring.grapheme("´")
        self.apps.__enter__()
        super().__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        super().__exit__(exc_type, exc_val, exc_tb)
        self.apps.__exit__(exc_type, exc_val, exc_tb)
        self.__restore_non_cursed_terminal()

    def _read_event_internals(self):
        return self.__event_controller.read_event_internals()

    def _color_to_plain_color(self, color: viwid.Color) -> viwid.PlainColor:
        return color.fallback if self.__use_fallback_colors else color.base

    def determine_terminal_size(self):
        height, width = self.__curses_screen_window.getmaxyx()
        return viwid.Size(width, height)

    def measure_character_width(self, char):
        current_cursor_position = self.__curses_screen_window.getyx()

        self.__curses_screen_window.move(0, 0)
        self.__curses_screen_window.addstr(char, self.__measurement_curses_attributes)
        _, width = self.__curses_screen_window.getyx()

        self.apps.output_canvas._call_repainted_handlers(0, 1)

        self.__curses_screen_window.move(*current_cursor_position)

        return width

    def refresh_screen(self, source_canvas, line_indexes):
        for y in line_indexes:
            self.__curses_screen_window.redrawln(y, 1)
            ignore_next_n = 0

            line_attributes, line_graphemes = source_canvas.line(y)

            for x in range(self.apps.terminal_size.width):
                content = line_graphemes[x]
                block_attributes = line_attributes[x]

                if ignore_next_n > 0:
                    ignore_next_n -= 1
                elif (content := self.__character_if_complete_and_displayable(line_graphemes, x)) is not None:
                    ignore_next_n = content.width_on_screen - 1
                else:
                    content = self.__stripped_character_placeholder

                if content is not None:
                    try:
                        self.__curses_screen_window.addstr(y, x, content.as_str or " ", curses.color_pair(self.__curses_colors.color_pair(
                             block_attributes.foreground_color, block_attributes.background_color)))
                    except curses.error:
                        pass   # odd; but it will routinely raise an exception in the last bottom/right block

        if self.__cursor:
            self.__curses_screen_window.move(self.__cursor.y, self.__cursor.x)
            curses.curs_set(1)
        elif self.apps.terminal_size.width:
            self.__curses_screen_window.move(self.apps.terminal_size.height-1, self.apps.terminal_size.width-1)
            curses.curs_set(0)

    def set_cursor(self, position):
        self.__cursor = position
        self.refresh_screen(self.apps.output_canvas, ())

    def __character_if_complete_and_displayable(self, line, x: int) -> viwid.text.Grapheme|None:
        if (character := line[x]) is not None:
            if character.width_on_screen == 1:
                return character

            if x + character.width_on_screen <= self.apps.terminal_size.width:
                if all([line[x + i_x + 1] is None for i_x in range(character.width_on_screen - 1)]):
                    return character

    def __create_curses_screen_window(self) -> curses.window:
        locale.setlocale(locale.LC_ALL, "")
        # noinspection PyTypeChecker
        curses_screen_window: curses.window = curses.initscr()
        curses_screen_window.keypad(True)
        curses.raw()
        curses.curs_set(0)
        curses.noecho()
        curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
        # https://stackoverflow.com/questions/56300134/how-to-enable-mouse-movement-events-in-curses
        # https://invisible-island.net/xterm/ctlseqs/ctlseqs.html#h2-Mouse-Tracking
        print("\033[?1003h")  # otherwise mouse events do not work in some terminals
        curses.mouseinterval(0)
        curses.flushinp()
        try:
            curses.start_color()
        except:
            pass
        curses.cbreak()
        curses.halfdelay(1)
        return curses_screen_window

    def __restore_non_cursed_terminal(self):
        print("\033[?1003l")  # stop the terminal reporting mouse position
        curses.echo()
        curses.nocbreak()
        curses.endwin()
