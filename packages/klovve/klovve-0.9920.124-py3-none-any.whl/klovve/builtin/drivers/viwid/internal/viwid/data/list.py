#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
Data structures for list handling.
"""
import collections.abc
import typing as t


class List[T](collections.abc.MutableSequence):
    """
    A list that can be observed.
    """

    def __init__(self, content: t.Iterable[T] = ()):
        super().__init__()
        self.__content = list(content)
        self.__observers: list["ListObserver"] = []

    def __eq__(self, other):
        return self.__content == other

    def __len__(self):
        return len(self.__content)

    def __getitem__(self, i):
        return self.__content[i]

    def __delitem__(self, i):
        i = self.__correct_index(i)
        v = self.__content.pop(i)
        for observer in self.__observers:
            observer.item_removed(i, v)

    def __setitem__(self, i, v):
        i = self.__correct_index(i)
        old_v, self.__content[i] = self.__content[i], v
        for observer in self.__observers:
            observer.item_replaced(i, old_v, v)

    def insert(self, i, v):
        i = self.__correct_index(i)
        self.__content.insert(i, v)
        for observer in self.__observers:
            observer.item_added(i, v)

    def __repr__(self):
        return repr(self.__content)

    def update(self, other: t.Sequence) -> None:
        # very similar code is also used in klovve.data.list!
        other = tuple(other)
        other_dict = collections.defaultdict(lambda: 0)
        for other_item in other:
            try:
                other_dict[other_item] += 1
            except TypeError:
                other_dict[List._HashableRepresentation(other_item)] += 1

        for i_content, content_item in reversed(tuple(enumerate(self.__content))):
            try:
                content_item_counter = other_dict[content_item]
            except TypeError:
                content_item_counter = other_dict[content_item := List._HashableRepresentation(content_item)]
            if content_item_counter > 0:
                other_dict[content_item] -= 1
            else:
                self.pop(i_content)

        content_dict = collections.defaultdict(lambda: ())
        for i_content, content_item in enumerate(self.__content):
            try:
                content_dict_old_tuple = content_dict[content_item]
            except TypeError:
                content_dict_old_tuple = content_dict[content_item := List._HashableRepresentation(content_item)]
            content_dict[content_item] = (*content_dict_old_tuple, i_content)

        for i_other, other_item in enumerate(other):
            other_item_ = other_item
            try:
                content_indexes = content_dict[other_item]
            except TypeError:
                content_indexes = content_dict[other_item := List._HashableRepresentation(other_item)]

            if content_indexes:
                i_content, remaining_content_indexes = content_indexes[0], content_indexes[1:]
                if remaining_content_indexes:
                    content_dict[other_item] = remaining_content_indexes
                else:
                    content_dict.pop(other_item)
                if i_other != i_content:
                    self.insert(i_other, self.pop(i_content))
                    for k, v in content_dict.items():
                        if (v_new := tuple(i + (1 if i < i_content else 0) for i in v)) != v:
                            content_dict[k] = v_new
            else:
                self.insert(i_other, other_item_)
                for k, v in content_dict.items():
                    content_dict[k] = tuple(i + 1 for i in v)

    def add_observer(self, observer: "ListObserver[T]" , *, initialize: bool = True) -> None:
        """
        Add a new observer to this list.

        See also :py:meth:`remove_observer`.

        :param observer: The observer to add.
        :param initialize: Whether to instantly run `item_added_func` now for all items in the list.
        """
        self.__observers.append(observer)

        if initialize:
            for index, item in enumerate(self.__content):
                observer.item_added(index, item)

    def add_observer_functions(self, item_added_func: t.Callable[[int, T], None],
                               item_removed_func: t.Callable[[int, T], None],
                               item_replaced_func: t.Callable[[int, T, T], None]|None = None , *,
                               initialize: bool = True) -> "ListObserver":
        """
        Add new observing functions to this list.

        Returns a :py:class:`ListObserver` for later removal.

        :param item_added_func: The function to call when a new item was added.
        :param item_removed_func: The function to call when an item was removed.
        :param item_replaced_func: The function to call when an item was replaced. If not specified, it will consider
                                   such a case as a removal followed by an addition.
        :param initialize: Whether to instantly run `item_added_func` now for all items in the list.
        """
        observer = ListObserver()
        observer.item_added = item_added_func
        observer.item_removed = item_removed_func
        if item_replaced_func:
            observer.item_replaced = item_replaced_func

        self.add_observer(observer, initialize=initialize)

        return observer

    def remove_observer(self, observer: "ListObserver") -> None:
        """
        Remove an observer. See :py:meth:`add_observer`.

        :param observer: The observer to remove.
        """
        self.__observers.append(observer)

    def __correct_index(self, i: int) -> int:
        if i < 0:
            i += len(self.__content)
        return i

    class _HashableRepresentation:

        def __init__(self, object):
            self.object = object
            self.__id = id(object)

        def __hash__(self):
            return self.__id

        def __eq__(self, other):
            return isinstance(other, List._HashableRepresentation) and self.__id == other.__id


class ListObserver[T]:
    """
    A list observer.
    """

    def item_added(self, index: int, item: T) -> None:
        """
        Handle a new item to be added to the list.

        :param index: The insertion position.
        :param item: The new item.
        """
        raise NotImplementedError()

    def item_removed(self, index: int, item: T) -> None:
        """
        Handle an item to be removed from the list.

        :param index: The removal position.
        :param item: The removed item.
        """
        raise NotImplementedError()

    def item_replaced(self, index: int, old_item: T, new_item: T) -> None:
        """
        Handle an item to be replaced by a new one in the list.

        :param index: The replacement position.
        :param old_item: The item that was replaced.
        :param new_item: The new item.
        """
        self.item_removed(index, old_item)
        self.item_added(index, new_item)
