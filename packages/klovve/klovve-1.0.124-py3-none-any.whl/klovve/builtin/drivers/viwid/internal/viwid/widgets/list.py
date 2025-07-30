#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
See :py:class:`List`.
"""
import typing as t

from viwid.widgets.tree import _Tree


class List(_Tree):
    """
    A list (of rows) that lets the user choose one item (or multiple if configured this way).

    After creation, no item is selected. The user (or the program logic that controls the list) explicitly has to select
    one to change that. If multi-selection is not allowed (the default), once an item is selected, the user cannot just
    unselect it anymore without selecting another one.
    """

    def _item_representation(self, row):
        return row

    def _is_row_expanded(self, row):
        return False

    def _set_row_expanded(self, row, expanded):
        pass

    def _child_item_added(self, in_row, index, new_row):
        raise RuntimeError("lists cannot have rows with child rows")

    def _child_item_removed(self, in_row, index, old_row):
        raise RuntimeError("lists cannot have rows with child rows")

    @property
    def selected_item_indexes(self) -> t.Sequence[int]:
        """
        The list of indexes of the selected items. Empty list by default.

        Whenever this changes, :py:class:`_Tree.SelectionChangedEvent` will be triggered as well.
        """
        return tuple(_[0] for _ in self._selected_item_indexes)

    @selected_item_indexes.setter
    def selected_item_indexes(self, _):
        self._selected_item_indexes = tuple((i,) for i in _)

    @property
    def active_item_index(self) -> int | None:
        """
        The index of the active item. :code:`None` by default.

        The active item is the same as the selected item as long as :py:attr:`allows_multi_select` is not enabled.
        Otherwise, the active item is the item that is currently 'focused', i.e. 'selected by means of mouse and
        keyboard'. This is not the user's actual selection, but just the item that the user _could_ toggle selection for
        next (or recently did).
        """
        if self._active_item_index is not None:
            return self._active_item_index[0]

    @active_item_index.setter
    def active_item_index(self, _):
        self._active_item_index = None if _ is None else (_,)

    def item_for_index(self, index: int) -> "_Tree.Row":
        """
        Return the item for a given index.

        :param index: The index.
        """
        return self._item_for_index((index,))
