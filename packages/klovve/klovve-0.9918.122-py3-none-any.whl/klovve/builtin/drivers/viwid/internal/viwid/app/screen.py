#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
Screen specific application aspects.

See :py:class:`ScreenLayer` and other part of the module.
"""
import typing as t

import viwid.event
import viwid.layout

if t.TYPE_CHECKING:
    import viwid.app.manager


class ScreenLayer:
    """
    Screen layers are one piece in the chain of how applications interact with the outer world (in terms of presenting
    widgets visually on the screen and receiving user input).

    A typical application gets one screen layer for its main window, and then maybe a few more for dialog windows or
    popups.

    Each screen layer has one root widget. Many screen layers represent a window, so they have a window as root widget.

    A screen layer can be modal, so it splits everything below it and everything in front of it (and itself) into two
    modality contexts. The user is only able to interact with the topmost modality context.
    """

    def __init__(self, application_manager: "viwid.app.manager.ApplicationManager", app: "viwid.app.Application|None",
                 widget: "viwid.widgets.widget.Widget", is_modal: bool):
        """
        Usually you do not create instances directly. See :py:meth:`viwid.app.Application.add_layer_for_window` and
        :py:meth:`viwid.app.Application.add_layer`.

        :param application_manager: The application manager that owns this screen layer.
        :param app: The application that owns this screen layer.
        :param widget: The root widget.
        :param is_modal: Whether this screen layer shall be modal.
        """
        self.__application_manager = application_manager
        self.__app = app
        self.__widget = widget
        self.__is_modal = is_modal
        self.__focused_widget = None

    @property
    def application(self) -> "viwid.app.Application|None":
        """
        The application that owns this screen layer.

        This can be `None` if the screen layer is not used for an application, but for the application managers own
        purposes. You usually do not get access to them at all, though, so this case is only relevant for
        infrastructure.
        """
        return self.__app

    @property
    def widget(self) -> "viwid.widgets.widget.Widget":
        """
        The root widget.
        """
        return self.__widget

    @property
    def is_modal(self) -> bool:
        """
        Whether this screen layer is modal.
        """
        return self.__is_modal

    @property
    def focused_widget(self) -> "viwid.widgets.widget.Widget|None":
        """
        The screen layer's focused widget.
        """
        if self.__focused_widget and ((self.__focused_widget.screen_layer is not self)
                                      or not self.__focused_widget.is_actually_visible
                                      or not self.__focused_widget.is_actually_enabled):
            self.__focused_widget = None
        return self.__focused_widget

    @focused_widget.setter
    def focused_widget(self, _: "viwid.widgets.widget.Widget|None"):
        self.__focused_widget = _
        self.__application_manager._widget_focused()

    @property
    def cursor_position(self) -> viwid.Point|None:
        """
        This screen layer's current keyboard cursor position.

        The cursor position has solely visual purposes and does not influence and behavior.
        """
        if self.__focused_widget and self.__focused_widget.cursor_position:
            point, is_visible = translate_coordinates_to_root(self.__focused_widget.cursor_position,
                                                              old_origin=self.__focused_widget)
            if is_visible:
                return translate_coordinates_from_root(point, new_origin=self.__widget)

    @staticmethod
    def trigger_event(widget: "viwid.widgets.widget.Widget", event: "viwid.event.Event",
                     *, bubble_upwards: bool = True) -> None:
        """
        Trigger an event on this screen layer for given widget.

        The event handling usually involves not only `widget` itself, but any widget on the axis of ancestors. See also
        :py:class:`viwid.event.Event`.

        :param widget: The widget to trigger the event for.
        :param event: The event to trigger.
        :param bubble_upwards: Whether to involve other widgets on the axis of ancestors (or restrict event handling to
                               the given widget only).
        """
        if (isinstance(event, viwid.event.mouse.MoveEvent) and not event.is_left_button_pressed
                and not event.is_middle_button_pressed and not event.is_right_button_pressed):
            widget.application_manager._set_hovered_widget(widget)

        widgets = []
        widgets_enabled_from_i = 0
        widget_ = widget
        i = 0
        while widget_ and not event.is_handling_stopped:
            widgets.append(widget_)
            if not widget_.is_enabled:
                widgets_enabled_from_i = i + 1
            widget_ = widget_.parent if bubble_upwards else None
            i += 1

        for widget_ in reversed(widgets):
            if event.is_handling_stopped or not widget_.is_enabled:
                break
            widget_._handle_event(event, preview=True)

        for i_widget, widget_ in enumerate(widgets[widgets_enabled_from_i:]):
            if event.is_handling_stopped:
                break
            widget_._handle_event(event, preview=False)

    def _cursor_position_changed(self, widget: "viwid.widgets.widget.Widget") -> None:
        """
        Called by the infrastructure when the keyboard cursor position has been changed for a widget.

        :param widget: The widget that has changed its cursor position.
        """
        if widget is self.__focused_widget:
            self.__application_manager._cursor_position_changed()


def translate_coordinates_to_root(point: viwid.Point, *,
                                  old_origin: "viwid.widgets.widget.Widget") -> tuple[viwid.Point, bool]:
    """
    Translate a given position from the coordinate space of the given widget to screen coordinates.

    Return a tuple of the translated position and whether it is actually visible on the screen (instead of being out of
    visible range, e.g. in a scrollable area).

    See also :py:func:`translate_coordinates_from_root`.

    :param point: The position.
    :param old_origin: The widget of the coordinate space to translate from.
    """
    is_visible = True
    while old_origin is not None:
        if point.x < 0 or point.y < 0 or point.x >= old_origin.size.width or point.y >= old_origin.size.height:
            is_visible = False
        point += old_origin.position
        old_origin = old_origin.parent
    return point, is_visible


def translate_coordinates_from_root(point: viwid.Point, *,
                                    new_origin: "viwid.widgets.widget.Widget") -> viwid.Point:
    """
    Translate a given position from screen coordinates to the coordinate space of the given widget.

    See also :py:func:`translate_coordinates_to_root`.

    :param point: The position.
    :param new_origin: The widget of the coordinate space to translate to.
    """
    reverse_point, _ = translate_coordinates_to_root(viwid.Point.ORIGIN, old_origin=new_origin)
    return point - reverse_point


class Layout(viwid.layout.GridLayout):
    """
    A special layout for the alignment of the root widget inside a screen layer.
    """

    def __init__(self, *, only_initially: bool = False, anchor_widget: "viwid.widgets.widget.Widget|None" = None):
        super().__init__(viwid.layout.GridLayout.HORIZONTAL_PARTITIONER)
        self.__only_initially = only_initially
        self.__anchor_widget = anchor_widget
        self.__is_first_time = True
        self.__last_geometry = None

    def apply(self, widgets, size, *, forcefully_apply_resizing_for = ()):
        if not size.width or not size.height:
            return

        if self.__is_first_time or not self.__only_initially or self.__anchor_widget:
            if self.__anchor_widget:
                anchor_widget_screen_position, _ = translate_coordinates_to_root(viwid.Point.ORIGIN,
                                                                                 old_origin=self.__anchor_widget)
                height_above = anchor_widget_screen_position.y
                height_below = size.height - anchor_widget_screen_position.y - self.__anchor_widget.size.height
                for widget in widgets:
                    widget_width = widget.width_demand(minimal=False)
                    widget_height = widget.height_demand(widget_width, minimal=False)
                    if height_above < height_below:
                        widget_height = min(widget_height, height_below)
                        widget_x = anchor_widget_screen_position.x
                        widget_y = anchor_widget_screen_position.y + self.__anchor_widget.size.height
                        position, size_ = Layout.unshrunk_widget_alignment(
                            widget, viwid.Point(widget_x, widget_y), viwid.Size(widget_width, widget_height), size)
                        widget.align(position, size_, forcefully_apply_resizing_for=forcefully_apply_resizing_for)
                    else:
                        widget_height = min(widget_height, height_above)
                        widget_x = anchor_widget_screen_position.x
                        widget_y = anchor_widget_screen_position.y - widget_height
                        position, size_ = Layout.unshrunk_widget_alignment(
                            widget, viwid.Point(widget_x, widget_y), viwid.Size(widget_width, widget_height), size)
                        widget.align(position, size_, forcefully_apply_resizing_for=forcefully_apply_resizing_for)
            else:
                geometry = tuple((widget.position, widget.size) for widget in widgets)
                if self.__last_geometry is None:
                    self.__last_geometry = geometry
                elif self.__is_first_time:
                    self.__is_first_time = self.__last_geometry == geometry

                if self.__is_first_time or not self.__only_initially:
                    super().apply(widgets, size, forcefully_apply_resizing_for=forcefully_apply_resizing_for)

                if self.__is_first_time:
                    self.__last_geometry = tuple((widget.position, widget.size) for widget in widgets)

        for widget in widgets:
            position, size_ = Layout.unshrunk_widget_alignment(widget, widget.position, widget.size, size)
            widget.align(position, size_, forcefully_apply_resizing_for=forcefully_apply_resizing_for)

    def _stretch_from_partitioning(self, partitioning):
        return (True,), (True,)

    @staticmethod
    def unshrunk_widget_alignment(widget: "viwid.widgets.widget.Widget", position: viwid.Point, size: viwid.Size,
                                  screen_size: viwid.Size) -> tuple[viwid.Point, viwid.Size]:
        """
        For a given alignment, return an alignment that tries as good as possible to meet the widget's size demand.

        :param widget: The widget.
        :param position: The suggested position.
        :param size: The suggested size.
        :param screen_size: The screen size.
        """
        if widget.horizontal_alignment == viwid.Alignment.FILL_EXPANDING:
            width = screen_size.width
            height = screen_size.height
            x = y = 0

        else:
            x = position.x
            y = position.y
            width = size.width
            height = size.height
            width = max(width, widget.width_demand(minimal=True))
            height = max(height, widget.height_demand(width, minimal=True))

            if height > screen_size.height:
                width, height = widget.width_demand_for_height(screen_size.height), screen_size.height

            missing_width = (width + x) - screen_size.width
            missing_height = (height + y) - screen_size.height
            if missing_width > 0:
                x -= missing_width
            if missing_height > 0:
                y -= missing_height

        return (viwid.Point(max(0, x), max(0, y)),
                viwid.Size(min(screen_size.width, width), min(screen_size.height, height)))
