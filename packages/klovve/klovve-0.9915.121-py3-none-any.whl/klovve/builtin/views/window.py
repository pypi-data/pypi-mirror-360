#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import klovve


class Window(klovve.ui.Piece):

    title: str = klovve.ui.property(initial="")

    body: klovve.ui.View | None = klovve.ui.property()

    horizontal_layout = klovve.ui.property(initial=klovve.ui.Layout(klovve.ui.Align.CENTER))
    vertical_layout = klovve.ui.property(initial=klovve.ui.Layout(klovve.ui.Align.CENTER))

    def request_close(self):
        closed_requested_event = Window.CloseRequestedEvent(self)
        self.trigger_event(closed_requested_event)
        if not closed_requested_event.processing_stopped:
            self.close()

    def close(self):
        self._introspect.set_property_value(Window._is_closed, True)

    _is_closed = klovve.ui.property(initial=False, is_settable=False)

    class CloseRequestedEvent(klovve.event.Event):

        def __init__(self, window: "Window"):
            super().__init__()
            self.__window = window

        @property
        def window(self) -> "Window":
            return self.__window
