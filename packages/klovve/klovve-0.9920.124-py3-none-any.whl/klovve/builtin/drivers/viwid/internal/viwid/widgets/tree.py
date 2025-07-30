#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
See :py:class:`Tree`.
"""
import abc
import functools
import typing as t

import viwid.app.screen
import viwid.event
import viwid.widgets
from viwid.widgets.widget import Widget as _Widget


class _Tree(_Widget, abc.ABC):
    """
    Internal base class for widgets like :py:class:`Tree` and :py:class:`viwid.widgets.list.List`.
    """

    def __init__(self, **kwargs):
        super().__init__(**{**dict(class_style_name="list",
                                   layout=viwid.layout.GridLayout(viwid.layout.GridLayout.VERTICAL_PARTITIONER),
                                   is_focusable=True), **kwargs})
        self.__last_active_item = None
        self.__item_representations = {}
        self.__item_by_representations = {}
        self.__item_row_visibility_changed_handlers = {}

    allows_multi_select: bool
    @_Widget.Property(default=lambda: False)
    def allows_multi_select(self, _):
        """
        Whether to allow selecting more than one item. :code:`False` by default.
        """
        for i_row, row in enumerate(self.items):
            row._allows_multi_select = _
        if not _:
            self._selected_item_indexes = self._selected_item_indexes[:1]

    def __item_added(self, index: int, item: _Widget) -> None:
        item._allows_multi_select = self.allows_multi_select
        item._host = self
        item._depth = 0
        item._parent_row = None
        self._children.insert(index, self._item_representation_for_new_item(item))

    def __item_removed(self, index: int, item: _Widget) -> None:
        self._remove_item_representation_for_item(item)
        self._children.pop(index)

    @_Widget.ListProperty(__item_added, __item_removed)
    def items(self) -> list["_Tree.Row"]:
        """
        The items to provide for choice.
        """

    _selected_item_indexes: t.Sequence[t.Sequence[int]]
    @_Widget.Property(default=lambda: (), changes_also=("selected_item_indexes",))
    def _selected_item_indexes(self, _):
        """
        The list of indexes of the selected items. Empty list by default.

        Whenever this changes, :py:class:`_Tree.SelectionChangedEvent` will be triggered as well.
        """
        selected_item_indexes = set(_)
        nodes = [((i,), x) for i, x in enumerate(self.items)]
        while nodes:
            node_index, node = nodes.pop()
            nodes += (((*node_index, i), x) for i, x in enumerate(node.items))
            node._is_selected = node_index in selected_item_indexes
        if not self.allows_multi_select:
            active_item_index = _[0] if len(_) > 0 else None
            if self._active_item_index != active_item_index:
                self._active_item_index = active_item_index
        self.screen_layer.trigger_event(self, _Tree.SelectionChangedEvent(self))

    _active_item_index: t.Sequence[int]|None
    @_Widget.Property(changes_also=("active_item_index",))
    def _active_item_index(self, _):
        """
        The index of the active item. :code:`None` by default.

        The active item is the same as the selected item as long as :py:attr:`allows_multi_select` is not enabled.
        Otherwise, the active item is the item that is currently 'focused', i.e. 'selected by means of mouse and
        keyboard'. This is not the user's actual selection, but just the item that the user _could_ toggle selection for
        next (or recently did).
        """
        if _ is not None:
            if len(self.items) == 0:
                self._active_item_index = None
                return
            corrected_index = list(_)
            node = self
            for i in range(len(corrected_index)):
                if len(node.items) == 0:
                    corrected_index = corrected_index[:i]
                    break
                index_element = corrected_index[i] = min(max(0, corrected_index[i]), len(node.items)-1)
                node = node.items[index_element]
            corrected_index = tuple(corrected_index) if len(corrected_index) > 0 else None
            if self._active_item_index != corrected_index:
                self._active_item_index = corrected_index
                return
            if node is self:
                node = None
        else:
            node = None

        if self.__last_active_item == node:
            return

        if not self.allows_multi_select:
            self._selected_item_indexes = (_,) if _ is not None else ()

        if self.__last_active_item is not None:
            self.__last_active_item._is_active = False
        self.__last_active_item = node
        if self.__last_active_item is not None:
            self.__last_active_item._is_active = True

    @abc.abstractmethod
    def _item_representation(self, row: "Row") -> _Widget:
        pass

    @abc.abstractmethod
    def _is_row_expanded(self, row: "Row") -> bool:
        pass

    @abc.abstractmethod
    def _set_row_expanded(self, row: "Row", expanded: bool) -> bool:
        pass

    @abc.abstractmethod
    def _child_item_added(self, in_row: "Row", index: int, new_row: "Row") -> None:
        pass

    @abc.abstractmethod
    def _child_item_removed(self, in_row: "Row", index: int, old_row: "Row") -> None:
        pass

    def _item_representation_for_new_item(self, item):
        self.__item_representations[item] = item_representation = self._item_representation(item)
        self.__item_by_representations[item_representation] = item
        self.__item_row_visibility_changed_handlers[item] = row_visibility_changed_handler = functools.partial(
            self.__handle_row_visibility_changed, item)

        item.listen_property("is_visible", row_visibility_changed_handler)
        row_visibility_changed_handler()

        return item_representation

    def _item_representation_for_existing_item(self, item):
        return self.__item_representations.get(item)

    def _remove_item_representation_for_item(self, item):
        item.unlisten_property("is_visible", self.__item_row_visibility_changed_handlers.pop(item))
        self.__item_by_representations.pop(self.__item_representations.pop(item))

    def __handle_row_visibility_changed(self, row):
        item_representation = self.__item_representations[row]
        row_visible = row.is_visible
        if item_representation.is_visible != row_visible:
            item_representation.is_visible = row_visible

        if self._active_item_index is not None:
            active_row = self._item_for_index(self._active_item_index)
            if not active_row or not active_row.is_actually_visible:
                self._active_item_index = None

    def _materialize(self):
        super()._materialize()

        self.listen_event(viwid.event.mouse.ClickEvent, self.__handle_mouse_clicked, implements_default_behavior=True)
        self.listen_event(viwid.event.keyboard.KeyPressEvent, self.__handle_keyboard_key_pressed,
                          implements_default_behavior=True)

    def _dematerialize(self):
        self.unlisten_event(self.__handle_mouse_clicked)
        self.unlisten_event(self.__handle_keyboard_key_pressed)

        super()._dematerialize()

    def _item_for_index(self, index: t.Sequence[int]) -> "Row":
        if len(index) == 0:
            raise ValueError("invalid index")
        result = self
        for i in index:
            result = result.items[i]
        return result

    def _row_to_index(self, row):
        if row is None:
            return None

        result = []

        while row:
            result.append((row._parent_row or self).items.index(row))
            row = row._parent_row

        return tuple(reversed(result))

    def __handle_keyboard_key_pressed(self, event):
        if len(self.items) > 0:
            if event.code == viwid.event.keyboard.KeyCodes.ARROW_UP:
                if self._active_item_index is None:
                    self._active_item_index = (0,)
                    self._bring_child_into_view(self._item_for_index(self._active_item_index))
                    event.stop_handling()
                else:
                    new_active_item_index = self.__handle_keyboard_key_pressed__new_index(-1)
                    if new_active_item_index is not None:
                        self._active_item_index = new_active_item_index
                        self._bring_child_into_view(self._item_for_index(self._active_item_index))
                        event.stop_handling()
            elif event.code == viwid.event.keyboard.KeyCodes.ARROW_DOWN:
                if self._active_item_index is None:
                    self._active_item_index = (0,)
                    self._bring_child_into_view(self._item_for_index(self._active_item_index))
                    event.stop_handling()
                else:
                    new_active_item_index = self.__handle_keyboard_key_pressed__new_index(1)
                    if new_active_item_index is not None:
                        self._active_item_index = new_active_item_index
                        self._bring_child_into_view(self._item_for_index(self._active_item_index))
                        event.stop_handling()
            elif event.char and event.char in "+-":
                if self._active_item_index is not None:
                    row = self._item_for_index(self._active_item_index)
                    self._set_row_expanded(row, not self._is_row_expanded(row))
                event.stop_handling()
            elif event.code in (viwid.event.keyboard.KeyCodes.ENTER,
                                viwid.event.keyboard.KeyCodes.SPACE):
                if self.allows_multi_select and self._active_item_index is not None:
                    selected_item_indexes = list(self._selected_item_indexes)
                    if self._active_item_index in selected_item_indexes:
                        selected_item_indexes.remove(self._active_item_index)
                    else:
                        selected_item_indexes.append(self._active_item_index)
                    self._selected_item_indexes = tuple(selected_item_indexes)
                self.screen_layer.trigger_event(self, _Tree.SelectionChangedEvent(self))
                event.stop_handling()

    def __handle_mouse_clicked(self, event):
        if event.subject_button == viwid.event.mouse.ClickEvent.BUTTON_LEFT:
            self.try_focus()
            ppx = viwid.app.screen.translate_coordinates_from_root(event.screen_position, new_origin=self)
            row = self.__handle_mouse_clicked__row_for_widget(self.widget_at_position(ppx))
            if row:
                row_index = self._row_to_index(row)
                if row_index is not None:
                    if self.allows_multi_select:
                        selected_item_indexes = list(self._selected_item_indexes)
                        if row_index in selected_item_indexes:
                            selected_item_indexes.remove(row_index)
                        else:
                            selected_item_indexes.append(row_index)
                        self._selected_item_indexes = tuple(selected_item_indexes)
                    else:
                        self._selected_item_indexes = (row_index,)
                    self._active_item_index = row_index
                    self.screen_layer.trigger_event(self, _Tree.SelectionChangedEvent(self))
                    event.stop_handling()
                    return

    def __handle_mouse_clicked__row_for_widget(self, widget: _Widget) -> "Row":
        while widget:
            row = self.__item_by_representations.get(widget)
            if row:
                return row
            widget = widget.parent

    def __handle_keyboard_key_pressed__new_index(self, direction: int) -> t.Sequence[int]|None:
        row = self._item_for_index(self._active_item_index)
        flattened_tree = self.__handle_keyboard_key_pressed__flattened_visible_tree()
        try:
            i = flattened_tree.index(row) + direction
        except ValueError:
            return None
        if 0 <= i < len(flattened_tree):
            return self._row_to_index(flattened_tree[i])

    def __handle_keyboard_key_pressed__flattened_visible_tree(self):
        result = []
        nodes = list(self.items)
        while nodes:
            node = nodes.pop(0)
            result.append(node)
            if self._is_row_expanded(node):
                for child_node in reversed(node.items):
                    nodes.insert(0, child_node)

        return result

    class SelectionChangedEvent(viwid.event.Event):
        """
        Event that occurs when the selection in the tree/list has been changed (either by the user or by the program
        logic that controls the tree/list).
        """

        def __init__(self, list: "viwid.widgets.list._Tree"):
            super().__init__()
            self.__list = list

        @property
        def list(self) -> "viwid.widgets.list._Tree":
            """
            The tree/list whose selection has been changed.
            """
            return self.__list

    class Row(_Widget):  # TODO why do we expose it? and if so, why not e.g. for drop-downs as well?
        """
        One selectable row in a :py:class:`_Tree`.
        """

        def __init__(self, **kwargs):
            super().__init__(
                vertical_alignment=viwid.Alignment.FILL,
                **kwargs)

            self.__selected_prefix_text = None
            self.__unselected_prefix_text = None

        text: str
        @_Widget.Property(default=lambda: "")
        def text(self, _):
            """
            The text of this row.
            """
            self.__measure_input_text = self._text_measuring.text(_)
            self._request_resize_and_repaint()

        def __item_added(self, index: int, item: _Widget) -> None:
            item._allows_multi_select = self._allows_multi_select
            item._depth = self._depth + 1
            item._host = self._host
            item._parent_row = self
            self._host._child_item_added(self, index, self._host._item_representation_for_new_item(item))

        def __item_removed(self, index: int, item: _Widget) -> None:
            self._host._remove_item_representation_for_item(item)
            self._host._child_item_removed(self, index, item)

        @_Widget.ListProperty(__item_added, __item_removed)
        def items(self) -> list["_Tree.Row"]:
            """
            The child items.

            This is intended to be used for tree-like structures (like :py:class:`Tree`).
            Do not use this for flat lists (like :py:class:`viwid.widgets.list.List`)!
            """

        def _materialize(self):
            super()._materialize()

            self.__selected_prefix_text = self._text_measuring.text("▐x▌")
            self.__unselected_prefix_text = self._text_measuring.text("▐ ▌")

        _is_active: bool
        @_Widget.Property
        def _is_active(self, _):
            self._set_class_style_name("selected_list_item" if _ else "list_item")

        _is_selected: bool
        @_Widget.Property
        def _is_selected(self, _):
            self._request_repaint()

        _allows_multi_select: bool
        @_Widget.Property(default=lambda: False)
        def _allows_multi_select(self, _):
            self._request_resize_and_repaint()

        _depth: int
        @_Widget.Property(default=lambda: 0)
        def _depth(self, _):
            self._request_resize_and_repaint()

        _host: "_Tree|None"
        @_Widget.Property
        def _host(self, _):
            pass

        _parent_row: "_Tree.Row|None"
        @_Widget.Property
        def _parent_row(self, _):
            pass

        def _compute_width(self, minimal) -> int:
            check_width = 3 if self._allows_multi_select else 0
            if minimal:
                return check_width + 1
            return check_width + self._text_measuring.text_width(self.__measure_input_text)

        def _compute_height(self, width: int, minimal) -> int:
            return self._text_measuring.text_height(self.__measure_input_text, for_width=width)

        def _paint(self, canvas):
            if self._allows_multi_select:
                canvas.draw_text(self.__selected_prefix_text if self._is_selected else self.__unselected_prefix_text)
                text_position = viwid.Point(3, 0)
            else:
                text_position = viwid.Point.ORIGIN
            canvas.draw_text(self.__measure_input_text, rectangle=viwid.Rectangle(text_position, self.size))


class Tree(_Tree):
    """
    A tree (of rows) that lets the user choose one item (or multiple if configured this way).

    After creation, no item is selected. The user (or the program logic that controls the list) explicitly has to select
    one to change that. If multi-selection is not allowed (the default), once an item is selected, the user cannot just
    unselect it anymore without selecting another one.
    """

    def _item_representation(self, row):
        result = Tree._RowWithChildren(row=row)
        for i_child_row, child_row in enumerate(row.items):
            self._child_item_added(result, i_child_row, self._item_representation_for_new_item(child_row))
        return result

    def _is_row_expanded(self, row):
        return self._item_representation_for_existing_item(row).is_expanded

    def _set_row_expanded(self, row, expanded):
        self._item_representation_for_existing_item(row).is_expanded = expanded
        if not expanded:
            if active_item_index := self._active_item_index:
                row_index = self._row_to_index(row)
                if len(active_item_index) > len(row_index) and active_item_index[:len(row_index)] == row_index:
                    self._active_item_index = row_index

    def _child_item_added(self, in_row, index, new_row):
        if isinstance(in_row, _Tree.Row):
            in_row = self._item_representation_for_existing_item(in_row)
            if in_row is None:
                return
        in_row.add_child(index, new_row)

    def _child_item_removed(self, in_row, index, old_row):
        if isinstance(in_row, _Tree.Row):
            in_row = self._item_representation_for_existing_item(in_row)
            if in_row is None:
                return
        in_row.remove_child(index, old_row)

    @property
    def selected_item_indexes(self) -> t.Sequence[t.Sequence[int]]:
        """
        The list of indexes of the selected items. Empty list by default.

        Whenever this changes, :py:class:`_Tree.SelectionChangedEvent` will be triggered as well.
        """
        return self._selected_item_indexes

    @selected_item_indexes.setter
    def selected_item_indexes(self, _):
        self._selected_item_indexes = _

    @property
    def active_item_index(self) -> t.Sequence[int] | None:
        """
        The index of the active item. :code:`None` by default.

        The active item is the same as the selected item as long as :py:attr:`allows_multi_select` is not enabled.
        Otherwise, the active item is the item that is currently 'focused', i.e. 'selected by means of mouse and
        keyboard'. This is not the user's actual selection, but just the item that the user _could_ toggle selection for
        next (or recently did).
        """
        return self._active_item_index

    @active_item_index.setter
    def active_item_index(self, _):
        self._active_item_index = _

    def item_for_index(self, index: t.Sequence[int]) -> "_Tree.Row":
        """
        Return the item for a given index.

        :param index: The index.
        """
        return self._item_for_index(index)

    def is_row_expanded(self, row: "_Tree.Row") -> bool:
        """
        Return whether a given row is in expanded state.

        It only regards the given row's own expanded state; i.e. whether itself is expanded or not. It does not regard
        e.g. whether ancestor rows are expanded as well.

        :param row: The row.
        """
        return self._is_row_expanded(row)

    def set_row_expanded(self, row: "_Tree.Row", expanded: bool) -> None:
        """
        Set the expanded state for a given row.

        :param row: The row.
        :param expanded: Whether to expand or collapse it.
        """
        self._set_row_expanded(row, expanded)

    class _RowWithChildren(_Widget):

        def __init__(self, **kwargs):
            self.__expand_button = viwid.widgets.button.Button(
                decoration=viwid.widgets.button.Decoration.NONE, class_style_name="tree_expander", is_focusable=False)
            self.__row_box = viwid.widgets.box.Box(children=[self.__expand_button, viwid.widgets.label.Label()])
            self.__children_box = viwid.widgets.box.Box(orientation=viwid.Orientation.VERTICAL)
            super().__init__(**{**dict(
                _children=[self.__row_box, self.__children_box],
                vertical_alignment=viwid.Alignment.FILL,
                layout=viwid.layout.GridLayout(viwid.layout.GridLayout.VERTICAL_PARTITIONER)), **kwargs})
            self.__refresh_expand_button()

        row: _Tree.Row | None
        @_Widget.Property
        def row(self, _):
            if not _:
                return
            self.__row_box._children[1] = _

        is_expanded: bool
        @_Widget.Property(default=lambda: False)
        def is_expanded(self, _):
            self.__refresh_expand_button()
            self.__children_box.is_visible = _

        def add_child(self, index, new_row):
            self.__children_box.children.insert(index, new_row)
            self.__refresh_expand_button()

        def remove_child(self, index, old_row):
            self.__children_box.children.pop(index)
            self.__refresh_expand_button()

        def _materialize(self):
            super()._materialize()

            self.__expand_button.listen_event(viwid.event.mouse.ClickEvent,
                                              self.__handle_expand_button_triggered,
                                              implements_default_behavior=True)
            self.row.listen_property("_depth", self.__handle_depth_changed)
            self.__handle_depth_changed()

        def _dematerialize(self):
            self.__expand_button.unlisten_event(self.__handle_expand_button_triggered)
            self.row.unlisten_property("_depth", self.__handle_depth_changed)

            super()._dematerialize()

        def __handle_depth_changed(self) -> None:
            self.__expand_button.margin = viwid.Margin(left=2 * self.row._depth, right=1)

        def __handle_expand_button_triggered(self, event: viwid.event.mouse.ClickEvent) -> None:
            self.row._host._set_row_expanded(self.row, not self.is_expanded)
            event.stop_handling()

        def __refresh_expand_button(self) -> None:
            self.__expand_button.text = (" " if not any(_.is_visible for _ in self.__children_box.children)
                                         else "v" if self.is_expanded else ">")
