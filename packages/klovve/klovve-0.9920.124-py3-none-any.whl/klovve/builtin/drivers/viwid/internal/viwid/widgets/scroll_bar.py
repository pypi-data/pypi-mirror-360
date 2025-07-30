#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
See :py:class:`ScrollBar`.
"""
import abc
import typing as t

import viwid.event
import viwid.layout
import viwid.app.screen
import viwid.widgets
from viwid.widgets.widget import Widget as _Widget


class ScrollBar(_Widget):
    """
    A scroll bar.

    It does not automatically scroll something but is similar to a :py:class:`viwid.widgets.slider.Slider`. Its name
    just follows common terminology. For actual scrolling behavior, see :py:class:`viwid.widgets.scrollable.Scrollable`.
    """

    def __init__(self, **kwargs):
        self.__button_decrease = viwid.widgets.button.Button(decoration=viwid.widgets.button.Decoration.NONE,
                                                             is_focusable=False)
        self.__button_handle = viwid.widgets.button.Button(decoration=viwid.widgets.button.Decoration.NONE,
                                                           class_style_name="scroll_bar_handle", is_focusable=False)
        self.__button_increase = viwid.widgets.button.Button(decoration=viwid.widgets.button.Decoration.NONE,
                                                             is_focusable=False)

        super().__init__(**{**dict(_children=(self.__button_decrease,
                                              self.__button_handle,
                                              self.__button_increase),
                                   class_style_name="scroll_bar", is_focusable=True,
                                   layout=ScrollBar._Layout(self)), **kwargs})
        self._orientation_handler = None

        self.__move_mouse_grabber = None

    orientation: viwid.Orientation
    @_Widget.Property(default=lambda: viwid.Orientation.HORIZONTAL)
    def orientation(self, _):
        """
        The orientation. :py:attr:`viwid.Orientation.HORIZONTAL` by default.
        """
        self._orientation_handler = (ScrollBar._HorizontalOrientation
                                     if self.orientation == viwid.Orientation.HORIZONTAL
                                     else ScrollBar._VerticalOrientation)(self)
        self._orientation_handler.refresh_button_texts(self.__button_decrease, self.__button_increase)
        self._request_resize_and_repaint()

    value_range: viwid.NumericValueRange
    @_Widget.Property(default=lambda: viwid.NumericValueRange.ZERO_TO_HUNDRED_BY_ONE)
    def value_range(self, _):
        """
        The range of allowed values. :py:attr:`viwid.NumericValueRange.ZERO_TO_HUNDRED_BY_ONE` by default.
        """
        self.__correct_value()
        self._request_resize_and_repaint()

    value: float
    @_Widget.Property(default=lambda: 0)
    def value(self, _):
        """
        The current value. `0` by default (or the nearest value in the allowed range).
        """
        self.__correct_value()
        self._request_resize_and_repaint()

    handle_size_fraction: float
    @_Widget.Property(default=lambda: 0.1)
    def handle_size_fraction(self, _):
        """
        The fraction of the full scroll bar length to be taken for the handle. Between `0` and `1`. `0.1` by default.
        """
        if _ != (correct_handle_size_fraction := min(max(0.0, _), 1.0)):
            self.handle_size_fraction = correct_handle_size_fraction
        self._request_resize_and_repaint()

    def _materialize(self):
        super()._materialize()

        self.listen_event(viwid.event.mouse.ClickEvent, self.__handle_mouse_clicked,
                          implements_default_behavior=True)
        self.listen_event(viwid.event.keyboard.KeyPressEvent, self.__handle_keyboard_key_pressed,
                          implements_default_behavior=True)
        self.__button_handle.listen_event(viwid.event.mouse.ButtonDownEvent, self.__handle_handle_mouse_button_down,
                                          implements_default_behavior=True)
        self.__button_handle.listen_event(viwid.event.mouse.ButtonUpEvent, self.__handle_handle_mouse_button_up,
                                          implements_default_behavior=True)
        self.__button_handle.listen_event(viwid.event.mouse.MoveEvent, self.__handle_handle_mouse_moved,
                                          implements_default_behavior=True)

    def _dematerialize(self):
        self.unlisten_event(self.__handle_mouse_clicked)
        self.unlisten_event(self.__handle_keyboard_key_pressed)
        self.__button_handle.unlisten_event(self.__handle_handle_mouse_button_down)
        self.__button_handle.unlisten_event(self.__handle_handle_mouse_button_up)
        self.__button_handle.unlisten_event(self.__handle_handle_mouse_moved)

        super()._dematerialize()

    def _compute_width(self, minimal) -> int:
        if self.orientation == viwid.Orientation.VERTICAL:
            return 1
        return 2 if minimal else 5

    def _compute_height(self, width: int, minimal) -> int:
        if self.orientation == viwid.Orientation.HORIZONTAL:
            return 1
        return 2 if minimal else 5

    def __correct_value(self):
        valid_value = self.value_range.valid_value(self.value)
        if self.value != valid_value:
            self.value = valid_value

    def __handle_mouse_clicked(self, event: viwid.event.mouse.ClickEvent) -> None:
        self._orientation_handler.handle_mouse_clicked(event)

    def __handle_keyboard_key_pressed(self, event: viwid.event.keyboard.KeyPressEvent) -> None:
        self._orientation_handler.handle_keyboard_key_pressed(event)

    def __handle_handle_mouse_button_down(self, event: viwid.event.mouse.ButtonDownEvent) -> None:
        self.__move_mouse_grabber = event.grab_mouse(self.__button_handle)
        self.__move_mouse_grabber.__enter__()

    def __handle_handle_mouse_button_up(self, event: viwid.event.mouse.ButtonUpEvent) -> None:
        if self.__move_mouse_grabber:
            self.__move_mouse_grabber.__exit__(None, None, None)
            self.__move_mouse_grabber = None

    def __handle_handle_mouse_moved(self, event: viwid.event.mouse.MoveEvent) -> None:
        if self.__move_mouse_grabber:
            self._orientation_handler.handle_handle_moved(event)

    class _Orientation(abc.ABC):

        def __init__(self, scroll_bar: "ScrollBar"):
            self._scroll_bar = scroll_bar
            self.__label_text_inc = None
            self.__label_text_dec = None

        def apply_layout(self, widgets: t.Sequence["viwid.widgets.widget.Widget"],
                         forcefully_apply_resizing_for: t.Sequence["viwid.widgets.widget.Widget"]) -> None:
            scroll_bar_length = self._scroll_bar_length()
            button_1_rect, button_2_rect = self._button_rectangles()
            handle_size = max(1, int(self._scroll_bar.handle_size_fraction * (scroll_bar_length - 2)))

            handle_start = self._scroll_bar.value_range.value_to_alien_scale(
                self._scroll_bar.value, alien_max_value=scroll_bar_length-2-handle_size)
            handle_rect = self._handle_rectangle(handle_start, handle_size)

            button_decrease, button_handle, button_increase = widgets
            button_decrease.align(button_1_rect.top_left, button_1_rect.size,
                                  forcefully_apply_resizing_for=forcefully_apply_resizing_for)
            button_handle.align(handle_rect.top_left, handle_rect.size,
                                  forcefully_apply_resizing_for=forcefully_apply_resizing_for)
            button_increase.align(button_2_rect.top_left, button_2_rect.size,
                                  forcefully_apply_resizing_for=forcefully_apply_resizing_for)

        def refresh_button_texts(self, button_decrease, button_increase):
            button_decrease.text, button_increase.text = self._button_label_texts()

        def handle_handle_moved(self, event: viwid.event.mouse.MoveEvent) -> None:
            self.__scroll_to_position(event.screen_position, handle_buttons=False)

        def handle_mouse_clicked(self, event: viwid.event.mouse.ClickEvent) -> None:
            if event.subject_button != event.BUTTON_LEFT:
                return
            self.__scroll_to_position(event.screen_position, handle_buttons=True)
            self._scroll_bar._request_resize_and_repaint()
            self._scroll_bar.try_focus()  # TODO odd that we have to
            event.stop_handling()

        def handle_keyboard_key_pressed(self, event: viwid.event.keyboard.KeyPressEvent) -> None:
            if direction := self._scroll(*{
                viwid.event.keyboard.KeyCodes.ARROW_UP: (0, -1),
                viwid.event.keyboard.KeyCodes.ARROW_RIGHT: (1, 0),
                viwid.event.keyboard.KeyCodes.ARROW_DOWN: (0, 1),
                viwid.event.keyboard.KeyCodes.ARROW_LEFT: (-1, 0),
            }.get(event.code, (0, 0))):
                self._scroll_bar.value = self._scroll_bar.value_range.step_number_to_value(
                    self._scroll_bar.value_range.value_to_step_number(self._scroll_bar.value) + direction)
                event.stop_handling()

        @abc.abstractmethod
        def _scroll(self, horizontal: int, vertical: int) -> int:
            pass

        @abc.abstractmethod
        def _scroll_bar_length(self) -> int:
            pass

        @abc.abstractmethod
        def _button_rectangles(self) -> tuple[viwid.Rectangle, viwid.Rectangle]:
            pass

        @abc.abstractmethod
        def _handle_rectangle(self, handle_start: int, handle_size: int) -> viwid.Rectangle:
            pass

        @abc.abstractmethod
        def _button_label_texts(self) -> tuple[str, str]:
            pass

        def __scroll_to_position(self, screen_position: viwid.Point, *, handle_buttons: bool) -> None:
            point = viwid.app.screen.translate_coordinates_from_root(screen_position, new_origin=self._scroll_bar)
            point_value = self._scroll(point.x, point.y)
            scroll_bar_length = self._scroll_bar_length()
            if handle_buttons and point_value == 0:
                self._scroll_bar.value -= 2
            elif handle_buttons and point_value == scroll_bar_length - 1:
                self._scroll_bar.value += 2
            else:
                handle_size = max(1, int(self._scroll_bar.handle_size_fraction * (scroll_bar_length - 2)))
                non_handle_size = max(0, scroll_bar_length - 2 - handle_size)
                self._scroll_bar.value = self._scroll_bar.value_range.value_by_alien_scale(
                    alien_value=point_value - 1 - handle_size // 2, alien_max_value=non_handle_size)

    class _HorizontalOrientation(_Orientation):

        def _scroll_bar_length(self) -> int:
            return self._scroll_bar.size.width

        def _scroll(self, horizontal, vertical):
            return horizontal

        def _button_rectangles(self):
            return (viwid.Rectangle(viwid.Point(0, 0), viwid.Size(1, self._scroll_bar.size.height)),
                    viwid.Rectangle(viwid.Point(self._scroll_bar.size.width - 1, 0),
                                    viwid.Size(1, self._scroll_bar.size.height)))

        def _handle_rectangle(self, handle_start, handle_size):
            return viwid.Rectangle(viwid.Point(1 + handle_start, 0),
                                   viwid.Size(handle_size, self._scroll_bar.size.height))

        def _button_label_texts(self):
            return "<", ">"

    class _VerticalOrientation(_Orientation):

        def _scroll_bar_length(self) -> int:
            return self._scroll_bar.size.height

        def _scroll(self, horizontal, vertical):
            return vertical

        def _button_rectangles(self):
            return (viwid.Rectangle(viwid.Point(0, 0), viwid.Size(self._scroll_bar.size.width, 1)),
                    viwid.Rectangle(viwid.Point(0, self._scroll_bar.size.height - 1),
                                    viwid.Size(self._scroll_bar.size.width, 1)))

        def _handle_rectangle(self, handle_start, handle_size):
            return viwid.Rectangle(viwid.Point(0, 1 + handle_start),
                                   viwid.Size(self._scroll_bar.size.width, handle_size))

        def _button_label_texts(self):
            return "^", "v"

    class _Layout(viwid.layout.Layout):

        def __init__(self, scroll_bar: "ScrollBar"):
            super().__init__()
            self.__scroll_bar = scroll_bar

        def apply(self, widgets, size, *, forcefully_apply_resizing_for=()):
            self.__scroll_bar._orientation_handler.apply_layout(widgets, forcefully_apply_resizing_for)

        def compute_layout_width(self, widgets, minimal):
            return 0

        def compute_layout_height(self, widgets, width, minimal):
            return 0
