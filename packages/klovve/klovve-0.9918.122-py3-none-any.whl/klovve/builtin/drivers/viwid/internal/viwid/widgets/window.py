#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
See :py:class:`Window`.
"""
import viwid.event
import viwid.layout
import viwid.app.screen
import viwid.widgets
from viwid.widgets.widget import Widget as _Widget


class Window(_Widget):
    """
    An application window with a title bar and a body below it.

    It can be configured to be closable by user. If so, a request to do that will trigger
    :py:class:`Window.RequestCloseEvent`. By default, this will eventually close the window.
    """

    def __init__(self, **kwargs):
        super().__init__(**{**dict(class_style_name="window",
                                   horizontal_alignment=viwid.Alignment.CENTER,
                                   vertical_alignment=viwid.Alignment.CENTER,
                                   layout=viwid.layout.GridLayout(viwid.layout.GridLayout.VERTICAL_PARTITIONER)),
                            **kwargs})
        self.__move_mouse_grabber = None
        self.__move_mouse_last_position = None
        self.__title_label = viwid.widgets.label.Label(horizontal_alignment=viwid.Alignment.FILL_EXPANDING,
                                                       overflow_mode=viwid.widgets.label.OverflowMode.ELLIPSIS_END)
        self.__resizer_label = viwid.widgets.label.Label(text="*", class_style_name="tiny_control",
                                                         margin=viwid.Margin(left=1), is_hoverable=True,
                                                         horizontal_alignment=viwid.Alignment.END)
        self.__closer_label = viwid.widgets.label.Label(text="x", class_style_name="tiny_control",
                                                        margin=viwid.Margin(left=1), is_hoverable=True,
                                                        horizontal_alignment=viwid.Alignment.END)
        self.__title_bar = viwid.widgets.box.Box(
            children=[self.__title_label, self.__resizer_label, self.__closer_label],
            class_style_name="window_title",
            vertical_alignment=viwid.Alignment.START,
            orientation=viwid.Orientation.HORIZONTAL)
        self._children = [self.__title_bar, viwid.widgets.label.Label()]

    body: "viwid.widgets.widget.Widget|None"
    @_Widget.Property()
    def body(self, _):
        """
        The window body widget. `None` by default.
        """
        self._children[1] = _ or viwid.widgets.label.Label()

    title: str
    @_Widget.Property(default=lambda: "")
    def title(self, _):
        """
        The window title. Empty string by default.
        """
        self.__title_label.text = " " + _

    is_resizable_by_user: bool
    @_Widget.Property(default=lambda: True)
    def is_resizable_by_user(self, _):
        """
        Whether this window is resizable by user. `True` by default.
        """
        self.__resizer_label.is_visible = _

    is_closable_by_user: bool
    @_Widget.Property(default=lambda: True)
    def is_closable_by_user(self, _):
        """
        Whether this window is closable by user. `True` by default.
        """
        self.__closer_label.is_visible = _

    is_movable_by_user: bool
    @_Widget.Property(default=lambda: True)
    def is_movable_by_user(self, _):
        """
        Whether this window is movable by user. `True` by default.
        """

    def request_close(self):
        self.screen_layer.trigger_event(self, Window.RequestCloseEvent())

    def _materialize(self):
        super()._materialize()

        self.__title_bar.listen_event(viwid.event.mouse.ButtonDownEvent, self.__handle_title_bar_mouse_button_down,
                                implements_default_behavior=True)
        self.__title_bar.listen_event(viwid.event.mouse.ButtonUpEvent, self.__handle_title_bar_mouse_button_up,
                                implements_default_behavior=True)
        self.__title_bar.listen_event(viwid.event.mouse.MoveEvent, self.__handle_title_bar_mouse_moved,
                                implements_default_behavior=True)
        self.__resizer_label.listen_event(viwid.event.mouse.ButtonDownEvent, self.__handle_resizer_mouse_button_down,
                                    implements_default_behavior=True)
        self.__resizer_label.listen_event(viwid.event.mouse.ButtonUpEvent, self.__handle_resizer_mouse_button_up,
                                    implements_default_behavior=True)
        self.__resizer_label.listen_event(viwid.event.mouse.MoveEvent, self.__handle_resizer_mouse_moved,
                                    implements_default_behavior=True)
        self.__closer_label.listen_event(viwid.event.mouse.ButtonDownEvent, self.__handle_closer_mouse_button_down,
                                    implements_default_behavior=True)
        self.__closer_label.listen_event(viwid.event.mouse.ButtonUpEvent, self.__handle_closer_mouse_button_up,
                                    implements_default_behavior=True)
        self.listen_event(Window.RequestCloseEvent, self.__handle_request_close, implements_default_behavior=True)

    def _dematerialize(self):
        self.__title_bar.unlisten_event(self.__handle_title_bar_mouse_button_down)
        self.__title_bar.unlisten_event(self.__handle_title_bar_mouse_button_up)
        self.__title_bar.unlisten_event(self.__handle_title_bar_mouse_moved)
        self.__resizer_label.unlisten_event(self.__handle_resizer_mouse_button_down)
        self.__resizer_label.unlisten_event(self.__handle_resizer_mouse_button_up)
        self.__resizer_label.unlisten_event(self.__handle_resizer_mouse_moved)
        self.__closer_label.unlisten_event(self.__handle_closer_mouse_button_down)
        self.__closer_label.unlisten_event(self.__handle_closer_mouse_button_up)
        self.unlisten_event(self.__handle_request_close)

        super()._dematerialize()

    def __handle_title_bar_mouse_button_down(self, event):
        self.screen_layer.application.set_layer_index(self.screen_layer, None)

        if not self.is_movable_by_user:
            return

        self.__move_mouse_last_position = event.screen_position
        self.__move_mouse_grabber = event.grab_mouse(self.__title_bar)
        self.__move_mouse_grabber.__enter__()

    def __handle_title_bar_mouse_button_up(self, event):
        if self.__move_mouse_grabber:
            self.__move_mouse_grabber.__exit__(None, None, None)
            self.__move_mouse_grabber = None

    def __handle_title_bar_mouse_moved(self, event):
        if self.__move_mouse_grabber:
            diff_x = event.screen_position.x - self.__move_mouse_last_position.x
            diff_y = event.screen_position.y - self.__move_mouse_last_position.y
            position, size = viwid.app.screen.Layout.unshrunk_widget_alignment(
                self, viwid.Point(self.position.x + diff_x, self.position.y + diff_y), self.size, self.parent.size)
            self.align(position=position, size=size)
            self.__move_mouse_last_position = event.screen_position

    def __handle_resizer_mouse_button_down(self, event):
        event.stop_handling()
        self.__move_mouse_last_position = event.screen_position
        self.__move_mouse_grabber = event.grab_mouse(self.__resizer_label)
        self.__move_mouse_grabber.__enter__()

    def __handle_resizer_mouse_button_up(self, event):
        if self.__move_mouse_grabber:
            self.__move_mouse_grabber.__exit__(None, None, None)
            self.__move_mouse_grabber = None

    def __handle_resizer_mouse_moved(self, event):
        if self.__move_mouse_grabber:
            diff_x = event.screen_position.x - self.__move_mouse_last_position.x
            diff_y = event.screen_position.y - self.__move_mouse_last_position.y
            self.__resize_by(diff_x, -diff_y)
            self.__move_mouse_last_position = event.screen_position

    def __handle_closer_mouse_button_down(self, event):
        event.stop_handling()

    def __handle_closer_mouse_button_up(self, event):
        if self.is_closable_by_user:
            self.request_close()

    def __handle_request_close(self, event):
        if self.is_materialized:
            self.screen_layer.application.remove_layer(self.screen_layer)
        event.stop_handling()

    def __resize_by(self, diff_x, diff_y):
        position, size = viwid.app.screen.Layout.unshrunk_widget_alignment(
            self, viwid.Point(self.position.x, self.position.y - diff_y),
            viwid.Size(self.size.width + diff_x, self.size.height + diff_y), self.parent.size)
        self.align(position=position, size=size)

    class RequestCloseEvent(viwid.event.Event):
        """
        Event that occurs when the user requests to close a window.
        """
