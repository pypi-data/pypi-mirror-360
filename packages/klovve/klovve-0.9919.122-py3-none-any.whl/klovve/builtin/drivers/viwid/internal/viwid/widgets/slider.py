#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
See :py:class:`Slider`.
"""
import viwid.app.screen
from viwid.widgets.widget import Widget as _Widget


class Slider(_Widget):
    """
    A range of values visualized by a bar together with a picker that allows the user to see and choose one value on
    that range.
    """

    def __init__(self, **kwargs):
        super().__init__(**{**dict(class_style_name="slider", is_focusable=True), **kwargs})
        self.__i = -1
        self.__chars = None
        self.__animation_running = False
        self.__horizontal_slider_text = None
        self.__horizontal_pin_text = None
        self.__vertical_slider_text = None
        self.__vertical_pin_text = None
        self.__move_mouse_grabber = None

    orientation: viwid.Orientation
    @_Widget.Property(default=lambda: viwid.Orientation.HORIZONTAL)
    def orientation(self, _):
        """
        The orientation. :py:attr:`viwid.Orientation.HORIZONTAL` by default.
        """
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

    def __correct_value(self):
        valid_value = self.value_range.valid_value(self.value)
        if self.value != valid_value:
            self.value = valid_value

    def _materialize(self):
        super()._materialize()

        self.__horizontal_slider_text = self._text_measuring.text("▄").render()
        self.__horizontal_pin_text = self._text_measuring.text("█").render()
        self.__vertical_slider_text = self._text_measuring.text("█").render()
        self.__vertical_pin_text = self._text_measuring.text("█").render()

        self.listen_event(viwid.event.mouse.ButtonDownEvent, self.__handle_mouse_button_down,
                          implements_default_behavior=True)
        self.listen_event(viwid.event.mouse.ButtonUpEvent, self.__handle_mouse_button_up,
                          implements_default_behavior=True)
        self.listen_event(viwid.event.mouse.MoveEvent, self.__handle_mouse_move, implements_default_behavior=True)
        self.listen_event(viwid.event.keyboard.KeyPressEvent, self.__handle_keyboard_key_pressed,
                          implements_default_behavior=True)

    def _dematerialize(self):
        self.unlisten_event(self.__handle_mouse_button_down)
        self.unlisten_event(self.__handle_mouse_button_up)
        self.unlisten_event(self.__handle_mouse_move)
        self.unlisten_event(self.__handle_keyboard_key_pressed)

        super()._dematerialize()

    def _compute_width(self, minimal) -> int:
        return 2

    def _compute_height(self, width: int, minimal) -> int:
        return 1 if self.orientation == viwid.Orientation.HORIZONTAL else 2

    def _paint(self, canvas):
        size_one = viwid.Size(1, 1)
        value = self.value_range.valid_value(self.value)
        if self.orientation == viwid.Orientation.HORIZONTAL:
            i_value = self.value_range.value_to_alien_scale(value, alien_max_value=self.size.width-1)
            for i in range(self.size.width):
                canvas.draw_text(self.__horizontal_slider_text, rectangle=viwid.Rectangle(viwid.Point(i, 0), size_one))
                if i == i_value:
                    canvas.draw_text(self.__horizontal_pin_text, rectangle=viwid.Rectangle(viwid.Point(i, 0), size_one))
        else:
            i_value = self.size.height - 1 - self.value_range.value_to_alien_scale(value,
                                                                                   alien_max_value=self.size.height-1)
            for i in range(self.size.height):
                canvas.draw_text(self.__vertical_slider_text, rectangle=viwid.Rectangle(viwid.Point(0, i), size_one))
                if i == i_value:
                    canvas.draw_text(self.__vertical_pin_text, rectangle=viwid.Rectangle(viwid.Point(1, i), size_one))

    def __handle_mouse_button_down(self, event: viwid.event.mouse.ButtonDownEvent) -> None:
        self.__handle_mouse_move(event, force=True)
        self.__move_mouse_grabber = event.grab_mouse(self)
        self.__move_mouse_grabber.__enter__()

    def __handle_mouse_button_up(self, event: viwid.event.mouse.ButtonUpEvent) -> None:
        if self.__move_mouse_grabber:
            self.__move_mouse_grabber.__exit__(None, None, None)
            self.__move_mouse_grabber = None

    def __handle_mouse_move(self, event: viwid.event.mouse._Event, *, force: bool = False) -> None:
        if self.__move_mouse_grabber or force:
            position = viwid.app.screen.translate_coordinates_from_root(event.screen_position, new_origin=self)
            if self.orientation == viwid.Orientation.HORIZONTAL:
                mouse_value, mouse_max_value = position.x, self.size.width - 1
            else:
                mouse_value, mouse_max_value = self.size.height - 1 - position.y, self.size.height - 1
            self.value = self.value_range.value_by_alien_scale(alien_value=mouse_value, alien_max_value=mouse_max_value)

    def __handle_keyboard_key_pressed(self, event: viwid.event.keyboard.KeyPressEvent) -> None:
        if self.orientation == viwid.Orientation.HORIZONTAL:
            direction = {viwid.event.keyboard.KeyCodes.ARROW_LEFT: -1,
                         viwid.event.keyboard.KeyCodes.ARROW_RIGHT: 1}.get(event.code, 0)
        else:
            direction = {viwid.event.keyboard.KeyCodes.ARROW_DOWN: -1,
                         viwid.event.keyboard.KeyCodes.ARROW_UP: 1}.get(event.code, 0)
        if direction:
            self.value = self.value_range.step_number_to_value(
                self.value_range.value_to_step_number(self.value) + direction)
            event.stop_handling()
