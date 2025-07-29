#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
See :py:class:`Scrollable`.
"""
import viwid.app.screen
import viwid.event
import viwid.layout
import viwid.widgets
from viwid.widgets.widget import Widget as _Widget
from viwid.widgets.viewport import Viewport as _Viewport


class Scrollable(_Widget):  # TODO does not work when only horizontally?!
    """
    A scrollable area that makes an arbitrary widget scrollable.

    Whenever the scroll offset get changed, :py:class:`Scrollable.OffsetChangedEvent` will be triggered.
    """

    def __init__(self, **kwargs):
        super().__init__(**{**dict(layout=viwid.layout.GridLayout(viwid.layout.GridLayout.VERTICAL_PARTITIONER)),
                            **kwargs})

        self.__old_offset = None
        self.__body = Scrollable._ScrollableBody(self)
        self.__horizontal_scroll_bar = viwid.widgets.scroll_bar.ScrollBar(
            orientation=viwid.Orientation.HORIZONTAL,
            vertical_alignment=viwid.Alignment.END,
            is_visible=False)
        self.__vertical_scroll_bar = viwid.widgets.scroll_bar.ScrollBar(
            orientation=viwid.Orientation.VERTICAL,
            horizontal_alignment=viwid.Alignment.END,
            is_visible=False)
        self.__nupsie = viwid.widgets.label.Label(text=" ", class_style_name="control", is_visible=False)
        self._children = [
            viwid.widgets.box.Box(
                children=[
                    viwid.widgets.box.Box(
                        children=[self.__body, self.__horizontal_scroll_bar],
                        orientation=viwid.Orientation.VERTICAL),
                    viwid.widgets.box.Box(
                        children=[self.__vertical_scroll_bar, self.__nupsie],
                        orientation=viwid.Orientation.VERTICAL,
                        horizontal_alignment=viwid.Alignment.END)])]

    body: "viwid.widgets.widget.Widget|None"
    @_Widget.Property()
    def body(self, _):
        """
        The widget inside the scrollable area. `None` by default.
        """
        self.__body.body = _

    is_vertically_scrollable: bool
    @_Widget.Property(default=lambda: True)
    def is_vertically_scrollable(self, _):
        """
        Whether this area is vertically scrollable. `True` by default.
        """
        self.__body.is_vertically_scrollable = self.is_vertically_scrollable
        self.__handle_resized()

    is_horizontally_scrollable: bool
    @_Widget.Property(default=lambda: False)
    def is_horizontally_scrollable(self, _):
        """
        Whether this area is horizontally scrollable. `False` by default.
        """
        self.__body.is_horizontally_scrollable = self.is_horizontally_scrollable
        self.__handle_resized()

    @property
    def horizontal_scroll_current_offset(self) -> int|None:
        """
        The current horizontal scroll offset.

        Is `None` when not :py:attr:`is_horizontally_scrollable`.

        This is a positive value >= 0 and <= :py:attr:`horizontal_scroll_max_offset`.
        """
        if not self.is_horizontally_scrollable:
            return None
        if not self.__horizontal_scroll_bar.is_visible:
            return 0

        return int(self.__horizontal_scroll_bar.value)

    @property
    def horizontal_scroll_max_offset(self) -> int|None:
        """
        The maximal horizontal scroll offset (i.e. how many steps must be scrolled to have the entire body seen). This
        is a positive value >= 0.

        Is `None` when not :py:attr:`is_horizontally_scrollable`.

        See also :py:attr:`horizontal_scroll_current_offset`.
        """
        if not self.is_horizontally_scrollable:
            return None
        if not self.__horizontal_scroll_bar.is_visible:
            return 0

        return int(self.__horizontal_scroll_bar.value_range.max_value)

    @property
    def vertical_scroll_current_offset(self) -> int|None:
        """
        The current vertical scroll offset.

        Is `None` when not :py:attr:`is_vertically_scrollable`.

        This is a positive value >= 0 and <= :py:attr:`vertical_scroll_max_offset`.
        """
        if not self.is_vertically_scrollable:
            return None
        if not self.__vertical_scroll_bar.is_visible:
            return 0

        return int(self.__vertical_scroll_bar.value)

    @property
    def vertical_scroll_max_offset(self) -> int|None:
        """
        The maximal vertical scroll offset (i.e. how many steps must be scrolled to have the entire body seen). This
        is a positive value >= 0.

        Is `None` when not :py:attr:`is_vertically_scrollable`.

        See also :py:attr:`vertical_scroll_current_offset`.
        """
        if not self.is_vertically_scrollable:
            return None
        if not self.__vertical_scroll_bar.is_visible:
            return 0

        return int(self.__vertical_scroll_bar.value_range.max_value)

    def scroll_to(self, offset: viwid.Offset) -> None:
        """
        Scroll to a given offset.

        The offset elements are positive values (see :py:attr:`horizontal_scroll_current_offset` and
        :py:attr:`vertical_scroll_current_offset`).

        :param offset: The offset.
        """
        if self.is_horizontally_scrollable and self.__horizontal_scroll_bar.is_visible:
            self.__horizontal_scroll_bar.value = offset.x
        if self.is_vertically_scrollable and self.__vertical_scroll_bar.is_visible:
            self.__vertical_scroll_bar.value = offset.y

    def _materialize(self):
        super()._materialize()

        self.__body.listen_event(viwid.widgets.viewport.Viewport.BodyResizedEvent, self.__handle_resized,
                                 implements_default_behavior=True)
        self.__horizontal_scroll_bar.listen_property("value", self.__handle_scrolled)
        self.__vertical_scroll_bar.listen_property("value", self.__handle_scrolled)
        self.__body.listen_property("offset", self.__handle_body_offset_changed)

        self.__handle_resized()

    def _dematerialize(self):
        self.__body.unlisten_event(self.__handle_resized)
        self.__horizontal_scroll_bar.unlisten_property("value", self.__handle_scrolled)
        self.__vertical_scroll_bar.unlisten_property("value", self.__handle_scrolled)
        self.__body.unlisten_property("offset", self.__handle_body_offset_changed)

        super()._dematerialize()

    def _compute_width(self, minimal):
        if minimal or self.is_horizontally_scrollable:
            return 3
        return super()._compute_width(minimal)

    def _compute_height(self, width, minimal):
        if minimal or self.is_vertically_scrollable:
            return 3
        return super()._compute_height(width, minimal)

    def _bring_child_into_view(self, widget):
        position, _ = viwid.app.screen.translate_coordinates_to_root(viwid.Point.ORIGIN, old_origin=widget)
        position = viwid.app.screen.translate_coordinates_from_root(position, new_origin=self.__body)
        position = position.moved_by(widget.size.width // 2, widget.size.height // 2)

        if self.is_horizontally_scrollable and self.__horizontal_scroll_bar.is_visible:
            self.__horizontal_scroll_bar.value = position.x - self.__body.size.width // 2

        if self.is_vertically_scrollable and self.__vertical_scroll_bar.is_visible:
            self.__vertical_scroll_bar.value = position.y - self.__body.size.height // 2

        super()._bring_child_into_view(widget)

    def __handle_scrolled(self):  # TODO odd
        self.__body.offset = viwid.Point(-int(self.__horizontal_scroll_bar.value
                                              if self.__horizontal_scroll_bar.is_visible else 0),
                                         -int(self.__vertical_scroll_bar.value
                                              if self.__vertical_scroll_bar.is_visible else 0))
        self.__body.repaint()

    def __handle_body_offset_changed(self):
        offset = self.horizontal_scroll_current_offset, self.vertical_scroll_current_offset
        if offset != self.__old_offset:
            self.__old_offset = offset
            self.screen_layer.trigger_event(self, Scrollable.OffsetChangedEvent())

    def __handle_resized(self):
        self.application_manager.driver.event_loop.create_task(self.__handle_resized__async())

    async def __handle_resized__async(self):
        if self.body:
            body_width = self.body.width_demand(minimal=False)

            if not self.is_horizontally_scrollable:
                body_width = min(body_width, self.__body.size.width)

            body_height = self.body.height_demand(body_width, minimal=False)

            outer_width = body_width + self.body.margin.width
            outer_height = body_height + self.body.margin.height
            over_width = outer_width - self.size.width
            over_height = outer_height - self.size.height

            if self.is_horizontally_scrollable and over_width > 0:
                self.__horizontal_scroll_bar.is_visible = True
                over_height += 1
            else:
                self.__horizontal_scroll_bar.is_visible = False

            if self.is_vertically_scrollable and over_height > 0:
                self.__vertical_scroll_bar.is_visible = True
                over_width += 1
            else:
                self.__vertical_scroll_bar.is_visible = False

            if self.is_horizontally_scrollable and not self.__horizontal_scroll_bar.is_visible and over_width > 0:
                self.__horizontal_scroll_bar.is_visible = True
                over_height += 1

            if self.__horizontal_scroll_bar.is_visible:
                self.__horizontal_scroll_bar.value_range = viwid.NumericValueRange(min_value=0, max_value=over_width,
                                                                                   step_size=1)
                self.__horizontal_scroll_bar.handle_size_fraction = self.__body.size.width / outer_width

            if self.__vertical_scroll_bar.is_visible:
                self.__vertical_scroll_bar.value_range = viwid.NumericValueRange(min_value=0, max_value=over_height,
                                                                                 step_size=1)
                self.__vertical_scroll_bar.handle_size_fraction = self.__body.size.height / outer_height

        else:
            self.__horizontal_scroll_bar.is_visible = False
            self.__vertical_scroll_bar.is_visible = False

        if not self.__horizontal_scroll_bar.is_visible:
            self.__horizontal_scroll_bar.value = 0

        if not self.__vertical_scroll_bar.is_visible:
            self.__vertical_scroll_bar.value = 0

        self.__nupsie.is_visible = self.__horizontal_scroll_bar.is_visible and self.__vertical_scroll_bar.is_visible

        self.__handle_scrolled()

        self.repaint()  # TODO odd, but the nupsie doesnt always come up otherwise?

    def _scroll(self, direction):
        if self.__vertical_scroll_bar.is_visible:
            self.__vertical_scroll_bar.value -= direction
            self.__handle_scrolled()

    class _ScrollableBody(_Viewport):

        def __init__(self, scrollable, **kwargs):
            super().__init__(**{**dict(), **kwargs})
            self.__scrollable = scrollable

        def _materialize(self):
            super()._materialize()

            self.listen_event(viwid.event.mouse.ScrollEvent, self.__handle_scrolled, implements_default_behavior=True)

        def _dematerialize(self):
            self.unlisten_event(self.__handle_scrolled)

            super()._dematerialize()

        def __handle_scrolled(self, event):
            self.__scrollable._scroll(event.direction)


    class OffsetChangedEvent(viwid.event.Event):
        """
        Event that occurs when the body widget of a viewport gets resized.
        """
