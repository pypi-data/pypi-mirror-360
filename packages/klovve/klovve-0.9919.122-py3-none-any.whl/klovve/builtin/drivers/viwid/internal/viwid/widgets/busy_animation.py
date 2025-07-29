#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
See :py:class:`BusyAnimation`.
"""
from viwid.widgets.widget import Widget as _Widget


class BusyAnimation(_Widget):
    """
    A busy animation.
    """

    def __init__(self, **kwargs):
        super().__init__(**{**dict(), **kwargs})
        self.__i = -1
        self.__chars = None
        self.__animation_running = False

    def _materialize(self):
        super()._materialize()

        self.__chars = [[[self._text_measuring.grapheme(_)]] for _ in r"\|/-"]
        self.__start_animation()

    def __start_animation(self):
        if self.__animation_running:
            return

        self.__animation_running = True
        self.__next()

    def __next(self):
        self.__i = (self.__i + 1) % len(self.__chars)
        self._request_repaint()

        if self.is_materialized:
            self.application_manager.driver.event_loop.call_later(0.5, self.__next)
        else:
            self.__animation_running = False

    def _compute_width(self, minimal) -> int:
        return 1

    def _compute_height(self, width: int, minimal) -> int:
        return 1

    def _paint(self, canvas):
        canvas.draw_text(self.__chars[self.__i])
