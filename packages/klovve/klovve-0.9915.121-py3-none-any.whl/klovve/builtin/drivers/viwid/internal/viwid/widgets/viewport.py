#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
See :py:class:`Viewport`.
"""
import viwid.layout
from viwid.widgets.widget import Widget as _Widget


class Viewport(_Widget):
    """
    A scrollable (by program logic) viewport.

    This is basically the body part of a :py:class:`viwid.widgets.scrollable.Scrollable`, i.e. without the scroll bars.
    """

    def __init__(self, **kwargs):
        super().__init__(**{**dict(layout=Viewport._Layout(self)), **kwargs})
        self.__old_body = None

    body: "viwid.widgets.widget.Widget|None"
    @_Widget.Property()
    def body(self, _):
        """
        The widget inside the scrollable viewport. `None` by default.

        Whenever the body gets resized, :py:class:`Viewport.BodyResizedEvent` will be triggered.
        """
        if self.is_materialized:
            if self.__old_body:
                self.__old_body.unlisten_event(self.__handle_body_resized)
            self.__old_body = _
            if _:
                self.body.listen_event(viwid.event.widget.ResizeEvent, self.__handle_body_resized,
                                       implements_default_behavior=True)

        self.offset = viwid.Offset.NULL
        self._children = [_] if _ else []
        self.__refresh_geometry()

    is_vertically_scrollable: bool
    @_Widget.Property(default=lambda: False)
    def is_vertically_scrollable(self, _):
        """
        Whether this area is vertically scrollable. `False` by default.
        """
        self.__refresh_geometry()

    is_horizontally_scrollable: bool
    @_Widget.Property(default=lambda: False)
    def is_horizontally_scrollable(self, _):
        """
        Whether this area is horizontally scrollable. `False` by default.
        """
        self.__refresh_geometry()

    offset: viwid.Offset
    @_Widget.Property(default=lambda: viwid.Offset.NULL)
    def offset(self, _):
        """
        The current scroll offset. When scrolled, it will contain negative values. :py:attr:`viwid.Offset.NULL` by
        default.
        """
        self.__refresh_geometry()

    def _dematerialize(self):
        if self.body:
            self.body.unlisten_event(self.__handle_body_resized)

        super()._dematerialize()

    def _compute_width(self, minimal):
        if self.is_horizontally_scrollable or not self.body:
            return 0
        return self.body._compute_width(minimal)

    def _compute_height(self, width, minimal):
        if self.is_vertically_scrollable or not self.body:
            return 0
        return self.body._compute_height(width, minimal)

    def __refresh_geometry(self):
        offset = self.offset
        if not self.is_horizontally_scrollable:
            offset = offset.with_x(0)
        if not self.is_vertically_scrollable:
            offset = offset.with_y(0)
        self._layout.offset = offset

        self._request_resize()

    def __handle_body_resized(self, event: viwid.event.widget.ResizeEvent) -> None:
        self.screen_layer.trigger_event(self, Viewport.BodyResizedEvent())

    class _Layout(viwid.layout.Layout):

        def __init__(self, viewport):
            self.offset = viwid.Point.ORIGIN
            self.__viewport = viewport

        def apply(self, widgets, size, *, forcefully_apply_resizing_for=()):
            if len(widgets) == 0:
                return
            widget = widgets[0]
            width = widget.width_demand(minimal=False) if self.__viewport.is_horizontally_scrollable else size.width
            height = widget.height_demand(width,
                                          minimal=False) if self.__viewport.is_vertically_scrollable else size.height
            widget.align(self.offset, size=viwid.Size(width, height),
                         forcefully_apply_resizing_for=forcefully_apply_resizing_for)

        def compute_layout_width(self, widgets, minimal):
            return 0

        def compute_layout_height(self, widgets, width, minimal):
            return 0

    class BodyResizedEvent(viwid.event.Event):
        """
        Event that occurs when the body widget of a viewport gets resized.
        """
