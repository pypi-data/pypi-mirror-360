#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
See :py:class:`DropDown`.
"""
import typing as t

import viwid.layout
import viwid.app.screen
import viwid.widgets
from viwid.widgets.widget import Widget as _Widget


class DropDown(_Widget):
    """
    A drop-down box that lets the user choose one item from a list of items.

    The items must be strings. After creation, no item is selected. The user (or the program logic that controls the
    drop-down box) explicitly has to select one to change that. Once an item is selected, the user cannot just unselect
    it anymore without selecting another one.
    """

    def __init__(self, **kwargs):
        super().__init__(**{**dict(layout=viwid.layout.GridLayout(viwid.layout.GridLayout.HORIZONTAL_PARTITIONER),
                                   horizontal_alignment=viwid.Alignment.CENTER,
                                   vertical_alignment=viwid.Alignment.CENTER),
                            **kwargs})
        self.__button = viwid.widgets.button.Button()
        self._children = [self.__button]
        self.selected_index = None

    def _materialize(self):
        super()._materialize()

        self.__button.listen_event(viwid.widgets.button.Button.TriggeredEvent, self.__handle_button_triggered,
                                   implements_default_behavior=True)

    def _dematerialize(self):
        self.__button.unlisten_event(self.__handle_button_triggered)

        super()._dematerialize()

    items: t.Sequence[str]
    @_Widget.ListProperty(lambda *_: None, lambda *_: None)  # TODO None odd
    def items(self):
        """
        The items to provide for choice.
        """
        pass

    selected_index: int|None
    @_Widget.Property
    def selected_index(self, _):
        """
        The index of the selected item. `None` by default.
        """
        self.selected_item = self.items[_] if (_ is not None) else None

    selected_item: str|None
    @_Widget.Property
    def selected_item(self, _):
        """
        The selected item. `None` by default.
        """
        try:
         idx = self.items.index(_) if (_ is not None) else None
        except ValueError:
            idx = None
        if idx != self.selected_index:
            self.selected_index = idx
            return
        self.__button.text = (_ if (_ is not None) else "   ") + "  v"

    def __handle_button_triggered(self, event: viwid.event.Event) -> None:
        def cc(i):
            def ccc():
                self.selected_index = i
                self.screen_layer.application.remove_layer(popup_layer)
            return ccc

        item_buttons = []
        for i, item in enumerate(self.items):
            button = viwid.widgets.button.Button(text=item, horizontal_alignment=viwid.Alignment.FILL,
                                                 decoration=viwid.widgets.button.Decoration.NONE)
            item_buttons.append(button)
            button.listen_event(viwid.widgets.button.Button.TriggeredEvent, cc(i))
        box = viwid.widgets.box.Box(orientation=viwid.Orientation.VERTICAL, children=item_buttons)
        # TODO the popup should somehow be just closable (via mouse and also via ESC)?!
        popup_layer = self.screen_layer.application.add_layer(
            viwid.widgets.box.Box(
                children=[viwid.widgets.frame.Frame(body=viwid.widgets.scrollable.Scrollable(
                    body=box,
                    is_vertically_scrollable=True))],
                class_style_name="window",
                horizontal_alignment=viwid.Alignment.FILL,
                vertical_alignment=viwid.Alignment.FILL),
            layout=viwid.app.screen.Layout(anchor_widget=self))

        event.stop_handling()
