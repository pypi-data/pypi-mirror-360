#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import curses

import viwid.drivers


class EventInternalSource:

    def __init__(self):
        super().__init__()
        self.__curses_screen_window = None
        self.__mouse_position = viwid.Point.ORIGIN
        self.__next_keyboard_key_is_with_alt_or_last_was_esc = False

    def set_curses_screen_window(self, curses_screen_window: curses.window):
        self.__curses_screen_window = curses_screen_window

    def read_event_internals(self):
        EventInternals = viwid.drivers.EventInternals
        event_internals = []

        self.__next_keyboard_key_is_with_alt_or_last_was_esc = False
        while True:
            try:
                key = self.__curses_screen_window.get_wch()

                if key == curses.KEY_RESIZE:
                    event_internals.append(EventInternals.ScreenResizedEventInternal())

                elif key == curses.KEY_MOUSE:
                    curses_mouse_event = curses.getmouse()
                    mouse_position = viwid.Point(curses_mouse_event[1], curses_mouse_event[2])
                    with_shift, with_alt, with_ctrl, buttons_pressed, buttons_released, buttons_clicked = self.__process_input__mouse_buttons(
                        curses_mouse_event)
                    for i_button, was_button_clicked in enumerate(buttons_clicked):
                        if was_button_clicked and i_button in EventInternalSource.MOUSE_NORMAL_BUTTONS:
                            event_internals.append(
                                EventInternals.MouseButtonDownEventInternal(mouse_position, i_button, with_shift, with_alt, with_ctrl))
                            event_internals.append(EventInternals.MouseButtonUpEventInternal(mouse_position, i_button, with_shift, with_alt, with_ctrl))
                    if self.__mouse_position != mouse_position:
                        event_internals.append(EventInternals.MouseMoveEventInternal(mouse_position, with_shift, with_alt, with_ctrl))
                    for i_button, was_button_pressed in enumerate(buttons_pressed):
                        if was_button_pressed and i_button in EventInternalSource.MOUSE_NORMAL_BUTTONS:
                            event_internals.append(
                                EventInternals.MouseButtonDownEventInternal(mouse_position, i_button, with_shift, with_alt, with_ctrl))
                        elif was_button_pressed and i_button in (EventInternalSource.MOUSE_SCROLL_DOWN_BUTTON,
                                                                 EventInternalSource.MOUSE_SCROLL_UP_BUTTON):
                            direction = 1 if (i_button == EventInternalSource.MOUSE_SCROLL_DOWN_BUTTON) else -1
                            event_internals.append(EventInternals.MouseScrollEventInternal(mouse_position, direction, with_shift, with_alt, with_ctrl))
                    for i_button, was_button_released in enumerate(buttons_released):
                        if was_button_released and i_button in EventInternalSource.MOUSE_NORMAL_BUTTONS:
                            event_internals.append(EventInternals.MouseButtonUpEventInternal(mouse_position, i_button, with_shift, with_alt, with_ctrl))
                    self.__mouse_position = mouse_position

                else:
                    if isinstance(key, str):
                        key = ord(key)
                    key_code, with_shift, with_alt, with_ctrl = self.__process_input__keyboard_key_combination(key)
                    if key_code is not None:
                        event_internals.append(EventInternals.KeyboardKeyPressedEventInternal(key_code, with_shift,
                                                                                               with_alt, with_ctrl))

            except curses.error:
                break

        if self.__next_keyboard_key_is_with_alt_or_last_was_esc:
            event_internals.append(EventInternals.KeyboardKeyPressedEventInternal(
                viwid.event.keyboard.KeyCodes.ESC, False, False, False))

        return event_internals

    MOUSE_NORMAL_BUTTONS = (0, 1, 2)
    MOUSE_SCROLL_DOWN_BUTTON = 3
    MOUSE_SCROLL_UP_BUTTON = 4

    def __process_input__mouse_buttons(self, curses_mouse_event):
        return (bool(curses_mouse_event[4] & curses.BUTTON_SHIFT),
                bool(curses_mouse_event[4] & curses.BUTTON_ALT),
                bool(curses_mouse_event[4] & curses.BUTTON_CTRL),
                (bool(curses_mouse_event[4] & curses.BUTTON1_PRESSED),
                 bool(curses_mouse_event[4] & curses.BUTTON2_PRESSED),
                 bool(curses_mouse_event[4] & curses.BUTTON3_PRESSED),
                 bool(curses_mouse_event[4] & curses.BUTTON4_PRESSED),
                 bool(curses_mouse_event[4] & curses.BUTTON5_PRESSED)),
                (bool(curses_mouse_event[4] & curses.BUTTON1_RELEASED),
                 bool(curses_mouse_event[4] & curses.BUTTON2_RELEASED),
                 bool(curses_mouse_event[4] & curses.BUTTON3_RELEASED),
                 bool(curses_mouse_event[4] & curses.BUTTON4_RELEASED),
                 bool(curses_mouse_event[4] & curses.BUTTON5_RELEASED)),
                (bool(curses_mouse_event[4] & curses.BUTTON1_CLICKED),
                 bool(curses_mouse_event[4] & curses.BUTTON2_CLICKED),
                 bool(curses_mouse_event[4] & curses.BUTTON3_CLICKED),
                 bool(curses_mouse_event[4] & curses.BUTTON4_CLICKED),
                 bool(curses_mouse_event[4] & curses.BUTTON5_CLICKED)))

    def __process_input__keyboard_key_combination(self, key: int) -> tuple[tuple[int, ...]|None, bool, bool, bool]:
        key_code, with_shift, with_ctrl = None, False, False
        with_alt = self.__next_keyboard_key_is_with_alt_or_last_was_esc
        self.__next_keyboard_key_is_with_alt_or_last_was_esc = False

        match key:
            case 27:
                self.__next_keyboard_key_is_with_alt_or_last_was_esc = True
            case curses.KEY_UP:
                key_code = viwid.event.keyboard.KeyCodes.ARROW_UP
            case curses.KEY_RIGHT:
                key_code = viwid.event.keyboard.KeyCodes.ARROW_RIGHT
            case curses.KEY_DOWN:
                key_code = viwid.event.keyboard.KeyCodes.ARROW_DOWN
            case curses.KEY_LEFT:
                key_code = viwid.event.keyboard.KeyCodes.ARROW_LEFT
            case curses.KEY_BACKSPACE:
                key_code = viwid.event.keyboard.KeyCodes.BACKSPACE
            case curses.KEY_HOME:
                key_code = viwid.event.keyboard.KeyCodes.HOME
            case curses.KEY_END:
                key_code = viwid.event.keyboard.KeyCodes.END
            case curses.KEY_DC:
                key_code = viwid.event.keyboard.KeyCodes.DEL
            case curses.KEY_IC:
                key_code = viwid.event.keyboard.KeyCodes.INS
            case curses.KEY_F1:
                key_code = viwid.event.keyboard.KeyCodes.F1
            case curses.KEY_F2:
                key_code = viwid.event.keyboard.KeyCodes.F2
            case curses.KEY_F3:
                key_code = viwid.event.keyboard.KeyCodes.F3
            case curses.KEY_F4:
                key_code = viwid.event.keyboard.KeyCodes.F4
            case curses.KEY_F5:
                key_code = viwid.event.keyboard.KeyCodes.F5
            case curses.KEY_F6:
                key_code = viwid.event.keyboard.KeyCodes.F6
            case curses.KEY_F7:
                key_code = viwid.event.keyboard.KeyCodes.F7
            case curses.KEY_F8:
                key_code = viwid.event.keyboard.KeyCodes.F8
            case curses.KEY_F9:
                key_code = viwid.event.keyboard.KeyCodes.F9
            case curses.KEY_F10:
                key_code = viwid.event.keyboard.KeyCodes.F10
            case curses.KEY_F11:
                key_code = viwid.event.keyboard.KeyCodes.F11
            case curses.KEY_F12:
                key_code = viwid.event.keyboard.KeyCodes.F12
            case curses.KEY_PRINT:
                key_code = viwid.event.keyboard.KeyCodes.PRINT
            case curses.KEY_PPAGE:
                key_code = viwid.event.keyboard.KeyCodes.PAGE_UP
            case curses.KEY_NPAGE:
                key_code = viwid.event.keyboard.KeyCodes.PAGE_DOWN
            case curses.KEY_BTAB:
                key_code, with_shift = viwid.event.keyboard.KeyCodes.TAB, True
            case 575:
                key_code, with_ctrl = viwid.event.keyboard.KeyCodes.ARROW_UP, True
            case 569:
                key_code, with_ctrl = viwid.event.keyboard.KeyCodes.ARROW_RIGHT, True
            case 554:
                key_code, with_ctrl = viwid.event.keyboard.KeyCodes.ARROW_LEFT, True
            case _:
                if 1 <= key <= 26 and key not in (9, 10):
                    key += 96
                    with_ctrl = True
                key_code = (key,)

        return key_code, with_shift, with_alt, with_ctrl
