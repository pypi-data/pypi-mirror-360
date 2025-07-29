#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
See :py:class:`Split`.
"""
import abc

import viwid.layout
import viwid.app.screen
from viwid.widgets.widget import Widget as _Widget


class Split(_Widget):
    """
    An arbitrary first widget and an arbitrary second widget (either left&right or top&bottom), together with a splitter
    between them which lets the user control how much visual space of the available area both widgets get.
    """

    def __init__(self, **kwargs):
        super().__init__(**{**dict(layout=Split._Layout(self)), **kwargs})
        self._orientation_handler = None
        self.__null_widget_1 = viwid.widgets.widget.Widget()
        self.__null_widget_2 = viwid.widgets.widget.Widget()
        self._splitter = Split._Splitter()
        self._children = [self.__null_widget_1, self._splitter, self.__null_widget_2]
        self.__move_mouse_grabber = None

    item_1: _Widget|None
    @_Widget.Property
    def item_1(self, _):
        """
        The left or top (see :py:attr:`orientation`) widget. `None` by default.
        """
        self._children[0] = self.__null_widget_1 if _ is None else _
        self._request_resize_and_repaint()

    item_2: _Widget|None
    @_Widget.Property
    def item_2(self, _):
        """
        The right or bottom (see :py:attr:`orientation`) widget. `None` by default.
        """
        self._children[2] = self.__null_widget_2 if _ is None else _
        self._request_resize_and_repaint()

    splitter_position: float
    @_Widget.Property(default=lambda: 0.5)
    def splitter_position(self, _):
        """
        The current splitter position. Between `0` and `1`. `0.5` by default.
        """
        self._request_resize_and_repaint()

    orientation: viwid.Orientation
    @_Widget.Property(default=lambda: viwid.Orientation.HORIZONTAL)
    def orientation(self, _):
        """
        The orientation. :py:attr:`viwid.Orientation.HORIZONTAL` by default.
        """
        self._orientation_handler = (Split._HorizontalOrientation(self)
                                     if self.orientation == viwid.Orientation.HORIZONTAL
                                     else Split._VerticalOrientation(self))
        self._request_resize_and_repaint()

    def _materialize(self):
        super()._materialize()

        self._splitter.listen_event(viwid.event.mouse.ButtonDownEvent, self.__handle_splitter_mouse_button_down,
                                    implements_default_behavior=True)
        self._splitter.listen_event(viwid.event.mouse.ButtonUpEvent, self.__handle_splitter_mouse_button_up,
                                    implements_default_behavior=True)
        self._splitter.listen_event(viwid.event.mouse.MoveEvent, self.__handle_splitter_mouse_moved,
                                    implements_default_behavior=True)
        self._splitter.listen_event(viwid.event.keyboard.KeyPressEvent, self.__handle_splitter_keyboard_key_pressed,
                                    implements_default_behavior=True)

    def _dematerialize(self):
        self._splitter.unlisten_event(self.__handle_splitter_mouse_button_down)
        self._splitter.unlisten_event(self.__handle_splitter_mouse_button_up)
        self._splitter.unlisten_event(self.__handle_splitter_mouse_moved)
        self._splitter.unlisten_event(self.__handle_splitter_keyboard_key_pressed)

        super()._dematerialize()

    def __handle_splitter_mouse_button_down(self, event: viwid.event.mouse.ButtonDownEvent) -> None:
        self.__move_mouse_grabber = event.grab_mouse(self._splitter)
        self.__move_mouse_grabber.__enter__()

    def __handle_splitter_mouse_button_up(self, event: viwid.event.mouse.ButtonUpEvent) -> None:
        if self.__move_mouse_grabber:
            self.__move_mouse_grabber.__exit__(None, None, None)
            self.__move_mouse_grabber = None

    def __handle_splitter_mouse_moved(self, event: viwid.event.mouse.MoveEvent) -> None:
        if self.__move_mouse_grabber:
            self._orientation_handler.handle_splitter_moved(event)

    def __handle_splitter_keyboard_key_pressed(self, event: viwid.event.keyboard.KeyPressEvent) -> None:
        self._orientation_handler.handle_splitter_keyboard_key_pressed(event)

    class _Layout(viwid.layout.Layout):

        def __init__(self, split: "Split"):
            self.__split = split

        def apply(self, widgets, size, *, forcefully_apply_resizing_for=()):
            return self.__split._orientation_handler.layout_apply(size, forcefully_apply_resizing_for)

        def compute_layout_width(self, widgets, minimal):
            return self.__split._orientation_handler.layout_compute_width(minimal)

        def compute_layout_height(self, widgets, width, minimal):
            return self.__split._orientation_handler.layout_compute_height(width, minimal)

    class _Splitter(_Widget):

        def __init__(self, **kwargs):
            super().__init__(**{**dict(class_style_name="control", is_focusable=True), **kwargs})

        def _compute_width(self, minimal):
            return 1

        def _compute_height(self, width, minimal):
            return 1

    class _Orientation(abc.ABC):

        def __init__(self, split: "Split"):
            self._split = split

        @abc.abstractmethod
        def _combined_width(self, item_1_width_demand: int, item_2_width_demand: int) -> int:
            pass

        @abc.abstractmethod
        def _combined_height(self, item_1_height_demand: int, item_2_height_demand: int) -> int:
            pass

        @abc.abstractmethod
        def _layout_split(self, size: viwid.Size
                          ) -> tuple[viwid.Point, viwid.Size, viwid.Point, viwid.Size, viwid.Point, viwid.Size]:
            pass

        @abc.abstractmethod
        def _point_to_splitter_position(self, position: viwid.Point) -> int:
            pass

        @abc.abstractmethod
        def _item_widths(self, width: int) -> tuple[int, int]:
            pass

        @abc.abstractmethod
        def _get_splitter_position_constraints(self) -> tuple[float, float]:
            pass

        def _moved_splitter_position(self, event: viwid.event.keyboard.KeyPressEvent) -> float|None:
            if event.code == viwid.event.keyboard.KeyCodes.ARROW_LEFT:
                direction = -1
            elif event.code == viwid.event.keyboard.KeyCodes.ARROW_RIGHT:
                direction = 1
            else:
                return None
            return self._split.splitter_position + direction * (1 / self._split.size.width)

        def _splitter_position_constraints(self) -> tuple[float, float]:
            has_item_1 = self._split.item_1 and self._split.item_1.is_visible
            has_item_2 = self._split.item_2 and self._split.item_2.is_visible
            if has_item_1 and has_item_2:
                min_value, max_value = self._get_splitter_position_constraints()
                min_value = min(max(0.0, min_value), 1.0)
                max_value = min(max(min_value, max_value), 1.0)
                return min_value, max_value
            else:
                return 1, 1

        def handle_splitter_keyboard_key_pressed(self, event: viwid.event.keyboard.KeyPressEvent) -> None:
            if (moved_splitter_position := self._moved_splitter_position(event)) is not None:
                min_value, max_value = self._splitter_position_constraints()
                self._split.splitter_position = min(max(min_value, moved_splitter_position), max_value)
                event.stop_handling()

        def handle_splitter_moved(self, event: viwid.event.mouse.MoveEvent) -> None:
            min_value, max_value = self._splitter_position_constraints()
            self._split.splitter_position = min(max(min_value, self._point_to_splitter_position(
                viwid.app.screen.translate_coordinates_from_root(
                    event.screen_position, new_origin=self._split))), max_value)

        def layout_apply(self, size: viwid.Size, forcefully_apply_resizing_for) -> None:
            has_item_1 = self._split.item_1 and self._split.item_1.is_visible
            has_item_2 = self._split.item_2 and self._split.item_2.is_visible
            item_1_position = splitter_position = item_2_position = viwid.Point.ORIGIN
            item_1_size, splitter_size, item_2_size = viwid.Size.NULL, viwid.Size.NULL, viwid.Size.NULL
            if has_item_1 and has_item_2:
                (item_1_position, item_1_size, splitter_position, splitter_size,
                 item_2_position, item_2_size) = self._layout_split(size)
            elif has_item_1:
                item_1_size = size
            elif has_item_2:
                item_2_size = size

            if self._split.item_1:
                self._split.item_1.align(item_1_position, item_1_size,
                                         forcefully_apply_resizing_for=forcefully_apply_resizing_for)
            if self._split.item_2:
                self._split.item_2.align(item_2_position, item_2_size,
                                         forcefully_apply_resizing_for=forcefully_apply_resizing_for)
            self._split._splitter.align(splitter_position, splitter_size)

        def layout_compute_width(self, minimal: bool) -> int:
            has_item_1 = self._split.item_1 and self._split.item_1.is_visible
            has_item_2 = self._split.item_2 and self._split.item_2.is_visible
            item_1_width_demand = self._split.item_1.width_demand(minimal=minimal) if has_item_1 else 0
            item_2_width_demand = self._split.item_2.width_demand(minimal=minimal) if has_item_2 else 0
            if item_1_width_demand and item_2_width_demand:
                return self._combined_width(item_1_width_demand, item_2_width_demand)
            elif item_1_width_demand:
                return item_1_width_demand
            elif item_2_width_demand:
                return item_2_width_demand
            else:
                return 0

        def layout_compute_height(self, width: int, minimal: bool) -> int:
            has_item_1 = self._split.item_1 and self._split.item_1.is_visible
            has_item_2 = self._split.item_2 and self._split.item_2.is_visible
            if has_item_1 and has_item_2:
                item_1_width, item_2_width = self._item_widths(width)
            elif has_item_1:
                item_1_width, item_2_width = width, 0
            elif has_item_2:
                item_1_width, item_2_width = 0, width
            else:
                return 0
            item_1_height_demand = (self._split.item_1.height_demand(item_1_width, minimal=minimal)
                                    if has_item_1 and item_1_width else 0)
            item_2_height_demand = (self._split.item_2.height_demand(item_2_width, minimal=minimal)
                                    if has_item_2 and item_2_width else 0)
            if item_1_height_demand and item_2_height_demand:
                return self._combined_height(item_1_height_demand, item_2_height_demand)
            elif item_1_height_demand:
                return item_1_height_demand
            elif item_2_height_demand:
                return item_2_height_demand
            else:
                return 0

    class _HorizontalOrientation(_Orientation):

        def _combined_width(self, item_1_width_demand, item_2_width_demand):
            return item_1_width_demand + item_2_width_demand + 1

        def _combined_height(self, item_1_height_demand, item_2_height_demand):
            return max(item_1_height_demand, item_2_height_demand)

        def _layout_split(self, size):
            min_value, max_value = self._splitter_position_constraints()
            item_1_width = min(max(0, int(size.width * min(max(min_value, self._split.splitter_position),
                                                           max_value))), size.width-1)
            item_2_width = size.width - item_1_width - 1
            return (viwid.Point.ORIGIN, viwid.Size(item_1_width, size.height),
                    viwid.Point(item_1_width, 0), viwid.Size(1, size.height),
                    viwid.Point(item_1_width+1, 0), viwid.Size(item_2_width, size.height))

        def _point_to_splitter_position(self, position):
            return position.x / self._split.size.width

        def _item_widths(self, width):
            item_1_width = min(max(0, int(width * self._split.splitter_position)), width-1)
            item_2_width = width - item_1_width - 1
            return item_1_width, item_2_width

        def _get_splitter_position_constraints(self):
            width, height = self._split.size.width, self._split.size.height
            item_1_minimal_width = self.__minimal_item_width(self._split.item_1, height)
            item_2_minimal_width = self.__minimal_item_width(self._split.item_2, height)
            return item_1_minimal_width / width + 0.01, (0.99 - item_2_minimal_width / width)

        def _moved_splitter_position(self, event):
            if event.code == viwid.event.keyboard.KeyCodes.ARROW_LEFT:
                direction = -1
            elif event.code == viwid.event.keyboard.KeyCodes.ARROW_RIGHT:
                direction = 1
            else:
                return None
            return self._split.splitter_position + direction * (1 / self._split.size.width)

        def __minimal_item_width(self, item, height: int) -> int:
            return item.width_demand_for_height(height)

    class _VerticalOrientation(_Orientation):

        def _combined_width(self, item_1_width_demand, item_2_width_demand):
            return max(item_1_width_demand, item_2_width_demand)

        def _combined_height(self, item_1_height_demand, item_2_height_demand):
            return item_1_height_demand + item_2_height_demand + 1

        def _layout_split(self, size):
            min_value, max_value = self._splitter_position_constraints()
            item_1_height = min(max(0, int(size.height * min(max(min_value, self._split.splitter_position),
                                                             max_value))), size.height-1)
            item_2_height = size.height - item_1_height - 1
            return (viwid.Point.ORIGIN, viwid.Size(size.width, item_1_height),
                    viwid.Point(0, item_1_height), viwid.Size(size.width, 1),
                    viwid.Point(0, item_1_height+1), viwid.Size(size.width, item_2_height))

        def _point_to_splitter_position(self, position):
            return position.y / self._split.size.height

        def _item_widths(self, width):
            return width, width

        def _get_splitter_position_constraints(self):
            width, height = self._split.size.width, self._split.size.height
            item_1_minimal_height = self.__minimal_item_height(self._split.item_1, width, height)
            item_2_minimal_height = self.__minimal_item_height(self._split.item_2, width, height)
            return item_1_minimal_height / height + 0.01, (0.99 - item_2_minimal_height / height)

        def _moved_splitter_position(self, event):
            if event.code == viwid.event.keyboard.KeyCodes.ARROW_UP:
                direction = -1
            elif event.code == viwid.event.keyboard.KeyCodes.ARROW_DOWN:
                direction = 1
            else:
                return None
            return self._split.splitter_position + direction * (1 / self._split.size.height)

        def __minimal_item_height(self, item, width: int, height: int) -> int:
            return item.height_demand(width, minimal=True)
