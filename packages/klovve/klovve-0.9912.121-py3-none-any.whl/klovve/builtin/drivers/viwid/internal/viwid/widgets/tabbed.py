#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
See :py:class:`Tabbed`.
"""
import functools
import typing as t

import viwid
from viwid.widgets.widget import Widget as _Widget


class Tabbed(_Widget):
    """
    A panel with tabs.
    """

    def __init__(self, **kwargs):
        self.__active_tab = None
        self.__tab_changed_handlers = []
        super().__init__(**{**dict(layout=viwid.layout.GridLayout(viwid.layout.GridLayout.VERTICAL_PARTITIONER)
                                   ), **kwargs})

        self.__tab_bar = Tabbed._TabBar()
        self.__body_placeholder = viwid.widgets.box.Box()
        self._children = (self.__tab_bar, self.__body_placeholder)

    def __tab_added(self, index: int, tab: "Tab") -> None:
        if self.is_materialized:
            self.application_manager.materialize_widget(tab, self.screen_layer, self.__body_placeholder,
                                                        self.layer_style)
        self.__tab_bar.insert_tab_handle(index, tab_handle := Tabbed._TabHandle())

        tab_handle.listen_event(Tabbed._TabHandle.RequestActivateEvent, self.__handle_tab_handle_request_active)
        tab_handle.listen_event(Tabbed._TabHandle.RequestCloseEvent, self.__handle_tab_handle_request_close)

        if self.active_tab is None:
            self.active_tab = tab

        tab_changed_handler = functools.partial(self.__handle_tab_changed, tab)
        self.__tab_changed_handlers.insert(index, tab_changed_handler)
        tab.listen_property("title", tab_changed_handler)
        tab.listen_property("body", tab_changed_handler)
        tab.listen_property("is_closable_by_user", tab_changed_handler)
        tab.listen_property("is_visible", tab_changed_handler)
        tab_changed_handler()

    def __tab_removed(self, index: int, tab: "Tab") -> None:
        tab_changed_handler = self.__tab_changed_handlers.pop(index)
        tab.unlisten_property("title", tab_changed_handler)
        tab.unlisten_property("body", tab_changed_handler)
        tab.unlisten_property("is_closable_by_user", tab_changed_handler)
        tab.unlisten_property("is_visible", tab_changed_handler)

        self.application_manager.dematerialize_widget(tab)
        tab_handle = self.__tab_bar.remove_tab_handle(index)

        tab_handle.unlisten_event(self.__handle_tab_handle_request_active)
        tab_handle.unlisten_event(self.__handle_tab_handle_request_close)

        if tab is self.active_tab:
            self.active_tab_index = index

    @_Widget.ListProperty(__tab_added, __tab_removed)
    def tabs(self) -> list["Tab"]:
        """
        The tabs. Empty list by default.
        """

    @property
    def active_tab_index(self) -> int|None:
        """
        The index of the active tab.

        There will always be an active tab unless there are no tabs at all.
        """
        if self.active_tab is None:
            return None
        try:
            return self.tabs.index(self.active_tab)
        except ValueError:
            return None

    @active_tab_index.setter
    def active_tab_index(self, _: int|None) -> None:
        if _ is None or len(self.tabs) == 0:
            self.active_tab = None
        else:
            self.active_tab = self.tabs[min(max(0, _), len(self.tabs) - 1)]

    @property
    def active_tab(self) -> "Tab|None":
        """
        The active tab.

        There will always be an active tab unless there are no tabs at all.
        """
        return self.__active_tab

    @active_tab.setter
    def active_tab(self, _: "Tab|None") -> None:
        if _ is not None and _ not in self.tabs:
            self.active_tab = None
            return

        self.__active_tab = _
        self.__body_placeholder.children = (_.body,) if (_ and _.body) else ()
        if self.__body_placeholder.is_materialized:
            self.__body_placeholder.try_focus()
        i_active_tab = self.active_tab_index
        for i_tab, tab_handle in enumerate(self.__tab_bar.tab_handles):
            tab_handle_is_active = i_tab == i_active_tab
            if tab_handle.is_active != tab_handle_is_active:
                tab_handle.is_active = tab_handle_is_active

    def _materialize(self):
        super()._materialize()

        self.listen_event(Tabbed.Tab.RequestCloseEvent, self.__handle_request_tab_close,
                          implements_default_behavior=True)

        for tab in self.tabs:
            self.application_manager.materialize_widget(tab, self.screen_layer, self.__body_placeholder,
                                                        self.layer_style)

    def _dematerialize(self):
        self.unlisten_event(self.__handle_request_tab_close)

        for tab in self.tabs:
            self.application_manager.dematerialize_widget(tab)

        super()._dematerialize()

    def __handle_tab_changed(self, tab: "Tab") -> None:
        try:
            i_tab = self.tabs.index(tab)
        except ValueError:
            return

        tab_handle = self.__tab_bar.tab_handles[i_tab]
        if tab_handle.text != tab.title:
            tab_handle.text = tab.title
        if tab_handle.with_close_button != tab.is_closable_by_user:
            tab_handle.with_close_button = tab.is_closable_by_user
        if tab_handle.is_visible != tab.is_visible:
            tab_handle.is_visible = tab.is_visible

        if tab is self.__active_tab:
            if not tab.body:
                self.__body_placeholder.children = ()
            elif len(self.__body_placeholder.children) != 1 or self.__body_placeholder.children[0] != tab.body:
                self.__body_placeholder.children = (tab.body,)

    def __handle_request_tab_close(self, event):
        if event.tab in self.tabs:
            self.tabs.remove(event.tab)
        event.stop_handling()

    def __handle_tab_handle_request_active(self, event: "Tabbed._TabHandle.RequestActivateEvent") -> None:
        tab = self.tabs[self.__tab_bar.tab_handles.index(event.tab_handle)]
        self.active_tab = tab
        event.stop_handling()

    def __handle_tab_handle_request_close(self, event: "Tabbed._TabHandle.RequestCloseEvent") -> None:
        tab = self.tabs[self.__tab_bar.tab_handles.index(event.tab_handle)]
        self.screen_layer.trigger_event(tab, Tabbed.Tab.RequestCloseEvent(tab))
        event.stop_handling()

    class _TabBar(_Widget):

        def __init__(self, **kwargs):
            super().__init__(**{**dict(vertical_alignment=viwid.Alignment.START,
                                       layout=viwid.layout.GridLayout(viwid.layout.GridLayout.HORIZONTAL_PARTITIONER),
                                       class_style_name="tab_bar"),
                                **kwargs})

            self.__tab_handles_box = viwid.widgets.box.Box(vertical_alignment=viwid.Alignment.START,
                                                           class_style_name="tab_bar")
            self.__tab_handles_viewport = viwid.widgets.viewport.Viewport(body=self.__tab_handles_box,
                                                                          is_horizontally_scrollable=True)
            self.__scroll_left_button = viwid.widgets.button.Button(text="<")
            self.__scroll_right_button = viwid.widgets.button.Button(text=">")
            self._children = (self.__scroll_left_button, self.__tab_handles_viewport, self.__scroll_right_button)

        def _materialize(self):
            super()._materialize()

            self.__tab_handles_box.listen_event(viwid.event.widget.ResizeEvent, self.__handle_resized)
            self.__tab_handles_viewport.listen_event(viwid.event.widget.ResizeEvent, self.__handle_resized)
            self.listen_event(viwid.event.widget.ResizeEvent, self.__handle_resized)
            self.__scroll_left_button.listen_event(viwid.widgets.button.Button.TriggeredEvent,
                                                   self.__handle_scroll_left)
            self.__scroll_right_button.listen_event(viwid.widgets.button.Button.TriggeredEvent,
                                                    self.__handle_scroll_right)

        def _dematerialize(self):
            self.__tab_handles_box.unlisten_event(self.__handle_resized)
            self.__tab_handles_viewport.unlisten_event(self.__handle_resized)
            self.unlisten_event(self.__handle_resized)
            self.__scroll_left_button.unlisten_event(self.__handle_scroll_left)
            self.__scroll_right_button.unlisten_event(self.__handle_scroll_right)

            super()._dematerialize()

        def insert_tab_handle(self, index: int, tab_handle: "Tabbed._TabHandle") -> None:
            self.__tab_handles_box.children.insert(index, tab_handle)

        def remove_tab_handle(self, index: int) -> "Tabbed._TabHandle":
            return self.__tab_handles_box.children.pop(index)

        @property
        def tab_handles(self) -> t.Sequence["Tabbed._TabHandle"]:
            return tuple(self.__tab_handles_box.children)

        def __handle_scroll_left(self, event):
            self.__set_scroll_offset(2)

        def __handle_scroll_right(self, event):
            self.__set_scroll_offset(-2)

        def __handle_resized(self, event):
            scroll_buttons_visible = self.__tab_handles_box.size.width > self.size.width
            self.__scroll_left_button.is_visible = self.__scroll_right_button.is_visible = scroll_buttons_visible
            self.__set_scroll_offset(0)

        def __set_scroll_offset(self, delta_x: int) -> None:
            missing_width = max(0, self.__tab_handles_box.size.width - self.__tab_handles_viewport.size.width)
            x = min(max(-missing_width, self.__tab_handles_viewport.offset.x + delta_x), 0)
            self.__tab_handles_viewport.offset = viwid.Offset(x, 0)

        def _compute_width(self, minimal):
            return max(10, 0 if minimal else super()._compute_width(minimal))

    class _TabHandle(_Widget):

        def __init__(self, **kwargs):
            super().__init__(**{**dict(layout=viwid.layout.GridLayout(viwid.layout.GridLayout.HORIZONTAL_PARTITIONER),
                                       horizontal_alignment=viwid.Alignment.CENTER,
                                       vertical_alignment=viwid.Alignment.CENTER),
                                **kwargs})
            self.__refresh_ui()

        text: str
        @_Widget.Property(default=lambda: "")
        def text(self, _):
            self.__refresh_ui()

        is_active: bool
        @_Widget.Property(default=lambda: False)
        def is_active(self, _):
            self.__refresh_ui()

        with_close_button: bool
        @_Widget.Property(default=lambda: False)
        def with_close_button(self, _):
            self.__refresh_ui()

        def _compute_height(self, width, minimal):
            return 1

        def __refresh_ui(self):
            class_style_name_outer = "tab_handle_active_outer" if self.is_active else "tab_handle_outer"
            class_style_name = "tab_handle_active" if self.is_active else "tab_handle"
            class_style_name_close = "tab_handle_active_close" if self.is_active else "tab_handle_close"
            self._set_class_style_name(class_style_name_outer)
            self._children = (
                viwid.widgets.label.Label(text="/", class_style_name=class_style_name_outer),
                activate_button := viwid.widgets.button.Button(text=self.text, class_style_name=class_style_name,
                                                               decoration=viwid.widgets.button.Decoration.NONE,
                                                               minimal_size=viwid.Size(1, 1)),
                close_button := viwid.widgets.button.Button(text="x", class_style_name=class_style_name_close,
                                                            decoration=viwid.widgets.button.Decoration.NONE,
                                                            margin=viwid.Margin(left=2),
                                                            is_visible=self.with_close_button),
                viwid.widgets.label.Label(text="\\", class_style_name=class_style_name_outer))
            activate_button.listen_event(viwid.widgets.button.Button.TriggeredEvent, self.__handle_activated)
            close_button.listen_event(viwid.widgets.button.Button.TriggeredEvent, self.__handle_close)
            self.listen_event(viwid.event.mouse.ClickEvent, self.__handle_activated, preview=True)

        def __handle_activated(self, event):
            if isinstance(getattr(event, "touched_widget", None), viwid.widgets.button.Button):
                return  # we handle that in the TriggeredEvent
            self.screen_layer.trigger_event(self, Tabbed._TabHandle.RequestActivateEvent(self))
            event.stop_handling()

        def __handle_close(self, event):
            self.screen_layer.trigger_event(self, Tabbed._TabHandle.RequestCloseEvent(self))
            event.stop_handling()

        class _Event(viwid.event.Event):

            def __init__(self, tab_handle: "Tabbed._TabHandle"):
                super().__init__()
                self.__tab_handle = tab_handle

            @property
            def tab_handle(self) -> "Tabbed._TabHandle":
                return self.__tab_handle

        class RequestActivateEvent(_Event):
            pass

        class RequestCloseEvent(_Event):
            pass

    class Tab(_Widget):
        """
        One tab in a :py:class:`Tabbed`.

        It can be configured to be closable by user. If so, a request to do that will trigger
        :py:class:`Tabbed.Tab.RequestCloseEvent`. By default, this will eventually close the tab.
        """

        def __init__(self, **kwargs):
            super().__init__(**{**dict(), **kwargs})

        title: str
        @_Widget.Property(default=lambda: "")
        def title(self, _):
            """
            The tab title. Empty string by default.
            """

        body: _Widget|None
        @_Widget.Property
        def body(self, _):
            """
            The body widget of this tab. `None` by default.
            """

        is_closable_by_user: bool
        @_Widget.Property(default=lambda: False)
        def is_closable_by_user(self, _):
            """
            Whether this tab can be closed by the user. `False` by default.
            """

        class RequestCloseEvent(viwid.event.Event):
            """
            Event that occurs when the user requests to close a tab in a :py:class:`Tabbed`.
            """

            def __init__(self, tab: "Tabbed.Tab"):
                super().__init__()
                self.__tab = tab

            @property
            def tab(self) -> "Tabbed.Tab":
                """
                The tab that was requested to disappear.
                """
                return self.__tab
