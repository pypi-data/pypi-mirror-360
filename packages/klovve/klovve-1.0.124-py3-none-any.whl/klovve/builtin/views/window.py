#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
See :py:class:`Window`.
"""
import klovve


class Window(klovve.ui.Piece):
    """
    A window.

    This is a root view that - directly or indirectly - contains all views e.g. of your application main window.

    See also :py:attr:`klovve.app.BaseApplication.windows`.
    """

    #: The window title.
    title: str = klovve.ui.property(initial="")

    #: The window body.
    body: klovve.ui.View | None = klovve.ui.property()

    horizontal_layout = klovve.ui.property(initial=klovve.ui.Layout(klovve.ui.Align.CENTER))
    vertical_layout = klovve.ui.property(initial=klovve.ui.Layout(klovve.ui.Align.CENTER))

    def request_close(self):
        """
        Trigger a close request, and if event processing was not stopped, close the window.
        """
        closed_requested_event = Window.CloseRequestedEvent(self)
        self.trigger_event(closed_requested_event)
        if not closed_requested_event.processing_stopped:
            self.close()

    def close(self):
        """
        Instantly close this window.

        This is usually not used directly. See :py:meth:`request_close`.
        """
        self._introspect.set_property_value(Window._is_closed, True)

    _is_closed = klovve.ui.property(initial=False, is_settable=False)

    class CloseRequestedEvent(klovve.event.Event):
        """
        Event that occurs when a window was requested to be closed.
        """

        def __init__(self, window: "Window"):
            super().__init__()
            self.__window = window

        @property
        def window(self) -> "Window":
            """
            The window.
            """
            return self.__window
