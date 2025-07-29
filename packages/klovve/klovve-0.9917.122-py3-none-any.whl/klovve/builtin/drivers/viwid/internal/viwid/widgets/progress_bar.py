#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
See :py:class:`ProgressBar`.
"""
import viwid.widgets.widget
from viwid.widgets.label import Label as _Label


class ProgressBar(_Label):
    """
    A horizontal progress bar.
    """

    def __init__(self, **kwargs):
        super().__init__(**{**dict(class_style_name="progress_not_done",
                                   horizontal_alignment=viwid.Alignment.FILL,
                                   vertical_alignment=viwid.Alignment.FILL), **kwargs})

    value: float
    @_Label.Property(default=lambda: 0)
    def value(self, _):
        """
        The progress value. Between `0` and `1`. `0` by default.
        """
        self._request_repaint()

    def _compute_width(self, minimal):
        return 1 if minimal else 10

    def _compute_height(self, width, minimal):
        return 1

    def _paint(self, canvas):
        canvas.fill(self._style(self.layer_style.progress_done),
                    rectangle=viwid.Rectangle(viwid.Point(0, 0),
                                              viwid.Point(int(self.value * self.size.width), self.size.height)))
