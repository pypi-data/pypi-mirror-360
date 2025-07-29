#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
See :py:class:`Frame`.
"""
import viwid.layout
from viwid.widgets.widget import Widget as _Widget


class Frame(_Widget):
    """
    A frame. It surrounds an arbitrary widget with a visual frame with width 1.

    It has no functionality beyond the visual encapsulation it gives.
    """

    def __init__(self, **kwargs):
        self.__body_box = viwid.widgets.box.Box(margin=viwid.Margin(all=1))
        super().__init__(**{**dict(layout=viwid.layout.GridLayout(viwid.layout.GridLayout.HORIZONTAL_PARTITIONER),
                                   _children=(self.__body_box,), class_style_name="frame"),
                            **kwargs})
        self.__frame_graphemes = None

    body: "viwid.widgets.widget.Widget|None"
    @_Widget.Property()
    def body(self, v):
        """
        The widget inside the frame. `None` by default.
        """
        self.__body_box.children = (v,) if v else ()

    def _materialize(self):
        super()._materialize()

        self.__frame_graphemes = [self._text_measuring.text(_) for _ in "▀▜▐▟▄▙▌▛"]

    def _paint(self, canvas):
        one_size = viwid.Size(1, 1)
        grapheme_n, grapheme_ne, grapheme_e, grapheme_se, grapheme_s, grapheme_sw, grapheme_w, grapheme_nw = self.__frame_graphemes
        canvas.draw_text(grapheme_nw, rectangle=viwid.Rectangle(viwid.Point(0, 0), one_size))
        canvas.draw_text(grapheme_ne, rectangle=viwid.Rectangle(viwid.Point(self.size.width-1, 0), one_size))
        canvas.draw_text(grapheme_sw, rectangle=viwid.Rectangle(viwid.Point(0, self.size.height-1), one_size))
        canvas.draw_text(grapheme_se, rectangle=viwid.Rectangle(viwid.Point(self.size.width-1, self.size.height-1), one_size))
        for x in range(1, self.size.width-1):
            canvas.draw_text(grapheme_n, rectangle=viwid.Rectangle(viwid.Point(x, 0), one_size))
            canvas.draw_text(grapheme_s, rectangle=viwid.Rectangle(viwid.Point(x, self.size.height-1), one_size))
        for y in range(1, self.size.height-1):
            canvas.draw_text(grapheme_e, rectangle=viwid.Rectangle(viwid.Point(self.size.width-1, y), one_size))
            canvas.draw_text(grapheme_w, rectangle=viwid.Rectangle(viwid.Point(0, y), one_size))
