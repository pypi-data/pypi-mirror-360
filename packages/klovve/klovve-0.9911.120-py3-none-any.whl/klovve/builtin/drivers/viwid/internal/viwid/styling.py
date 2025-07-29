#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
Styling - mostly colouring - of visual elements.

See :py:func:`default_theme`.
"""
import viwid.canvas
import viwid.data.color


class Theme:
    """
    A theme is the root of styling information. For each kind of screen layer (i.e. whether it is a normal window,
    a popup window, or something completely special), it contains a :py:class:`Theme.Layer` that defines how visual
    elements are to be styled there.
    """

    class Layer:
        """
        Styling information for a particular kind of screen layer (i.e. whether it is a normal window, a popup window,
        or something completely special). For each kind of visual element, it contains a :py:class:`Theme.Layer.Class`
        that defines how it is to be styled in the different states that elements can have.
        """

        class Class:
            """
            Styling information for a particular kind of visual element in a particular kind of screen layer (normal
            window, popup, ...). For each state that visual elements can have, it contains a
            :py:class:`Theme.Layer.Class.Style` that defines the actual visual attributes this element should be
            styled with.
            """

            class Style:
                """
                Styling information for a particular kind of visual element in a particular kind of screen layer (normal
                window, popup, ...) and a particular element state. It contains the visual attributes this element
                should be styled with.
                """

                def __init__(self, *, foreground: viwid.data.color.TColorInput = "#0000",
                             background: viwid.data.color.TColorInput = "#0000"):
                    """
                    See this type's attributes for more details about the parameters.
                    """
                    self.__foreground = viwid.Color.get(foreground)
                    self.__background = viwid.Color.get(background)

                @property
                def foreground(self) -> viwid.Color:
                    """
                    The foreground color.

                    Text will be printed in this color.
                    """
                    return self.__foreground

                @property
                def background(self) -> viwid.Color:
                    """
                    The background color.
                    """
                    return self.__background

            def __init__(self, normal: Style, *, hovered: Style | None = None, focused: Style | None = None,
                         activated: Style | None = None, disabled: Style | None = None):
                """
                See this type's attributes for more details about the parameters.
                """
                self.__normal = normal
                self.__hovered = hovered or normal
                self.__focused = focused or normal
                self.__activated = activated or normal
                self.__disabled = disabled or normal

            @property
            def normal(self) -> Style:
                """
                Styling information for this visual element in normal state.

                It applies whenever none of the other states apply.
                """
                return self.__normal

            @property
            def hovered(self) -> Style:
                """
                Styling information for this visual element in hovered state.

                It applies when the visual element is touched by the user's mouse cursor, until the cursor leaves it
                again.

                Only some visual elements can be hovered (e.g. plain text labels cannot).

                It usually looks similar but not identical to :py:attr:`focused`, since these are very similar in
                concept.
                """
                return self.__hovered

            @property
            def focused(self) -> Style:
                """
                Styling information for this visual element in focused state.

                It applies when the visual element is visited by the user either by 'tabbing' to it or by clicking at
                it.

                Only some visual elements can be focused (e.g. plain text labels cannot).

                It usually looks similar but not identical to :py:attr:`hovered`, since these are very similar in
                concept.
                """
                return self.__focused

            @property
            def activated(self) -> Style:
                """
                Styling information for this visual element in activated state.

                It can apply for some kinds of visual elements (e.g. buttons), for a fraction of a second after
                triggering it.
                """
                return self.__activated

            @property
            def disabled(self) -> Style:
                """
                Styling information for this visual element in disabled state.

                It applies when this visual element (or one of its ancestors) is set up to be disabled.
                """
                return self.__disabled

        def __init__(self, *, plain: Class|None = None, window: Class|None = None, window_title: Class|None = None,
                     control: Class|None = None, control_shades: Class|None = None, tiny_control: Class|None = None,
                     frame: Class|None = None, entry: Class|None = None, entry_hint: Class|None = None,
                     list: Class|None = None, list_item: Class|None = None, selected_list_item: Class|None = None,
                     progress_done: Class|None = None, progress_not_done: Class|None = None,
                     scroll_bar: Class|None = None, scroll_bar_handle: Class|None = None, tab_bar: Class|None = None,
                     tab_handle: Class|None = None, tab_handle_outer: Class|None = None,
                     tab_handle_close: Class | None = None, tab_handle_active: Class|None = None,
                     tab_handle_active_outer: Class|None = None, tab_handle_active_close: Class|None = None,
                     slider: Class|None = None, tree_expander: Class|None = None):
            """
            See this type's attributes for more details about the parameters.
            """
            Class, Style = Theme.Layer.Class, Theme.Layer.Class.Style

            self.__plain = plain or Class(normal=Style(foreground="#333"), disabled=Style(foreground="#666"))
            self.__window = window or Class(Style(background="#fff"))
            self.__window_title = window_title or Class(Style(foreground="#fff", background="#05f"))
            self.__control = control or Class(
                normal=Style(foreground="#fff", background="#05a"),
                hovered=Style(foreground="#fff", background="#0aa"),
                focused=Style(foreground="#fff", background="#088"),
                activated=Style(foreground="#ccf", background="#00f"),
                disabled=Style(foreground="#444", background="#88f"))
            self.__control_shades = control_shades or Class(
                normal=Style(foreground="#08d", background="#5af"),
                hovered=Style(foreground="#0dd", background="#0ff"),
                focused=Style(foreground="#0aa", background="#0dd"),
                activated=Style(foreground="#35a", background="#37c"),
                disabled=Style(foreground="#f5f", background="#faf"))
            self.__tiny_control = tiny_control or Class(normal=Style(foreground="#9cf"),
                                                           hovered=Style(foreground="#008", background="#0df"))
            self.__frame = frame or Class(Style(foreground="#9af"))
            self.__entry = entry or Class(
                normal=Style(foreground="#000", background="#bdf"),
                hovered=Style(foreground="#000", background="#0dd"),
                focused=Style(foreground="#000", background="#0aa"),
                disabled=Style(foreground="#666", background="#eef"))
            self.__entry_hint = entry_hint or Class(
                normal=Style(foreground="#05c"),
                disabled=Style(foreground="#999"))
            self.__list = list or Class(
                normal=Style(),
                focused=Style(background="#cff"),
                hovered=Style(background="#aff"),
                disabled=Style(foreground="#888"))
            self.__list_item = list_item or Class(
                normal=Style(foreground="#057"),
                disabled=Style(foreground="#555"))
            self.__selected_list_item = selected_list_item or Class(
                normal=Style(foreground="#007", background="#9cf"),
                disabled=Style(foreground="#ff0"))
            self.__progress_done = progress_done or Class(Style(foreground="#000", background="#00f"))
            self.__progress_not_done = progress_not_done or Class(Style(foreground="#000", background="#ccc"))
            self.__scroll_bar = scroll_bar or Class(
                normal=Style(background="#acf"),
                hovered=Style(background="#aff"),
                focused=Style(background="#aff"),
                activated=Style(background="#acf"),
                disabled=Style(background="#aaf"))
            self.__scroll_bar_handle = scroll_bar_handle or Class(
                normal=Style(background="#0af"),
                hovered=Style(background="#088"),
                focused=Style(background="#055"),
                activated=Style(background="#00f"),
                disabled=Style(background="#88f"))
            self.__tab_bar = tab_bar or Class(Style(foreground="#000", background="#ccf"))
            self.__tab_handle = tab_handle or Class(
                normal=Style(foreground="#55a", background="#aaf"),
                hovered=Style(foreground="#55f", background="#8cc"),
                focused=Style(foreground="#55f", background="#5aa"),
                activated=Style(foreground="#55f", background="#00f"),
                disabled=Style(foreground="#888", background="#aaf"))
            self.__tab_handle_outer = tab_handle_outer or Class(
                normal=Style(foreground="#55f", background="#aaf"),
                hovered=Style(foreground="#55f", background="#aaf"),
                focused=Style(foreground="#55f", background="#aaf"),
                activated=Style(foreground="#55f", background="#aaf"),
                disabled=Style(foreground="#888", background="#aaf"))
            self.__tab_handle_close = tab_handle_close or Class(
                normal=Style(foreground="#a55"),
                hovered=Style(foreground="#a55", background="#8cc"),
                focused=Style(foreground="#a55", background="#5aa"),
                activated=Style(foreground="#a55", background="#aaf"),
                disabled=Style(foreground="#888"))
            self.__tab_handle_active = tab_handle_active or Class(
                normal=Style(foreground="#055", background="#aaf"),
                hovered=Style(foreground="#055", background="#8cc"),
                focused=Style(foreground="#055", background="#5aa"),
                activated=Style(foreground="#055", background="#00f"),
                disabled=Style(foreground="#555", background="#aaf"))
            self.__tab_handle_active_outer = tab_handle_active_outer or Class(
                normal=Style(foreground="#0aa", background="#aaf"),
                hovered=Style(foreground="#55f", background="#aaf"),
                focused=Style(foreground="#55f", background="#aaf"),
                activated=Style(foreground="#55f", background="#aaf"),
                disabled=Style(foreground="#555", background="#aaf"))
            self.__tab_handle_active_close = tab_handle_active_close or Class(
                normal=Style(foreground="#a55", background="#aaf"),
                hovered=Style(foreground="#a55", background="#8cc"),
                focused=Style(foreground="#a55", background="#5aa"),
                activated=Style(foreground="#a55", background="#aaf"),
                disabled=Style(foreground="#888", background="#aaf"))
            self.__slider = slider or Class(
                normal=Style(foreground="#5af"),
                hovered=Style(foreground="#0ff"),
                focused=Style(foreground="#0dd"),
                activated=Style(foreground="#37c"),
                disabled=Style(foreground="#faf"))
            self.__tree_expander = tree_expander or Class(
                normal=Style(foreground="#0af"),
                disabled=Style(foreground="#555"))

        @property
        def plain(self) -> Class:
            """
            Styling for plain text labels or similar.
            """
            return self.__plain

        @property
        def window(self) -> Class:
            """
            Styling for a window body.
            """
            return self.__window

        @property
        def window_title(self) -> Class:
            """
            Styling for a window title bar.
            """
            return self.__window_title

        @property
        def control(self) -> Class:
            """
            Styling for a control (a button or similar things).
            """
            return self.__control

        @property
        def control_shades(self) -> Class:
            """
            Styling for the outer shades of a control.
            """
            return self.__control_shades

        @property
        def tiny_control(self) -> Class:
            """
            Styling for a tiny control.
            """
            return self.__tiny_control

        @property
        def frame(self) -> Class:
            """
            Styling for a frame.
            """
            return self.__frame

        @property
        def entry(self) -> Class:
            """
            Styling for an entry field (where users can enter text).
            """
            return self.__entry

        @property
        def entry_hint(self) -> Class:
            """
            Styling for the hint text in an entry field.
            """
            return self.__entry_hint

        @property
        def list(self) -> Class:
            """
            Styling for a list. There are further definitions for more specific parts.
            """
            return self.__list

        @property
        def list_item(self) -> Class:
            """
            Styling for an item of a list.
            """
            return self.__list_item

        @property
        def selected_list_item(self) -> Class:
            """
            Styling for the selected item of a list.
            """
            return self.__selected_list_item

        @property
        def progress_done(self) -> Class:
            """
            Styling for the "done" part of progress bars.
            """
            return self.__progress_done

        @property
        def progress_not_done(self) -> Class:
            """
            Styling for the "not-done" part of progress bars.
            """
            return self.__progress_not_done

        @property
        def scroll_bar(self) -> Class:
            """
            Styling for scroll bars.
            """
            return self.__scroll_bar

        @property
        def scroll_bar_handle(self) -> Class:
            """
            Styling for scroll bar handles.
            """
            return self.__scroll_bar_handle

        @property
        def tab_bar(self) -> Class:
            """
            Styling for tab bars.
            """
            return self.__tab_bar

        @property
        def tab_handle(self) -> Class:
            """
            Styling for tab handles. There are further definitions for more specific parts.
            """
            return self.__tab_handle

        @property
        def tab_handle_outer(self) -> Class:
            """
            Styling for the outer part of tab handles.
            """
            return self.__tab_handle_outer

        @property
        def tab_handle_close(self) -> Class:
            """
            Styling for close buttons in tab handles.
            """
            return self.__tab_handle_close

        @property
        def tab_handle_active(self) -> Class:
            """
            Styling for active tab handles.
            """
            return self.__tab_handle_active

        @property
        def tab_handle_active_outer(self) -> Class:
            """
            Styling for the outer part of active tab handles.
            """
            return self.__tab_handle_active_outer

        @property
        def tab_handle_active_close(self) -> Class:
            """
            Styling for close buttons in active tab handles.
            """
            return self.__tab_handle_active_close

        @property
        def slider(self) -> Class:
            """
            Styling for slider elements.
            """
            return self.__slider

        @property
        def tree_expander(self) -> Class:
            """
            Styling for tree_expander elements.
            """
            return self.__tree_expander

    def __init__(self, *, main: Layer, popup: Layer, app_chooser: Layer):
        """
        See this type's attributes for more details about the parameters.
        """
        self.__main = main
        self.__popup = popup
        self.__app_chooser = app_chooser

    @property
    def main(self) -> Layer:
        """
        The layer styling for normal main windows.
        """
        return self.__main

    @property
    def popup(self) -> Layer:
        """
        The layer styling for popup windows.
        """
        return self.__popup

    @property
    def app_chooser(self) -> Layer:
        """
        The layer styling for the application chooser (only visible when more than one application is running).
        """
        return self.__app_chooser


def default_theme() -> Theme:
    """
    Return the default theme.
    """
    Layer, Class, Style = Theme.Layer, Theme.Layer.Class, Theme.Layer.Class.Style

    return Theme(
        main=Layer(),
        popup=Layer(
            window=Class(Style(background="#aff"))),
        app_chooser=Layer(
            plain=Class(Style(background="#005", foreground="#777")),
            control=Class(Style(foreground="#88f", background="#00a")),
            control_shades=Class(Style(foreground="#005", background="#005")),
            tiny_control=Class(Style(foreground="#005", background="#05f"))))
