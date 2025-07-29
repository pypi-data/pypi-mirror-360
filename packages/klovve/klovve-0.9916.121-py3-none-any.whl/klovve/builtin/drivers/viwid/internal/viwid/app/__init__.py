#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
Applications.

See :py:class:`Application`.
"""
import typing as t

import viwid.app.manager
import viwid.canvas
import viwid.drivers
import viwid.layout
import viwid.app.screen
import viwid.styling


class Application:
    """
    One viwid application.

    For application developers, the most relevant method is :py:class:`add_layer_for_window`. Many things are mostly
    for viwid's internal management and rarely used outside.
    """

    def __init__(self, driver: "viwid.drivers.Driver", application_manager: "viwid.app.manager.ApplicationManager",
                 stop_when_last_screen_layer_closed: bool, theme: "viwid.styling.Theme"):
        """
        Usually you do not create instances directly. See
        :py:meth:`viwid.app.manager.ApplicationManager.start_new_application`.

        :param driver: The driver to use.
        :param application_manager: The application manager.
        :param stop_when_last_screen_layer_closed: Whether to stop this application automatically when the last screen
                                                   layer gets closed.
        :param theme: The application theme.
        """
        self.__driver = driver
        self.__application_manager = application_manager
        self.__stop_when_last_screen_layer_closed = stop_when_last_screen_layer_closed
        self.__theme = theme
        self.__size = viwid.Size.NULL
        self.__layers = []
        self.__output_canvas = viwid.canvas.ComposingCanvas()
        self.__focused_widget = None

    @property
    def focused_widget(self) -> "viwid.widgets.widget.Widget|None":
        """
        The application's focused widget.
        """
        topmost_layer = self.topmost_layer
        return topmost_layer.focused_widget if topmost_layer else None

    @property
    def cursor_position(self) -> viwid.Point|None:
        """
        The application's keyboard cursor position.

        The cursor position has solely visual purposes and does not influence and behavior.
        """
        if self.topmost_layer:
            return self.topmost_layer.cursor_position

    @property
    def driver(self) -> "viwid.drivers.Driver":
        """
        The driver that hosts this application.
        """
        return self.__driver

    @property
    def output_canvas(self) -> "viwid.canvas.Canvas":
        """
        The application output canvas.

        This is what a driver would eventually paint to the screen (unless another application is the active one).
        """
        return self.__output_canvas

    @property
    def screen_size(self) -> viwid.Size:
        """
        The application's screen size.

        This is not always the same as the physical terminal size, e.g. when the application manager uses parts of the
        screen for other purposes (like an application switcher).
        """
        return self.__size

    @property
    def manager(self) -> "viwid.app.manager.ApplicationManager":
        """
        The application manager.
        """
        return self.__application_manager

    @property
    def layers(self) -> t.Sequence["viwid.app.screen.ScreenLayer"]:
        """
        This application's screen layers.

        There is usually one screen layer for each window or popup.

        A screen layer index (as accepted by some parts of this class API) is a position in this list. This position
        also implies their z-position: The screen layer with the highest index is in front of all the others.
        """
        return tuple(self.__layers)

    @property
    def topmost_layer(self) -> "viwid.app.screen.ScreenLayer|None":
        """
        The topmost screen layer (or `None` if this application has no screen layers).
        """
        if any(self.__layers):
            return self.__layers[-1]

    def add_layer(self, widget: "viwid.widgets.widget.Widget", *, index: int|None = None,
                  layout: viwid.layout.Layout|None=None, is_modal: bool = True,
                  layer_style_name: str = "main") -> "viwid.app.screen.ScreenLayer":
        """
        Add a screen layer to this application.

        In order to add a window, use :py:meth:`add_layer_for_window` instead.

        See also :py:meth:`remove_layer`.

        :param widget: The root widget to show in this layer.
        :param index: The screen layer index. If unspecified, put it to the end (in front of all others).
        :param layout: The layout to apply in order to align the root widget on the screen layer.
        :param is_modal: Whether this screen layer is modal. The user can then not reach any screen layers below.
        :param layer_style_name: The layer style name. One of the attribute names in :py:class:`viwid.styling.Theme`.
        """
        layout = layout or viwid.app.screen.Layout()
        index = len(self.__layers) if index is None else index

        widget = viwid.widgets.box._RootBox(children=(widget,), layout=layout)
        self.__layers.insert(index, screen_layer := viwid.app.screen.ScreenLayer(self.__application_manager, self,
                                                                                 widget, is_modal))
        self.__application_manager.materialize_widget(widget, screen_layer, None,
                                                      getattr(self.__theme, layer_style_name))

        canvas_index = self.__layer_index_to_canvas_index(index)
        self.__output_canvas.insert_source_canvas(canvas_index, widget.outer_canvas, position=widget.position)
        if is_modal:
            self.__output_canvas.insert_source_canvas(canvas_index,
                                                      viwid.canvas.BlankSemiOpaqueAreaCanvas(size=self.__size))

        widget.align(viwid.Point.ORIGIN, self.screen_size)
        self.__widget_focused()

        return screen_layer

    def add_layer_for_window(self, window: "viwid.widgets.window.Window", *,
                             index: int|None = None, is_modal: bool = True,
                             layer_style_name: str = "main") -> "viwid.app.screen.ScreenLayer":
        """
        Add a screen layer for a window.

        See also :py:meth:`remove_layer`.

        :param window: The window to show in this layer.
        :param index: The screen layer index. If unspecified, put it to the end (in front of all others).
        :param is_modal: Whether this screen layer is modal. The user can then not reach any screen layers below.
        :param layer_style_name: The layer style name. One of the attribute names in :py:class:`viwid.styling.Theme`.
        """
        return self.add_layer(window, index=index, layout=viwid.app.screen.Layout(only_initially=True),
                              is_modal=is_modal, layer_style_name=layer_style_name)

    def remove_layer(self, screen_layer: "viwid.app.screen.ScreenLayer|int") -> None:
        """
        Remove a screen layer.

        :param screen_layer: The screen layer to remove. Can be an index or a screen layer instance.
        """
        if isinstance(screen_layer, viwid.app.screen.ScreenLayer):
            index = self.__layers.index(screen_layer)
        else:
            index = screen_layer
            screen_layer = self.__layers[index]
        canvas_index = self.__layer_index_to_canvas_index(index)
        self.__layers.pop(index)

        source_canvases = self.__output_canvas.source_canvases
        while canvas_index < len(source_canvases) and isinstance(source_canvases[canvas_index],
                                                                 viwid.canvas.BlankSemiOpaqueAreaCanvas):
            canvas_index += 1

        if screen_layer.is_modal:
            blank_area_canvas_index = canvas_index
            source_canvases = self.__output_canvas.source_canvases
            while not isinstance(source_canvases[blank_area_canvas_index], viwid.canvas.BlankSemiOpaqueAreaCanvas):
                blank_area_canvas_index -= 1
            self.__output_canvas.remove_source_canvas(blank_area_canvas_index)
            canvas_index -= 1

        widget_canvas_index = canvas_index

        self.__output_canvas.remove_source_canvas(widget_canvas_index)

        if screen_layer.widget.is_materialized:
            self.manager.dematerialize_widget(screen_layer.widget)
        self.__widget_focused()

        if self.__stop_when_last_screen_layer_closed and len(self.__layers) == 0:
            self.__application_manager.stop_application(self)

    def set_layer_index(self, screen_layer: "viwid.app.screen.ScreenLayer|int", to_index: int|None) -> None:
        """
        Move a screen layer to a new screen layer index. This changes to order of the screen layers on the z-axis.
        You can move a screen layer only within its modality context, so you can never make a screen layer accessible
        though it was hidden behind a modal one, or the other way around.

        :param screen_layer: The screen layer to move. Can be an index or a screen layer instance.
        :param to_index: The new screen layer index.
        """
        if to_index is None:
            to_index = len(self.__layers) - 1

        if isinstance(screen_layer, viwid.app.screen.ScreenLayer):
            index = self.__layers.index(screen_layer)
        else:
            index = screen_layer
        if index == to_index:
            return

        screen_layer = self.__layers.pop(index)
        self.__layers.insert(to_index, screen_layer)

        canvas_index = self.__layer_index_to_canvas_index(index)
        canvas_to_index = self.__layer_index_to_canvas_index(to_index)

        source_canvases = self.__output_canvas.source_canvases
        while canvas_index < len(source_canvases) and isinstance(source_canvases[canvas_index],
                                                                 viwid.canvas.BlankSemiOpaqueAreaCanvas):
            canvas_index += 1
        while canvas_to_index < len(source_canvases) and isinstance(source_canvases[canvas_to_index],
                                                                    viwid.canvas.BlankSemiOpaqueAreaCanvas):
            canvas_to_index += 1
        for i in range(min(canvas_index, canvas_to_index), max(canvas_index, canvas_to_index)):
            if isinstance(source_canvases[i], viwid.canvas.BlankSemiOpaqueAreaCanvas):
                raise RuntimeError("screen layers must only be moved within the same modality context")

        self.__output_canvas.set_source_canvas_index(canvas_index, canvas_to_index)

        self.__widget_focused()

    def layer_at_position(self, position: viwid.Point) -> "viwid.app.screen.ScreenLayer|None":
        """
        Return the topmost screen layer of those which are not "empty" at the given screen position.

        :param position: The screen position.
        """
        i_canvas = len(self.__output_canvas.source_canvases)
        for layer in reversed(self.__layers):
            i_canvas -= 1
            if isinstance(self.__output_canvas.source_canvases[i_canvas], viwid.canvas.BlankSemiOpaqueAreaCanvas):
                break
            if len(layer.widget.children) > 0:
                widget = layer.widget.children[0]
                if viwid.Rectangle(widget.position, widget.size).contains(position):
                    return layer

    def modality_group_for_layer(
            self, screen_layer: "viwid.app.screen.ScreenLayer") -> t.Sequence["viwid.app.screen.ScreenLayer"]:
        """
        Return the modality group for a screen layer.

        This is the list of all screen layers (always including the given screen layer itself) in the same modality
        context, i.e. "with no modal screen layer between".

        :param screen_layer: The screen layer.
        """
        result = []

        source_canvases = self.__output_canvas.source_canvases
        index = self.__layers.index(screen_layer)
        canvas_index = self.__layer_index_to_canvas_index(index)
        if isinstance(source_canvases[canvas_index], viwid.canvas.BlankSemiOpaqueAreaCanvas):
            canvas_index += 1
        while canvas_index >= 0 and not isinstance(source_canvases[canvas_index],
                                                   viwid.canvas.BlankSemiOpaqueAreaCanvas):
            canvas_index -= 1
            index -= 1
        canvas_index += 1
        index += 1
        while canvas_index < len(source_canvases) and not isinstance(source_canvases[canvas_index],
                                                                    viwid.canvas.BlankSemiOpaqueAreaCanvas):
            result.append(self.__layers[index])
            index += 1
            canvas_index += 1

        return result

    def _screen_resized(self, size: viwid.Size) -> None:
        """
        Called by the infrastructure when the application screen got resized.

        :param size: The new size.
        """
        self.__size = size
        self.__output_canvas.resize(self.__size)
        for layer in self.__layers:
            layer.widget._layout.apply(layer.widget._children, self.__size)

    def _realign_widgets(self, resize_soon_widgets: t.Sequence["viwid.widgets.widget.Widget"]):
        """
        Called by the infrastructure in order to refresh the inner alignment for given widgets.

        :param resize_soon_widgets: The widgets to refresh inner alignment for.
        """
        for layer in self.__layers:
            layer.widget.align(viwid.Point.ORIGIN, self.__size, forcefully_apply_resizing_for=resize_soon_widgets)

    def __widget_focused(self) -> None:
        self.__application_manager._widget_focused()

    def __layer_index_to_canvas_index(self, layer_index: int) -> int:
        if layer_index == len(self.__layers):
            return len(self.__output_canvas.source_canvases)

        canvas_index = 0
        for _ in range(layer_index):
            if isinstance(self.__output_canvas.source_canvases[canvas_index],
                          viwid.canvas.BlankSemiOpaqueAreaCanvas):
                canvas_index += 1
            canvas_index += 1

        return canvas_index
