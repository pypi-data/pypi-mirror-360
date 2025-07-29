#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
See :py:class:`Label`.
"""
import enum

import viwid.canvas
import viwid.data.color
import viwid.widgets
import viwid.text
from viwid.widgets.widget import Widget as _Widget


class Label(_Widget):
    """
    A text label.

    It shows arbitrary text (by default with automatic line wrapping).
    """

    def __init__(self, **kwargs):
        super().__init__(**{**dict(horizontal_alignment=viwid.Alignment.CENTER,
                                   vertical_alignment=viwid.Alignment.CENTER), **kwargs})
        self.__measure_input_text = None

    text: str
    @_Widget.Property(default=lambda: "")
    def text(self, _):
        """
        The text to show. Empty string by default.

        Can be an arbitrary printable string.
        """
        self.__measure_input_text = self._text_measuring.text(_)
        self._request_resize_and_repaint()

    foreground: viwid.data.color.TColorInput|None
    @_Widget.Property
    def foreground(self, _):
        """
        The foreground color. `None` by default.

        There are only rare occasions where this should be set.
        """
        self._request_repaint()

    background: viwid.data.color.TColorInput|None
    @_Widget.Property
    def background(self, _):
        """
        The background color. `None` by default.

        There are only rare occasions where this should be set.
        """
        self._request_repaint()

    overflow_mode: "OverflowMode"
    @_Widget.Property(default=lambda: OverflowMode.WRAP_TEXT)
    def overflow_mode(self, _):
        """
        The overflow mode. :py:attr:`OverflowMode.WRAP_TEXT` by default.

        It defines how the label should behave when the text is larger in width than the label itself.

        In general, the label will never be smaller than the text needs to be fully shown, no matter what overflow mode
        is chosen. There are explicitly documented exceptions, though; see e.g. :py:attr:`OverflowMode.ELLIPSIS_END`.

        Note: This will never change :py:attr:`text` but only its visualization.
        """
        self._request_resize_and_repaint()

    def _compute_width(self, minimal) -> int:
        if minimal:
            return 1
        return self._text_measuring.text_width(self.__measure_input_text)

    def _compute_height(self, width: int, minimal) -> int:
        return len(self.__text(width))

    def _paint(self, canvas):
        canvas.fill(viwid.canvas.BlockAttributes.get(
            foreground_color=self.application_manager.driver.plain_color(self.foreground or self._style().foreground),
            background_color=self.application_manager.driver.plain_color(self.background or self._style().background)))
        canvas.draw_text(self.__text(self.size.width))

    def __text(self, width: int):
        if self.overflow_mode == OverflowMode.WRAP_TEXT:
            return self.__measure_input_text.render(width=width)
        elif self.overflow_mode == OverflowMode.ELLIPSIS_END:
            return self.__measure_input_text.render_trimmed_to_width(width)
        else:
            raise RuntimeError(f"invalid overflow_mode {self.overflow_mode!r}")


class OverflowMode(enum.Enum):
    """
    A label's overflow mode.
    """

    #: Do not allow the label to become smaller that its text needs to show (without any word wrapping).
    STRICT = enum.auto()

    #: Automatically wrap text; at word boundaries whenever possible.
    WRAP_TEXT = enum.auto()

    #: Truncate the overflow and show a "..." and the end of lines that were too long.
    ELLIPSIS_END = enum.auto()
