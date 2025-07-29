#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
Applications managers.

See :py:class:`ApplicationManager`.
"""
import contextlib
import typing as t

import viwid.app
import viwid.canvas
import viwid.drivers
import viwid.event
import viwid.app.screen
import viwid.styling
import viwid.text


class ApplicationManager:
    """
    Once the viwid environment gets initialized in your process, there is one application manager. It manages all
    applications that are running in the current process.

    All running applications share a single terminal, so as soon as there is more than one application, it will provide
    ways to the user to switch between them.
    """

    def __init__(self, driver: "viwid.drivers.Driver", theme: "viwid.styling.Theme|None" = None):
        """
        Usually you do not create instances directly. See :py:attr:`viwid.drivers.Driver.apps`.

        :param driver: The driver to use.
        :param theme: The application theme used for applications. If unspecified, uses the default theme.
        """
        self.__driver = driver
        self.__theme = theme or viwid.styling.default_theme()
        self.__apps = []
        self.__active_app = None
        self.__canvas = viwid.canvas.ComposingCanvas()
        self.__terminal_size = None
        self.__measure_character_width__cache = {}
        self.__text_measuring = viwid.text.TextMeasuring(self.measure_character_width)
        self.__mouse_buttons_down = []
        self.__mouse_position = viwid.Point(-1, -1)
        self.__mouse_button_pressed_at_screen_position = None
        self.__mouse_grabbed_widget = None
        self.__hovered_widget = None
        self.__focused_widget = None
        self.__resize_soon_widgets = set()
        self.__repaint_soon_widgets = set()
        self.__requests_pending = False
        self.__active_app_canvas_offset = viwid.Offset.NULL
        self.__app_switcher_widget = viwid.widgets.box.Box()
        self.__app_switcher_widget.listen_event(viwid.event.mouse.ClickEvent, self.__handle_app_switcher_mouse_clicked)
        self.__is_entered = False
        self.__materialize_on_enter = []
        self.__last_cursor_position = None

    def __enter__(self):
        self.__is_entered = True
        self.__terminal_size = self.driver.determine_terminal_size()
        for widget, screen_layer, parent, layer_style in self.__materialize_on_enter:
            if not widget.is_materialized and (parent is None or parent.is_materialized):
                widget.do_materialization(self, screen_layer, parent, layer_style)
        self.__materialize_on_enter = None
        self.__handle_terminal_resized()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__is_entered = False
        self.__materialize_on_enter = []

        if self.__app_switcher_widget.is_materialized:
            self.dematerialize_widget(self.__app_switcher_widget)

    @property
    def driver(self) -> "viwid.drivers.Driver":
        """
        The driver used by this application manager.
        """
        return self.__driver

    @property
    def terminal_size(self) -> "viwid.Size":
        """
        The terminal size.

        Note that the size of an application's screen can be different.
        See :py:attr:`viwid.app.Application.screen_size`.
        """
        if self.__terminal_size is None:
            raise RuntimeError("must not be accessed that early")
        return self.__terminal_size

    @property
    def all_running(self) -> t.Sequence["viwid.app.Application"]:
        """
        All running applications.
        """
        return tuple(self.__apps)

    @property
    def output_canvas(self) -> "viwid.canvas.Canvas":
        """
        The application manager's output canvas.

        Usually this is an exact copy of the active application's output canvas, but it can also contain additional
        things, like an application chooser (when more than one application is running).

        This is what a driver would paint to the screen.
        """
        return self.__canvas

    @property
    def hovered_widget(self) -> "viwid.widgets.widget.Widget|None":
        """
        The widget that is currently hovered, i.e. touched by the mouse cursor.

        Note that only some widgets can be hovered. See :py:attr:`viwid.widgets.widget.Widget.is_hoverable` and
        :py:attr:`viwid.widgets.widget.Widget.is_focusable`.
        """
        if self.__hovered_widget and not self.__hovered_widget.is_materialized:
            self.__hovered_widget = None
        return self.__hovered_widget

    def start_new_application(self, *, activate: bool = True, stop_when_last_screen_layer_closed: bool = True,
                              theme: "viwid.styling.Theme|None" = None) -> "viwid.app.Application":
        """
        Start a new application.

        See also :py:meth:`stop_application`.

        :param activate: Whether to directly activate this application. This only makes a difference when you start more
                         than one application in parallel in your process.
        :param stop_when_last_screen_layer_closed: Automatically stop this application when the last screen layer (this
                                                   usually means: the last window) got closed.
        :param theme: The application theme to use. If not specified, it uses the application theme that was set up
                      for this application manager.
        """
        app = viwid.app.Application(self.__driver, self, stop_when_last_screen_layer_closed, theme or self.__theme)
        app._screen_resized(self.__terminal_size)

        self.__apps.append(app)

        if activate:
            self.activate_application(app)
        else:
            self.__handle_applications_changed()

        return app

    def stop_application(self, app: "viwid.app.Application") -> None:
        """
        Stop an application.

        If started with default parameters, this will automatically happen when the last screen layer got closed.

        :param app: The application to stop.
        """
        self.__apps.remove(app)
        self.__handle_applications_changed()

    def measure_character_width(self, char: str) -> int:
        """
        Measure the width on screen for a string that represents a single grapheme.

        You should not use this directly. Use :py:attr:`text_measuring` instead.
        See :py:meth:`viwid.drivers.Driver.measure_character_width`.

        :param char: The string to measure.
        """
        if len(char) == 1 and ord(char) < 256 and char not in "\t":
            return 1

        if (result := self.__measure_character_width__cache.get(char)) is None:
            result = self.__measure_character_width__cache[char] = self.driver.measure_character_width(char)
        return result

    @property
    def text_measuring(self) -> "viwid.text.TextMeasuring":
        """
        Text measuring and rendering facility.
        """
        return self.__text_measuring

    @property
    def active_application(self) -> "viwid.app.Application|None":
        """
        The application that is currently active, i.e. visible on the screen and receiving user input.

        When more than one application is running in parallel in your process, only one of them will be active at any
        point in time. There will be an application switcher presented to the user as well.
        """
        return self.__active_app

    def activate_application(self, app: "viwid.app.Application") -> None:
        """
        Activate an application.

        See :py:attr:`active_application`.

        :param app: The application to activate.
        """
        if app is self.__active_app:
            return
        self.__active_app = app
        self.__handle_applications_changed()
        self._cursor_position_changed()

    def materialize_widget(self, widget: "viwid.widgets.widget.Widget", screen_layer: "viwid.app.screen.ScreenLayer",
                           parent: "viwid.widgets.widget.Widget|None",
                           layer_style: "viwid.styling.Theme.Layer|None") -> None:
        """
        Materialize a widget.

        If the widget already is materialized, this does nothing. If it is called before the viwid environment is up
        and running, the actual materialization will take place once the environment is up.

        Most of the time, this is completely handled by the infrastructure. You only need it in rather exotic cases.

        The materialization routine basically makes connects a widget to its outer environment and makes it able to
        interact with the outer world, like showing a visual representation on the screen and retrieving user input.
        Without being materialized, a widget is not much more than a data structure and solves no actual purpose.

        Typically, the infrastructure materializes the root widget for each screen layer. Each widget takes care of
        materializing its children (by calling this method again).

        See also :py:meth:`dematerialize_widget`.

        :param widget: The widget to _materialize.
        :param screen_layer: The screen layer to assign to this widget.
        :param parent: The widget's parent widget.
        :param layer_style: The layer style to use for this widget.
        """
        if widget.is_materialized or (parent is not None and not parent.is_materialized):
            return
        if self.__is_entered:
            widget.do_materialization(self, screen_layer, parent, layer_style)
        else:
            self.__materialize_on_enter.append((widget, screen_layer, parent, layer_style))

    def dematerialize_widget(self, widget: "viwid.widgets.widget.Widget") -> None:
        """
        Dematerialize a widget.

        Most of the time, this is completely handled by the infrastructure. You only need it in rather exotic cases.

        See also :py:meth:`materialize_widget`.

        :param widget: The widget to _dematerialize.
        """
        if self.__is_entered:
            if widget.is_materialized:
                widget.do_dematerialization()
        else:
            for i, (widget_, *_) in reversed(tuple(enumerate(self.__materialize_on_enter))):
                if widget_ is widget:
                    self.__materialize_on_enter.pop(i)

    def handle_event_internals(self, event_internals: t.Sequence["viwid.drivers.EventInternals.EventInternal"]) -> None:
        """
        Handle event internals (see :py:class:`viwid.drivers.EventInternals`) by translating them to real events
        (:py:class:`viwid.event.Event`) and trigger them.

        This will usually hand over the generated events to the current application's topmost screen layer (for keyboard
        events) or something similar for other events. Some events do not end up in the current application at all, e.g.
        if they were related to the application switcher (that is visible when more than one application is running in
        parallel in your process). Apart from these corner cases, this method will basically call
        :py:meth:`viwid.app.screen.ScreenLayer.trigger_event` with a translated event for each event internal.

        :param event_internals: The event internals that occurred recently.
        """
        active_application = self.active_application

        for event_internal in event_internals:
            if isinstance(event_internal, viwid.drivers.EventInternals.KeyboardKeyPressedEventInternal):
                if event_internal.with_ctrl and event_internal.key_code in (
                        viwid.event.keyboard.KeyCodes.ARROW_LEFT,
                        viwid.event.keyboard.KeyCodes.ARROW_RIGHT):
                    if len(self.__apps) > 1:
                        direction = -1 if (event_internal.key_code == viwid.event.keyboard.KeyCodes.ARROW_LEFT) else 1
                        self.activate_application(self.__apps[(self.__apps.index(self.__active_app) + direction)
                                                              % len(self.__apps)])
                elif not event_internal.with_ctrl and event_internal.key_code == viwid.event.keyboard.KeyCodes.TAB:
                    self.__handle_event_internals__tab_key(event_internal.with_shift)

                elif active_application and (topmost_screen_layer := active_application.topmost_layer):
                    if focused_widget := topmost_screen_layer.focused_widget:
                        topmost_screen_layer.trigger_event(focused_widget, viwid.event.keyboard.KeyPressEvent(
                                viwid.event.keyboard.KeyCombination.by_code(
                                    event_internal.key_code, with_shift=event_internal.with_shift,
                                    with_alt=event_internal.with_alt, with_ctrl=event_internal.with_ctrl)))

            elif isinstance(event_internal, (viwid.drivers.EventInternals.MouseButtonDownEventInternal,
                                             viwid.drivers.EventInternals.MouseButtonUpEventInternal,
                                             viwid.drivers.EventInternals.MouseScrollEventInternal,
                                             viwid.drivers.EventInternals.MouseMoveEventInternal)):
                mouse_position = event_internal.mouse_position.moved_by(-self.__active_app_canvas_offset)
                is_real = True
                if self.__mouse_grabbed_widget:
                    touched_widget = self.__mouse_grabbed_widget
                else:
                    touched_widget = None
                    if len(self.__apps) > 1 and mouse_position.y == -1:
                        mouse_position = mouse_position.moved_by(0, 1)
                        touched_widget = self.__app_switcher_widget.child_at_position(mouse_position)
                        is_real = False
                    elif active_application and (layer := active_application.layer_at_position(mouse_position)):
                        touched_widget = layer.widget.widget_at_position(mouse_position)
                if isinstance(event_internal, (viwid.drivers.EventInternals.MouseButtonDownEventInternal,
                                               viwid.drivers.EventInternals.MouseButtonUpEventInternal)):
                    is_down = isinstance(event_internal, viwid.drivers.EventInternals.MouseButtonDownEventInternal)
                    self.__mouse_buttons_down = self.__mouse_buttons_down + (
                                event_internal.button + 1 - len(self.__mouse_buttons_down)) * [False]
                    if button_state_changed := self.__mouse_buttons_down[event_internal.button] != is_down:
                        self.__mouse_buttons_down[event_internal.button] = is_down
                if touched_widget and active_application:
                    if isinstance(event_internal, (viwid.drivers.EventInternals.MouseButtonDownEventInternal,
                                                   viwid.drivers.EventInternals.MouseButtonUpEventInternal)):
                        if touched_widget.screen_layer is not active_application.topmost_layer and is_real:
                            active_application.set_layer_index(touched_widget.screen_layer, None)
                        if button_state_changed:
                            self.__mouse_buttons_down[event_internal.button] = is_down
                            event_type = (viwid.event.mouse.ButtonDownEvent
                                          if is_down else viwid.event.mouse.ButtonUpEvent)
                            touched_widget.screen_layer.trigger_event(touched_widget, event := event_type(
                                self.__grab_mouse, touched_widget, mouse_position, self.__mouse_buttons_down,
                                event_internal.button, event_internal.with_shift, event_internal.with_alt,
                                event_internal.with_ctrl))
                            if not event.is_handling_stopped:
                                if is_down:
                                    self.__mouse_button_pressed_at_screen_position = mouse_position
                                else:
                                    if self.__mouse_button_pressed_at_screen_position == mouse_position:
                                        self.__mouse_button_pressed_at_screen_position = None
                                        touched_widget.screen_layer.trigger_event(
                                            touched_widget, viwid.event.mouse.ClickEvent(
                                                self.__grab_mouse, touched_widget, mouse_position,
                                                self.__mouse_buttons_down, event_internal.button,
                                                event_internal.with_shift, event_internal.with_alt,
                                                event_internal.with_ctrl))

                    elif isinstance(event_internal, viwid.drivers.EventInternals.MouseScrollEventInternal):
                        touched_widget.screen_layer.trigger_event(touched_widget, viwid.event.mouse.ScrollEvent(
                            self.__grab_mouse, touched_widget, mouse_position, self.__mouse_buttons_down,
                            event_internal.direction, event_internal.with_shift, event_internal.with_alt,
                            event_internal.with_ctrl))
                    elif isinstance(event_internal, viwid.drivers.EventInternals.MouseMoveEventInternal):
                        self.__mouse_button_pressed_at_screen_position = None
                        if self.__mouse_position != mouse_position:
                            touched_widget.screen_layer.trigger_event(touched_widget, viwid.event.mouse.MoveEvent(
                                self.__grab_mouse, touched_widget, mouse_position,
                                self.__mouse_buttons_down, event_internal.with_shift, event_internal.with_alt,
                                event_internal.with_ctrl))

            elif isinstance(event_internal, viwid.drivers.EventInternals.ScreenResizedEventInternal):
                self.__handle_terminal_resized()

            else:
                raise ValueError(f"invalid event internal {event_internal!r}")

    def repaint_widget_soon(self, widget: "viwid.widgets.widget.Widget") -> None:
        """
        Schedule a widget to be repainted by the event loop as soon as possible.

        :param widget: The widget to repaint.
        """
        self.__repaint_soon_widgets.add(widget)
        self.__execute_requests_soon()

    def resize_widget_soon(self, widget: "viwid.widgets.widget.Widget") -> None:
        """
        Schedule a widget to be resized (according to its new demand) by the event loop as soon as possible.

        Internally this will trigger the root widgets' layout routine using its `forcefully_apply_resizing_for`
        parameter (for more details, see :py:meth:`viwid.layout.Layout.apply`).

        :param widget: The widget to resize.
        """
        self.__resize_soon_widgets.add(widget)
        self.__execute_requests_soon()

    def _widget_focused(self) -> None:
        """
        Called by the infrastructure when there is (potentially) another widget focused now.
        """
        focused_widget = self.__active_app.focused_widget if self.__active_app else None
        old_focused_widget, self.__focused_widget = self.__focused_widget, focused_widget

        if focused_widget:
            focused_widget._request_repaint()
        if old_focused_widget:
            old_focused_widget._request_repaint()

        self._cursor_position_changed()

    def _handle_widget_position_changed(self, widget: "viwid.widgets.widget.Widget") -> None:
        """
        Called by the widget infrastructure when a widget's position has been changed (typically by its parent widget's
        layout).

        :param widget: The widget.
        """
        self._cursor_position_changed()

    def _set_hovered_widget(self, widget: "viwid.widgets.widget.Widget|None"):
        """
        Called by the infrastructure when there is (potentially) another widget hovered now.

        :param widget: The widget.
        """
        while widget and not widget.is_focusable and not widget.is_hoverable:
            widget = widget.parent

        old_hovered_widget, self.__hovered_widget = self.__hovered_widget, widget

        repaint_widgets = []
        if widget:
            repaint_widgets.append(widget)
        if old_hovered_widget:
            repaint_widgets.append(old_hovered_widget)

        while repaint_widgets:
            repaint_widget = repaint_widgets.pop()
            repaint_widget._request_repaint()
            repaint_widgets += repaint_widget._children

    def _cursor_position_changed(self):
        """
        Called by the infrastructure when the keyboard cursor position (see
        :py:class:`viwid.app.Application.cursor_position`) has been changed for any reason (e.g. the current widget
        changed the cursor position or another widget got the focus).
        """
        cursor_position = None
        if self.__active_app and (cursor_position := self.__active_app.cursor_position):
            cursor_position = cursor_position.moved_by(self.__active_app_canvas_offset)

        if self.__last_cursor_position != cursor_position:
            self.__last_cursor_position = cursor_position
            self.driver.set_cursor(cursor_position)

    @contextlib.contextmanager
    def __grab_mouse(self, widget):
        if self.__mouse_grabbed_widget:
            raise RuntimeError(f"mouse is already grabbed by {self.__mouse_grabbed_widget!r}")
        self.__mouse_grabbed_widget = widget
        try:
            yield
        finally:
            self.__mouse_grabbed_widget = None

    def __handle_terminal_resized(self) -> None:
        self.__terminal_size = self.driver.determine_terminal_size()
        self.__canvas.resize(self.__terminal_size)
        if self.__app_switcher_widget.is_materialized:
            self.__app_switcher_widget.align(viwid.Point.ORIGIN, viwid.Size(self.__terminal_size.width, 1))
        self.__handle_applications_changed()

    def __handle_event_internals__tab_key(self, reverse: bool) -> None:
        if not self.__active_app:
            return

        focus_next = False

        if widget := self.__active_app.focused_widget:
            screen_layer = widget.screen_layer
        else:
            screen_layer = self.__active_app.topmost_layer
            focus_next = True
        screen_layers = tuple(reversed(self.__active_app.modality_group_for_layer(screen_layer)))

        for screen_layer in screen_layers:
            all_screen_widgets = screen_layer.widget.with_all_descendants()
            if reverse:
                all_screen_widgets = reversed(tuple(all_screen_widgets))

            for widget_ in all_screen_widgets:
                if focus_next and widget_.is_focusable and widget_.is_actually_enabled and widget_.is_actually_visible:
                    if screen_layer is not self.__active_app.topmost_layer:
                        self.__active_app.set_layer_index(screen_layer, None)
                    if widget_.try_focus():
                        widget_.bring_into_view()
                        return
                elif widget_ is widget:
                    focus_next = True

    def __handle_applications_changed(self):
        active_application = self.__active_app
        if active_application not in self.__apps:
            active_application = None
        if active_application is None and len(self.__apps) > 0:
            active_application = self.__apps[-1]
        if active_application != self.__active_app:
            return self.activate_application(active_application)

        while len(self.__canvas.source_canvases) > 0:
            self.__canvas.remove_source_canvas(0)

        if len(self.__apps) == 1:
            self.__active_app_canvas_offset = viwid.Offset.NULL
            app = self.__apps[0]
            app._screen_resized(self.__terminal_size)
            self.__canvas.insert_source_canvas(None, app.output_canvas, position=viwid.Point.ORIGIN)

        elif len(self.__apps) > 1:
            self.__active_app_canvas_offset = viwid.Offset(0, 1)
            if not self.__app_switcher_widget.is_materialized:
                self.materialize_widget(self.__app_switcher_widget,
                                        viwid.app.screen.ScreenLayer(self, None, self.__app_switcher_widget, False),
                                        None, self.__theme.app_chooser)

            self.__app_switcher_widget.children = [*[
                viwid.widgets.button.Button(text=" # ", is_focusable=False,  # misuse of 'tiny_control' here
                                            class_style_name="tiny_control" if (_ is self.__active_app) else "control")
                for _ in self.__apps], viwid.widgets.label.Label(text=" [Ctrl] + [⇄]")]

            app_rect = viwid.Rectangle(viwid.Point(0, 1),
                                       self.__terminal_size.with_height(self.__terminal_size.height - 1))

            self.__active_app._screen_resized(app_rect.size)

            self.__canvas.insert_source_canvas(None, self.__app_switcher_widget.outer_canvas, position=viwid.Point(0, 0))

            if active_app := self.__active_app:
                self.__canvas.insert_source_canvas(None, active_app.output_canvas, position=viwid.Point(0, 1))

        self._widget_focused()

    def __execute_requests_soon(self):
        if not self.__requests_pending:
            # noinspection PyTypeChecker
            self.__driver.event_loop.call_soon(self.__requests_queue__do_requests)
            self.__requests_pending = True

    def __requests_queue__do_requests(self):
        self.__requests_pending = False
        self.__resize_soon_widgets, resize_soon_widgets = set(), self.__resize_soon_widgets
        self.__repaint_soon_widgets, repaint_soon_widgets = set(), self.__repaint_soon_widgets

        for app in self.__apps:
            app._realign_widgets(resize_soon_widgets)

        if self.__app_switcher_widget.is_materialized:
            self.__app_switcher_widget.align(viwid.Point.ORIGIN, viwid.Size(self.__terminal_size.width, 1),
                                             forcefully_apply_resizing_for=resize_soon_widgets)

        for widget in repaint_soon_widgets:
            widget.repaint()

    def __handle_app_switcher_mouse_clicked(self, event: viwid.event.mouse.ButtonDownEvent):
        if isinstance(event.touched_widget, viwid.widgets.button.Button):
            app_index = event.touched_widget.parent.children.index(event.touched_widget)
            self.activate_application(self.__apps[app_index])
