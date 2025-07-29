#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
See :py:class:`Box`.
"""
import math

import viwid.data.color
import viwid.layout
from viwid.widgets.widget import Widget as _Widget


class Box(_Widget):
    """
    A box. It has no own visual representation and no behavior, but aligns its child widgets either horizontally or
    vertically.
    """

    def __init__(self, **kwargs):
        super().__init__(**{**dict(layout=viwid.layout.GridLayout(self.__partitioner)), **kwargs})

    background: viwid.data.color.TColorInput|None
    @_Widget.Property
    def background(self, _):
        """
        The optional background color. `None` by default.
        """
        self._request_repaint()

    orientation: viwid.Orientation
    @_Widget.Property(default=lambda: viwid.Orientation.HORIZONTAL)
    def orientation(self, _):
        """
        The orientation. :py:attr:`viwid.Orientation.HORIZONTAL` by default.
        """
        self._request_resize_and_repaint()

    def __partitioner(self, widgets):
        if self.orientation == viwid.Orientation.VERTICAL:
            return viwid.layout.GridLayout.VERTICAL_PARTITIONER(widgets)
        else:
            return viwid.layout.GridLayout.HORIZONTAL_PARTITIONER(widgets)

    def __item_added(self, index: int, item: _Widget) -> None:
        self._children.insert(index, item)

    def __item_removed(self, index: int, item: _Widget) -> None:
        self._children.pop(index)

    @_Widget.ListProperty(__item_added, __item_removed)
    def children(self) -> list:
        """
        The child widgets.
        """

    def _paint(self, canvas):
        super()._paint(canvas)
        if self.background:
            canvas.fill(self.background)

class _RootBox(Box):

    def __init__(self, **kwargs):
        super().__init__(**{**dict(background=viwid.PlainColor.TRANSPARENT), **kwargs})

    def _materialize(self):
        super()._materialize()

        self.listen_event(viwid.event.keyboard.KeyPressEvent, self.__handle_keyboard_key_pressed,
                          implements_default_behavior=True)

    def _dematerialize(self):
        self.unlisten_event(self.__handle_keyboard_key_pressed)

        super()._dematerialize()

    def __handle_keyboard_key_pressed(self, event: viwid.event.keyboard.KeyPressEvent) -> None:
        if self.screen_layer.focused_widget is None:
            return

        match event.code:
            case viwid.event.keyboard.KeyCodes.ARROW_UP:
                delta = 0, -1
            case viwid.event.keyboard.KeyCodes.ARROW_RIGHT:
                delta = 1, 0
            case viwid.event.keyboard.KeyCodes.ARROW_DOWN:
                delta = 0, 1
            case viwid.event.keyboard.KeyCodes.ARROW_LEFT:
                delta = -1, 0
            case _:
                delta = None

        if delta is not None:
            if self.__handle_arrow_key_pressed(self.screen_layer.focused_widget, delta[0], delta[1]):
                event.stop_handling()

    def __handle_arrow_key_pressed(self, from_widget: "Widget", delta_x: int, delta_y: int) -> bool:
        from_rectangle = viwid.Rectangle(
            viwid.app.screen.translate_coordinates_to_root(viwid.Point.ORIGIN, old_origin=from_widget)[0],
            from_widget.size)

        score_for_widgets = {}
        screen_size = from_widget.screen_layer.application.screen_size
        for widget in from_widget.screen_layer.widget.with_all_descendants():
            if widget is from_widget:
                continue
            if not (widget.is_focusable and widget.is_actually_visible and widget.is_actually_enabled):
                continue

            widget_rectangle = viwid.Rectangle(
                viwid.app.screen.translate_coordinates_to_root(viwid.Point.ORIGIN, old_origin=widget)[0],
                widget.size)

            if delta_x < 0:
                thin_area = viwid.Rectangle(viwid.Point(0, from_rectangle.top_y),
                                            viwid.Size(from_rectangle.left_x, from_rectangle.height))
                large_area = viwid.Rectangle(viwid.Point(0, 0),
                                             viwid.Size(from_rectangle.left_x, screen_size.height))
            elif delta_x > 0:
                thin_area = viwid.Rectangle(viwid.Point(from_rectangle.right_x, from_rectangle.top_y),
                                            viwid.Size(screen_size.width, from_rectangle.height))
                large_area = viwid.Rectangle(viwid.Point(from_rectangle.right_x, 0),
                                             viwid.Size(screen_size.width, screen_size.height))
            elif delta_y < 0:
                thin_area = viwid.Rectangle(viwid.Point(from_rectangle.left_x, 0),
                                            viwid.Size(from_rectangle.width, from_rectangle.top_y))
                large_area = viwid.Rectangle(viwid.Point(0, 0),
                                             viwid.Size(screen_size.width, from_rectangle.top_y))
            else:
                thin_area = viwid.Rectangle(viwid.Point(from_rectangle.left_x, from_rectangle.bottom_y),
                                            viwid.Size(from_rectangle.width, screen_size.height))
                large_area = viwid.Rectangle(viwid.Point(0, from_rectangle.bottom_y),
                                             viwid.Size(screen_size.width, screen_size.height))

            in_range_score = 0
            for range_score, range_rectangle in ((2, thin_area), (1, large_area)):
                if widget_rectangle.clipped_by(range_rectangle).area > 0:
                    in_range_score = range_score
                    break

            score_for_widgets[widget] = in_range_score, -self.__handle_arrow_key_pressed__rectangle_distance(
                from_rectangle, widget_rectangle)

        for _, widget in sorted(((v, k) for k, v in score_for_widgets.items()), key=lambda _: _[0], reverse=True):
            if widget.try_focus():
                return True

        return False

    def __handle_arrow_key_pressed__rectangle_distance(self, rectangle_1: viwid.Rectangle,
                                                       rectangle_2: viwid.Rectangle) -> int:
        a1x, a1y = rectangle_1.top_left.x, rectangle_1.top_left.y
        b1x, b1y = rectangle_1.bottom_right.x, rectangle_1.bottom_right.y
        a2x, a2y = rectangle_2.top_left.x, rectangle_2.top_left.y
        b2x, b2y = rectangle_2.bottom_right.x, rectangle_2.bottom_right.y

        is_1_right = b2x < a1x
        is_1_left = b1x < a2x
        is_1_bottom = b2y < a1y
        is_1_top = b1y < a2y

        if is_1_top and is_1_left:
            return self.__handle_arrow_key_pressed__rectangle_distances__distance(b1x, b1y, a2x, a2y)
        if is_1_top and is_1_right:
            return self.__handle_arrow_key_pressed__rectangle_distances__distance(a1x, b1y, b2x, a2y)
        if is_1_bottom and is_1_left:
            return self.__handle_arrow_key_pressed__rectangle_distances__distance(b1x, a1y, a2x, b2y)
        if is_1_bottom and is_1_right:
            return self.__handle_arrow_key_pressed__rectangle_distances__distance(a1x, a1y, b2x, b2y)
        if is_1_top:
            return a2y - b1y
        if is_1_left:
            return a2x - b1x
        if is_1_bottom:
            return a1y - b2y
        if is_1_right:
            return a1x - b2x
        return 0

    def __handle_arrow_key_pressed__rectangle_distances__distance(self, x1: int, y1: int, x2: int, y2: int) -> int:
        return int(math.sqrt((x2 - x1) ** 2 + (2 * (y2 - y1)) ** 2))  # vertically counts double
