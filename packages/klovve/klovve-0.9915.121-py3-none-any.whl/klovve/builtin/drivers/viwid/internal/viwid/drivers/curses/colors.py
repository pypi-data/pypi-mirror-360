#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import curses
import enum
import sys

import viwid.canvas
import viwid.data.color


class CursesColors:

    curses_colors = [curses.COLOR_BLACK, curses.COLOR_BLUE, curses.COLOR_GREEN, curses.COLOR_CYAN,
                     curses.COLOR_RED, curses.COLOR_MAGENTA, curses.COLOR_YELLOW, curses.COLOR_WHITE]

    class Mode(enum.Enum):
        COLORS_8 = enum.auto()
        COLORS_256 = enum.auto()

    def __init__(self, driver):
        self.__driver = driver
        self.__mode = self.__color_mode()
        self.__curses_colors = {}
        self.__curses_color_pairs = {}
        self.__next_color_pair_number = 1

    @property
    def color_mode(self) -> Mode:
        return self.__mode

    def __color_mode(self):
        if curses.COLORS >= 256:
            try:
                curses.init_color(16, 0, 0, 0)
                return CursesColors.Mode.COLORS_256
            except curses.error:
                pass
        return CursesColors.Mode.COLORS_8

    def __curses_color(self, color: viwid.PlainColor):
        if self.__mode == CursesColors.Mode.COLORS_256:
            color_tuple = (int(color.r * 1000), int(color.g * 1000), int(color.b * 1000))
            result = self.__curses_colors.get(color_tuple)
            if result is None:
                color_number = _256colors_space.color_to_index(color.r * 255, color.g * 255, color.b * 255)
                curses.init_color(color_number, *color_tuple)
                result = self.__curses_colors[color_tuple] = color_number
        else:
            return CursesColors.curses_colors[(1 if color.b >= 0.5 else 0) + (2 if color.g >= 0.5 else 0)
                                               + (4 if color.r >= 0.5 else 0)]
        return result

    def color_pair(self, fg: viwid.data.color.TColorInput, bg: viwid.data.color.TColorInput):
        fg_color_number = self.__curses_color(self.__driver.plain_color(fg))
        bg_color_number = self.__curses_color(self.__driver.plain_color(bg))
        pair_tuple = fg_color_number, bg_color_number
        result = self.__curses_color_pairs.get(pair_tuple)
        if result is None:
            curses.init_pair(self.__next_color_pair_number, *pair_tuple)
            result = self.__curses_color_pairs[pair_tuple] = self.__next_color_pair_number
            self.__next_color_pair_number += 1
        return result


class _XTerm256TerminalColorSpace:  # stolen from hallyd

    def __color_to_index__colors(self, r, g, b):
        return (self._COLOR_INDEX_BEGIN
                + self.__color_to_index__colors__component(r) * (self._COLOR_SYMBOLS_PER_CHANNEL ** 2)
                + self.__color_to_index__colors__component(g) * self._COLOR_SYMBOLS_PER_CHANNEL
                + self.__color_to_index__colors__component(b))

    def __color_to_index__colors__component(self, v):
        if v < self._COLOR_VALUE_BEGIN - self._COLOR_VALUE_STEP / 2:
            return 0
        return self.__color_to_index__helper__channel(v, self._COLOR_SYMBOLS_PER_CHANNEL - 1,
                                                      self._COLOR_VALUE_BEGIN, self._COLOR_VALUE_STEP) + 1

    def __color_to_index__grayscale(self, r, g, b):
        return self.__color_to_index__helper__channel((r + g + b) / 3, self._GRAYSCALE_SYMBOLS_PER_CHANNEL,
                                                      self._GRAYSCALE_VALUE_BEGIN, self._GRAYSCALE_VALUE_STEP
                                                      ) + self._GRAYSCALE_INDEX_BEGIN

    def __color_to_index__helper__channel(self, val, symbol_count, value_begin, value_step):
        return min(max(0, int((val - value_begin + value_step / 2) / value_step)), symbol_count - 1)

    def __cost(self, c1, c2):
        return sum([d**2 for d in [v1-v2 for v1, v2 in zip(c1, c2)]])

    def color_to_index(self, r, g, b):
        index_colors = self.__color_to_index__colors(r, g, b)
        index_grayscale = self.__color_to_index__grayscale(r, g, b)

        return index_colors if (self.__cost(self.index_to_color(index_colors), (r, g, b))
                                < self.__cost(self.index_to_color(index_grayscale), (r, g, b))) else index_grayscale

    def index_to_color(self, idx):

        def color_value(ii, channel, symbols_per_channel, value_begin, value_step):
            val = (ii // symbols_per_channel ** channel) % symbols_per_channel
            return 0 if (val == 0) else ((val - 1) * value_step + value_begin)

        i = idx - self._GRAYSCALE_INDEX_BEGIN

        if i >= 0:

            col_val = color_value(i+1, 0, sys.maxsize, self._GRAYSCALE_VALUE_BEGIN, self._GRAYSCALE_VALUE_STEP)
            return col_val, col_val, col_val

        else:
            i = idx - self._COLOR_INDEX_BEGIN

        if i >= 0:

            return (color_value(i, 2, self._COLOR_SYMBOLS_PER_CHANNEL, self._COLOR_VALUE_BEGIN, self._COLOR_VALUE_STEP),
                    color_value(i, 1, self._COLOR_SYMBOLS_PER_CHANNEL, self._COLOR_VALUE_BEGIN, self._COLOR_VALUE_STEP),
                    color_value(i, 0, self._COLOR_SYMBOLS_PER_CHANNEL, self._COLOR_VALUE_BEGIN, self._COLOR_VALUE_STEP))

        return 0

    _COLOR_INDEX_BEGIN = 16
    _COLOR_VALUE_BEGIN = 95
    _COLOR_VALUE_STEP = 40
    _COLOR_VALUE_END = 255
    _GRAYSCALE_INDEX_BEGIN = 232
    _GRAYSCALE_VALUE_BEGIN = 8
    _GRAYSCALE_VALUE_STEP = 10
    _GRAYSCALE_VALUE_END = 238
    _END_INDEX_BEGIN = 256
    _COLOR_SYMBOLS_PER_CHANNEL = int((_COLOR_VALUE_END - _COLOR_VALUE_BEGIN) / _COLOR_VALUE_STEP) + 1 + 1
    _GRAYSCALE_SYMBOLS_PER_CHANNEL = int((_GRAYSCALE_VALUE_END - _GRAYSCALE_VALUE_BEGIN) / _GRAYSCALE_VALUE_STEP) + 1

_256colors_space = _XTerm256TerminalColorSpace()
