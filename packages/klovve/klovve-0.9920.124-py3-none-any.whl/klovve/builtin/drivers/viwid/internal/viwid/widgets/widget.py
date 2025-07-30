#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
Widget base class, including some infrastructure. See :py:class:`Widget`.
"""
import inspect
import functools
import math
import typing as t

import viwid.canvas
import viwid.data.list
import viwid.event.widget
import viwid.layout

if t.TYPE_CHECKING:
    import viwid.app.manager
    import viwid.app.screen
    import viwid.styling
    import viwid.text


class _Property[T](property):

    def __init__(self, setter: t.Callable[[T], None], default=lambda: None, changes_also: t.Sequence[str] = ()):
        super().__init__(self._fget, self._fset)
        self.__setter = setter
        self.__name = setter.__name__
        self.__default = default
        self.__changes_also = changes_also

    def _fget(self, obj) -> T:
        return obj._Widget__kwargs.get(self.__name, self.__default())

    def _fset(self, obj, value: T):
        obj._Widget__kwargs[self.__name] = value
        if obj._Widget__screen_layer:
            self.__setter(obj, value)
        for property_name in (self.__name, *self.__changes_also):
            for func in obj._Widget__property_listeners.get(property_name, ()):
                func()


def Property[T](setter: t.Callable[[T], None]|None = None, /, *,
                default: t.Callable[[], T] = lambda: None,
                changes_also: t.Sequence[str] = ()) -> _Property[T]|t.Callable[[...], _Property[T]]:
    if setter:
        return _Property(setter)
    else:
        def _(setter_):
            return _Property(setter_, default=default, changes_also=changes_also)
        return _


class _ListProperty[T](property):

    def __init__(self, setter, item_added_func: t.Callable[[int, T], None],
                 item_removed_func: t.Callable[[int, T], None],
                 item_replaced_func: t.Callable[[int, T, T], None]|None = None):
        super().__init__(self._fget, self._fset)
        self.__item_added_func = item_added_func
        self.__item_removed_func = item_removed_func
        self.__item_replaced_func = item_replaced_func
        self.__name = setter.__name__

    def _fget(self, obj):
        result = obj._Widget__kwargs.get(self.__name, None)
        if result is None:
            result = obj._Widget__kwargs[self.__name] = viwid.data.list.List()

        if not hasattr(result, "_vwd_observer_added"):
            result._vwd_observer_added = True
            result.add_observer_functions(
                functools.partial(self.__item_added_func, obj),
                functools.partial(self.__item_removed_func, obj),
                functools.partial(self.__item_replaced_func, obj) if self.__item_replaced_func else None)
        return result

    def _fset(self, obj, value):
        self._fget(obj).update(value)


def ListProperty(item_added_func, item_removed_func, item_replaced_func=None) -> property|t.Callable[[...], property]:
    def f(seta):
        return _ListProperty(seta, item_added_func, item_removed_func, item_replaced_func)
    return f


class Widget:
    """
    Widgets are small and composable units that together build a user interface. Every widget has a visual
    representation on the screen and some specific behavior, e.g. in how it deals with user input and other events.

    There are various types of widgets (see its subclasses), for things like simple text output, fields for text input
    by the user, buttons, and a lot more, but also containers like boxes, which have child widgets and align them in
    some way. This can go arbitrarily deep in order to build complex interfaces from these single widgets. In most
    cases, the root of that hierarchy is a :py:class:`viwid.widgets.window.Window`.

    Internally, each widget can have child widgets and each widget has a :py:class:`viwid.layout.Layout` for aligning
    them. However, only some of them (see :py:class:`viwid.widgets.box.Box`) provide that as an external feature. Other
    ones only use that because they use other widgets for their implementation.
    """

    Property = Property
    ListProperty = ListProperty

    _TEventHandler = t.Callable[["viwid.event.Event"], None] | t.Callable[[], None]

    def __init__(self, *, layout: "viwid.layout.Layout|None" = None, class_style_name: str|None = None, **kwargs):
        """
        :param layout: The layout to use. If unspecified, a :py:class:`viwid.layout.NullLayout` will be used, which will
                       leave your child widgets effectively invisible (because they get no size allocated). It is mostly
                       used by widget implementations and rarely specified outside.
        :param class_style_name: The class style name to use for this widget. One of the attribute names in
                                 :py:class:`viwid.styling.Theme.Layer`. It is up to the widget implementation to what
                                 extent it obeys this. It is mostly used by widget implementations and rarely specified
                                 outside.
        :param kwargs: Specify the initial value for arbitrary properties here.
        """
        self.__kwargs = {key: viwid.data.list.List(value) if isinstance(getattr(type(self), key),
                                                                        _ListProperty) else value
                         for key, value in kwargs.items()}
        self.__screen_layer = None
        self.__application_manager = None
        self.__class_style_name = class_style_name
        self.__position = viwid.Point.ORIGIN
        self.__size = viwid.Size.NULL
        self.__rectangle = viwid.Rectangle.NULL
        self.__parent = None
        self.__property_listeners = {}
        self.__layout = layout or viwid.layout.NullLayout()
        self.__layer_style = None
        self.__event_handlers = []
        self.__compute_width_cache = [None, None]
        self.__compute_height_cache = [None, None]
        self.__inner_canvas = viwid.canvas.OffScreenCanvas()
        self.__outer_canvas = viwid.canvas.ComposingCanvas()
        self.__outer_canvas.insert_source_canvas(None, self.__inner_canvas)
        self.__cursor = None
        self.__is_actually_enabled = False
        self.__is_actually_visible = False

    is_enabled: bool
    @Property(default=lambda: True)
    def is_enabled(self, _):
        """
        Whether this widget is enabled. :code:`True` by default.

        If not, this widget as well as all widgets inside it, will be painted in a different representation and will
        not receive any user input.

        See also :py:attr:`is_actually_enabled`.
        """
        self.__actual_properties_changed()
        self._request_repaint()

    is_visible: bool
    @Property(default=lambda: True)
    def is_visible(self, _):
        """
        Whether this widget is visible. :code:`True` by default.

        If not, this widget as well as all widgets inside it, will usually not get allocated any size and are not
        visible on the screen.

        See also :py:attr:`is_actually_visible`.
        """
        self.__actual_properties_changed()
        self._request_resize()

    is_focusable: bool
    @Property(default=lambda: False)
    def is_focusable(self, _):
        """
        Whether this widget is focusable. :code:`False` by default.

        This is usually controlled by the widget implementation and is usually constant.

        A focusable widget can be "selected" via the Tab keyboard key or clicking on it with the mouse. Usually it has
        a different visual representation then, in order to show the user which widget is focused.

        Keyboard user input gets forwarded to the focused widget, so only focusable widgets can receive keyboard input.

        Every focusable widget is automatically hoverable as well (see :py:attr:`is_hoverable`)!
        """
        if not _ and self.screen_layer.focused_widget is self:
            self.screen_layer.focused_widget = None

    is_hoverable: bool
    @Property(default=lambda: False)
    def is_hoverable(self, _):
        """
        Whether this widget is still hoverable, although :py:attr:`is_focusable` is :code:`False` (if the latter is
        :code:`True`, this flag has no effect - it is automatically considered as hoverable). :code:`False` by default.

        A hoverable widget usually changes its visual representation when it is touched by the mouse cursor, until the
        mouse cursor leaves it. This implies no behavioral change but signals to the user that this element could be
        useful to click on.

        This is usually controlled by the widget implementation and is usually constant.

        Every focusable widget (see :py:attr:`is_focusable`) is automatically hoverable as well!
        """
        if not _ and self.application_manager.hovered_widget is self:
            self.application_manager._set_hovered_widget(None)

    @property
    def is_materialized(self) -> bool:
        """
        Whether this widget is materialized. If so, the widget is connected to the infrastructure and could be actually
        visible on screen and could actually receive user input.

        A widget is not yet materialized during construction, so some infrastructure features (like
        :py:attr:`_text_measuring`) are not yet available at very early times.

        This flag usually does not matter for application developers. For widget development, see
        :py:meth:`_materialize`.
        """
        return self.__screen_layer is not None

    @property
    def is_actually_enabled(self) -> bool:
        """
        Whether this widget is actually enabled, i.e. :py:attr:`is_enabled` is set on this widget as well as all its
        ancestors up to the root widget.
        """
        return self.__is_actually_enabled

    @property
    def is_actually_visible(self) -> bool:
        """
        Whether this widget is actually potentially visible on its screen layer, i.e. :py:attr:`is_visible` is set on
        this widget as well as all its ancestors up to the root widget.

        Note: It could still happen that the widget has no size, is not even materialized, or is just out of range of
        a scrollable area.
        """
        return self.__is_actually_visible

    vertical_alignment: viwid.Alignment
    @Property(default=lambda: viwid.Alignment.FILL_EXPANDING)
    def vertical_alignment(self, _):
        """
        Specifies how to align this widget within its available space vertically.
        :py:attr:`viwid.Alignment.FILL_EXPANDING` by default, but some subclasses choose their own default.
        """
        self._request_resize()

    horizontal_alignment: viwid.Alignment
    @Property(default=lambda: viwid.Alignment.FILL_EXPANDING)
    def horizontal_alignment(self, _):
        """
        Specifies how to align this widget within its available space horizontally.
        :py:attr:`viwid.Alignment.FILL_EXPANDING` by default, but some subclasses choose their own default.
        """
        self._request_resize()

    minimal_size: viwid.Size
    @Property(default=lambda: viwid.Size.NULL)
    def minimal_size(self, _):
        """
        The widget's minimal size. :py:attr:`viwid.Size.NULL` by default.

        The alignment routine will always present the widget in at least this size, even if it would have lower demands.

        This does not influence the size demand computation of the widget. Instead, it is a size that an application
        developer can specify manually for UI design purposes. It is mostly considered by
        :py:class:`viwid.layout.Layout` implementations.
        """
        self._request_resize()

    margin: viwid.Margin
    @Property(default=lambda: viwid.Margin.NULL)
    def margin(self, _):
        """
        The widget's margin. :py:attr:`viwid.Margin.NULL` by default.

        The alignment routine will always put this amount of free space around this widget. This does not influence
        the size demand computation or the widget's own size (see :py:attr:`size`) but is mostly considered by
        :py:class:`viwid.layout.Layout` implementations.
        """
        self._request_resize()

    @property
    def layer_style(self) -> "viwid.styling.Theme.Layer":
        """
        The widget's layer style.
        """
        return self.__layer_style or self.parent.layer_style

    @property
    def application_manager(self) -> "viwid.app.manager.ApplicationManager":
        """
        The widget's application manager.
        """
        return self.__application_manager

    @property
    def parent(self) -> "Widget|None":
        """
        The parent widget.

        This is :code:`None` for unmaterialized widgets and the root widget of a screen layer.
        """
        return self.__parent

    @property
    def class_style_name(self) -> str:
        """
        The widget's class style name. One of the attribute names in :py:class:`viwid.styling.Theme.Layer`.
        """
        return self.__class_style_name or (self.parent.class_style_name if self.parent else "plain")

    def listen_property(self, property_name: str, func: t.Callable[[], None]) -> None:
        """
        Listen for changes on a given property. The given function will be called whenever the value of this property
        changes for any reason, until you call :py:meth:`unlisten_property`.

        :param property_name: The name of the property to listen to.
        :param func: The function to be called when the property value changes.
        """
        self.__property_listeners[property_name] = l = self.__property_listeners.get(property_name) or []
        l.append(func)

    def unlisten_property(self, property_name: str, func: t.Callable[[], None]) -> None:
        """
        Stop listening to a property. See :py:meth:`listen_property`.

        If the given function was registered more than once for the given property, it gets removed once. If it was not
        registered, `ValueError` gets raised.

        :param property_name: The name of the property.
        :param func: The function to stop listening with.
        """
        if l := self.__property_listeners.get(property_name):
            l.remove(func)
            return
        raise ValueError(f"not found")

    def listen_event[TEvent: "viwid.event.Event"](self, event_type: type[TEvent], func: _TEventHandler, *,
                                                  implements_default_behavior: bool = False,
                                                  preview: bool = False) -> None:
        """
        Listen for occurrences of a given event type. The given function will be called whenever an event of that type
        occurs on this widget, until you call :py:meth:`unlisten_event`. See also :py:class:`viwid.event.Event` for
        more details.

        :param event_type: The event type to listen for.
        :param func: The function to be called when an event of the given type occurs.
        :param implements_default_behavior: Whether this implements the default behavior of a widget. Widget
                                            implementations usually set this to :code:`True`, other leave it
                                            :code:`False`.
        :param preview: Whether to listen to the "preview" phase of event handling.
        """
        self.__event_handlers.append((event_type, bool(implements_default_behavior), bool(preview), func))

    def unlisten_event(self, func: _TEventHandler) -> None:
        """
        Stop listening for events. See :py:meth:`listen_event`.

        If the given function was registered more than once for event listening, it gets removed once. If it was not
        registered, `ValueError` gets raised.

        :param func: The function to stop listening with.
        """
        for i, (_1, _2, _3, func_) in enumerate(self.__event_handlers):
            if func_ == func:
                self.__event_handlers.pop(i)
                return
        raise ValueError(f"not a listening event handler: {func!r}")

    def repaint(self) -> None:
        """
        Called from outside (mostly by the infrastructure) in order to repaint this widget.

        Widget implementations do not override this method but :py:meth:`_paint`!
        """
        if not (self.is_materialized and self.is_visible):
            return

        self.__inner_canvas.fill(self._style())
        self._paint(self.__inner_canvas)

    def bring_into_view(self) -> None:
        """
        Try as good as possible to bring this widget actually into view, e.g. let scrollable areas move to the right
        offset in order to make this widget appear.
        """
        if self.parent:
            self.parent._bring_child_into_view(self)

    @property
    def screen_layer(self) -> "viwid.app.screen.ScreenLayer":
        """
        The screen layer that (directly or indirectly) hosts this widget.
        """
        return self.__screen_layer

    @property
    def position(self) -> viwid.Point:
        """
        The current position of this widget inside the coordinate space of the parent widget's surface.

        The position and :py:attr:`size` are usually set by the parent's :py:class:`viwid.layout.Layout`; eventually by
        :py:meth:`align`.

        For screen coordinates, see :py:func:`viwid.app.screen.translate_coordinates_from_root` and
        :py:func:`viwid.app.screen.translate_coordinates_to_root`.
        """
        return self.__position

    @property
    def size(self) -> viwid.Size:
        """
        The current size of this widget.

        The :py:attr:`position` and size are usually set by the parent's :py:class:`viwid.layout.Layout`; eventually by
        :py:meth:`align`.

        Assuming the screen is large enough and the layout has typical behavior, this size is at least as large as the
        size demand of this widget (see :py:meth:`width_demand` and :py:meth:`height_demand`); maybe larger.

        For screen coordinates, see :py:func:`viwid.app.screen.translate_coordinates_from_root` and
        :py:func:`viwid.app.screen.translate_coordinates_to_root`.
        """
        return self.__size

    @property
    def rectangle(self) -> viwid.Rectangle:
        """
        The rectangle with the widget's :py:attr:`position` and :py:attr:`size`.
        """
        return self.__rectangle

    def do_materialization(self, application_manager: "viwid.app.manager.ApplicationManager",
                           screen_layer: "viwid.app.screen.ScreenLayer", parent: "Widget|None",
                           layer_style: "viwid.styling.Theme.Layer|None") -> None:
        """
        Materialize this widget. See also :py:meth:`do_dematerialization`.

        Used by :py:meth:`viwid.app.manager.ApplicationManager.materialize_widget`.

        Widget implementations do not override this method but :py:meth:`_materialize`!

        :param application_manager: The application manager.
        :param screen_layer: The screen layer.
        :param parent: The parent widget.
        :param layer_style: The layer style.
        """
        if not screen_layer:
            raise ValueError(f"screen layer {screen_layer!r} is invalid")
        if self.__screen_layer:
            raise RuntimeError(f"{self!r} is already materialized")

        self.__parent = parent
        self.__layer_style = layer_style
        self.__screen_layer = screen_layer
        self.__application_manager = application_manager

        self.__actual_properties_changed(skip_children=True)

        kwargs = self.__kwargs or {}
        for widget_type in type(self).mro():
            for key, value in widget_type.__dict__.items():
                if isinstance(value, (_Property, _ListProperty)) and key not in kwargs:
                    kwargs[key] = getattr(self, key)

        for key, value in list(kwargs.items()):
            setattr(self, key, value)

        for child in self._children:
            application_manager.materialize_widget(child, screen_layer, self, layer_style)

        if self.screen_layer.focused_widget is None:
            self.try_focus()

        self.listen_event(viwid.event.mouse.ClickEvent, self.__handle_mouse_clicked, implements_default_behavior=True)

        self._materialize()

    def do_dematerialization(self) -> None:
        """
        Dematerialize this widget. See also :py:meth:`do_materialization`.

        Used by :py:meth:`viwid.app.manager.ApplicationManager.dematerialize_widget`.

        Widget implementations do not override this method but :py:meth:`_dematerialize`!
        """
        self._dematerialize()

        self.unlisten_event(self.__handle_mouse_clicked)

        for child in self._children:
            self.application_manager.dematerialize_widget(child)
        self.__parent = None
        self.__layer_style = None
        self.__screen_layer = None
        self.__application_manager = None

    @property
    def outer_canvas(self) -> viwid.canvas.Canvas:
        """
        The widget's outer canvas.

        This canvas contains the visual representation of this widget together with its visible children.
        It is only readable and not the canvas where the widget would directly paint its own content on.
        """
        return self.__outer_canvas

    def try_focus(self) -> bool:
        """
        Try to focus this widget. Return whether it succeeded or not.
        """
        if self.is_focusable:
            self.screen_layer.focused_widget = self
            return True
        for child in self._children:
            if child.try_focus():
                return True
        return False

    def width_demand(self, *, minimal: bool) -> int:
        """
        Return the width demand for this widget. See also :py:meth:`height_demand`.

        This is called from outside, while widget implementations override :py:meth:`_compute_width` instead.

        It returns cached values. The cache gets reset by calling :py:meth:`_request_resize`.

        :param minimal: Whether to compute the minimal demand, which might be less comfortable to the user but still
                        enough to work properly.
        """
        if not self.is_visible:
            return 0
        result = self.__compute_width_cache[int(minimal)]
        if result is None:
            result = self.__compute_width_cache[int(minimal)] = self._compute_width(minimal)
        return max(self.minimal_size.width, result)

    def height_demand(self, width: int, *, minimal: bool) -> int:
        """
        Return the height demand for this widget for a given width. See also :py:meth:`width_demand`.

        This is called from outside, while widget implementations override :py:meth:`_compute_height` instead.

        It returns cached values. The cache gets reset by calling :py:meth:`_request_resize`.

        :param width: The available width.
        :param minimal: Whether to compute the minimal demand, which might be less comfortable to the user but still
                        enough to work properly.
        """
        if not self.is_visible:
            return 0
        result = self.__compute_height_cache[int(minimal)]
        if (result is None) or (result[0] != width):
            result = self.__compute_height_cache[int(minimal)] = width, self._compute_height(width, minimal)
        return max(self.minimal_size.height, result[1])

    def width_demand_for_height(self, height: int) -> int:
        """
        Return the minimal width demand for a given height.

        Note: This is not used by typical layouts' alignment routines. It is only a convenience method for particular
        cases. Internally it is solely based on :py:meth:`width_demand` and :py:meth:`height_demand` and cannot directly
        be overridden by widget implementations.

        :param height: The available height.
        """
        search_from_width = self.width_demand(minimal=True)
        search_to_width = self.width_demand(minimal=False)
        search_current = search_from_width
        while True:
            height_for_current_width = self.height_demand(search_current, minimal=True)
            if search_to_width - search_from_width <= 1:
                return search_to_width
            if height_for_current_width <= height:
                search_to_width = search_current
            else:
                search_from_width = search_current
            search_current = (search_from_width + search_to_width) // 2

    def align(self, position: viwid.Point|None = None, size: viwid.Size|None = None, *,
              forcefully_apply_resizing_for: t.Iterable["Widget"] = ()):
        """
        Give the widget a position and a size.

        It also takes care of applying the layout to all child widgets if the size has been changed. This can
        recursively go down to the leaves of the widget tree.

        The parameter `forcefully_apply_resizing_for` can be used to forcefully recompute a widget's alignment somewhere
        inside that tree, even if its parent has not been resized. This is used whenever a widget calls
        :py:meth:`_request_resize`.

        :param position: The new widget position (in the coordinate space of its parent).
        :param size: The new widget size.
        :param forcefully_apply_resizing_for: Forcefully apply resizing for these widgets.
        """
        old_position, old_size = self.position, self.size
        position = old_position if position is None else position
        size = old_size if size is None else size
        self.__rectangle = viwid.Rectangle(position, size)

        if size != old_size:
            self.__inner_canvas.resize(size)

        if position != old_position:
            self.__position = position
            if self.__parent:
                self.__parent.__child_position_changed(self)
            self.__application_manager._handle_widget_position_changed(self)

        if (size != old_size) or self in forcefully_apply_resizing_for:
            self.__size = size
            self.__layout.apply(self._children, size, forcefully_apply_resizing_for=forcefully_apply_resizing_for)

            if size != old_size:
                self.__outer_canvas.resize(size)
                self.screen_layer.trigger_event(self, viwid.event.widget.ResizeEvent(), bubble_upwards=False)
                self.repaint()

    @property
    def cursor_position(self) -> viwid.Point|None:
        """
        The current keyboard cursor position of this widget, in the coordinate space of this widget.

        The cursor position has solely visual purposes and does not influence and behavior.
        """
        return self.__cursor

    def child_at_position(self, position: viwid.Point) -> "Widget|None":
        """
        Return the child widget at the given position in this widget's coordinate space (or none).

        See also :py:meth:`widget_at_position`.

        :param position: The position.
        """
        for child in self._children:
            if viwid.Rectangle(child.position, child.size).contains(position):
                return child

    def widget_at_position(self, position: viwid.Point) -> "Widget":
        """
        Return the widget at the given position in this widget's coordinate space (or none). This can be any descendant
        or itself.

        See also :py:meth:`child_at_position`.

        :param position: The position.
        """
        widget = self
        while True:
            child_widget = Widget.child_at_position(widget, position)

            if child_widget is None:
                return widget

            widget, position = child_widget, position.moved_by(-viwid.Offset(child_widget.position))

    def with_all_descendants(self) -> t.Iterable["viwid.widgets.widget.Widget"]:
        """
        Return an iterable with all descendants and this widget itself, with the leaves appearing at first.
        """
        for child_widget in self._children:
            for widget_ in child_widget.with_all_descendants():
                yield widget_
        yield self

    def _handle_event(self, event: viwid.event.Event, *, preview: bool) -> None:
        """
        Called by the infrastructure to let this widget handle an event. See :py:class:`viwid.event.Event`.

        :param event: The event to handle.
        :param preview: Whether to handle the "preview" phase of this event.
        """
        for default_implementations in (False, True):
            for event_type, implements_default_behavior, preview_, event_handler in tuple(self.__event_handlers):
                if event.is_handling_stopped:
                    break
                if (isinstance(event, event_type)
                        and implements_default_behavior == default_implementations and preview == preview_):
                    self.__handle_event__run_event_handler(event_handler, event)

    def _set_cursor_position(self, position: viwid.Point|None) -> None:
        """
        Set the keyboard cursor position.

        The cursor position has solely visual purposes and does not influence and behavior.

        :param position: The new cursor position.
        """
        self.__cursor = position
        if self.screen_layer:
            self.screen_layer._cursor_position_changed(self)

    def _request_resize(self) -> None:
        """
        Schedule this widget to be resized according to its current demand by the event loop as soon as possible.
        """
        self.__compute_width_cache = [None, None]
        self.__compute_height_cache = [None, None]
        if self.__application_manager:
            self.__application_manager.resize_widget_soon(self)
        if self.parent:
            self.parent._request_resize()

    def _request_repaint(self) -> None:
        """
        Schedule this widget to be repainted by the event loop as soon as possible.

        This will eventually call :py:meth:`repaint` when returned to the event loop. This is more efficient than
        directly call :py:meth:`repaint` in many cases, because redundant requests can get dropped.
        """
        if self.__application_manager:
            self.__application_manager.repaint_widget_soon(self)

    def _request_resize_and_repaint(self) -> None:
        """
        See :py:meth:`_request_resize` and :py:meth:`_request_repaint`.
        """
        self._request_resize()
        self._request_repaint()

    _is_activated: bool
    @Property(default=lambda: False)
    def _is_activated(self, _):
        """
        Whether this widget is in "activated" state.

        This is set by the widget implementation in particular situations (e.g. when the user has triggered some widget
        action) and automatically gets unset a fraction of a second later.

        While it is activated, it will be painted in a different representation.
        """
        if _:
            def deactivate():
                self._is_activated = False
            self.__application_manager.driver.event_loop.call_later(0.1, deactivate)
        self._request_repaint()

    @property
    def _layout(self) -> "viwid.layout.Layout":
        """
        The widget's layout.
        """
        return self.__layout

    def _materialize(self) -> None:
        """
        Called by the infrastructure just after this widget and all its descendants got materialized (by
        :py:meth:`do_materialization`).

        Widget implementations override this method in order to access some features as early as possible which require
        the widget to be materialized (like :py:attr:`text_measuring`) or to do things that explicitly need to get
        undone later (like listening for events or similar).

        See also :py:meth:`_dematerialize`.
        """

    def _dematerialize(self) -> None:
        """
        Called by the infrastructure just before this widget gets dematerialized.

        See also :py:meth:`_materialize`.
        """

    def _compute_width(self, minimal: bool) -> int:
        """
        Return the current width demand of this widget.

        Some widget implementations override this method (although usage of layouts is recommended instead), while other
        code should use :py:meth:`width_demand` instead.

        :param minimal: Whether to calculate the minimal demand or the preferred one for comfortable usage.
        """
        return self.__layout.compute_layout_width(self._children, minimal)

    def _compute_height(self, width: int, minimal: bool) -> int:
        """
        Return the current height demand of this widget for a given width.

        Some widget implementations override this method (although usage of layouts is recommended instead), while other
        code should use :py:meth:`height_demand` instead.

        :param width: The available width.
        :param minimal: Whether to calculate the minimal demand or the preferred one for comfortable usage.
        """
        return self.__layout.compute_layout_height(self._children, width, minimal)

    def _set_class_style_name(self, class_style_name: str) -> None:
        """
        Set the class style name to use for this widget. One of the attribute names in
        :py:class:`viwid.styling.Theme.Layer`.

        :param class_style_name: The class style name.
        """
        if self.__class_style_name != class_style_name:
            self.__class_style_name = class_style_name
            self._request_repaint()

    def _style(self, class_style: "viwid.styling.Theme.Layer.Class|str|None" = None
               ) -> "viwid.styling.Theme.Layer.Class.Style":
        """
        The style for this widget in its current state, either for its own class style (see
        :py:meth:`_set_class_style_name`) or another one.

        :param class_style: The class style to use.
        """
        if class_style is None:
            class_style = self.class_style_name
        if isinstance(class_style, str):
            class_style = getattr(self.layer_style, class_style)

        w = self
        is_focused = False
        while w:
            is_focused = is_focused or w is self.screen_layer.focused_widget
            w = w.parent

        w = self
        is_hovered = False
        while w:
            is_hovered = is_hovered or w is self.__application_manager.hovered_widget
            w = w.parent

        w = self
        is_activated = False
        while w:
            is_activated = is_activated or w._is_activated
            w = w.parent

        if not self.is_actually_enabled:
            atom_name = "disabled"
        elif is_activated:
            atom_name = "activated"
        elif is_hovered:
            atom_name = "hovered"
        elif is_focused:
            atom_name = "focused"
        else:
            atom_name = "normal"
        return getattr(class_style, atom_name)

    @property
    def _text_measuring(self) -> "viwid.text.TextMeasuring":
        """
        Text measuring and rendering facility.

        Can only be used once the widget is materialized (see :py:attr:`is_materialized`).
        """
        return self.__application_manager.text_measuring

    def _paint(self, canvas: "viwid.canvas.ModifiableCanvas") -> None:
        """
        Called by the widget infrastructure in order to get this widget repainted according to its current state.

        Widget implementations override this method. It is not directly called from outside. See :py:meth:`repaint`.

        :param canvas: The canvas to paint on.
        """

    def _bring_child_into_view(self, widget: "Widget") -> None:
        """
        Try to bring a child widget into view.

        Widget implementations override this method, e.g. scrollable areas can change its offsets in order to move the
        given child into the viewport. It is not directly called from outside. See :py:meth:`bring_into_view`.

        :param widget: The child widget to bring into view.
        """
        if self.parent:
            self.parent._bring_child_into_view(widget)

    def __child_added(self, index: int, child: "Widget") -> None:
        if self.__application_manager:
            self.__application_manager.materialize_widget(child, self.__screen_layer, self, self.__layer_style)
        self.__outer_canvas.insert_source_canvas(index+1, child.outer_canvas, position=child.position)
        self._request_resize()

    def __child_removed(self, index: int, child: "Widget") -> None:
        if self.__application_manager:
           self.application_manager.dematerialize_widget(child)
        self.__outer_canvas.remove_source_canvas(index+1)
        self._request_resize()

    @ListProperty(__child_added, __child_removed)
    def _children(self) -> list:
        """
        Child widgets.
        """

    def __child_position_changed(self, child: "Widget") -> None:
        self.__outer_canvas.set_source_canvas_position(child.outer_canvas, child.position)

    def __actual_properties_changed(self, *, skip_children: bool = False) -> None:
        if not self.is_materialized:
            return

        self.__is_actually_enabled = self.is_enabled and (self.__parent.__is_actually_enabled
                                                          if self.__parent else True)
        self.__is_actually_visible = self.is_visible and (self.__parent.__is_actually_visible
                                                          if self.__parent else True)
        if not skip_children:
            for child in self._children:
                child.__actual_properties_changed()

    def __handle_event__run_event_handler(self, event_handler: _TEventHandler, event: viwid.event.Event) -> None:
        if len([param for param in inspect.signature(event_handler).parameters.values()
                if param.kind in [inspect.Parameter.POSITIONAL_OR_KEYWORD]]) < 1:
            event_handler_ = event_handler
            event_handler = lambda _: event_handler_()

        event_handler(event)

    def __handle_mouse_clicked(self, event: viwid.event.mouse.ClickEvent) -> None:
        if self.is_focusable:
            self.try_focus()
