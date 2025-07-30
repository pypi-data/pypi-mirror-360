#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
Lists.

See :py:class:`List`.
"""
import abc
import collections.abc
import copy
import typing as t
import weakref


class List[T](collections.abc.MutableSequence[T]):
    """
    An observable list.

    Observable lists behave exactly as common Python lists (plus some additions), but can be observed for changes.
    """

    def __init__(self, content: t.Iterable = (), *, read_only: bool = False):
        """
        :param content: The initial content.
        :param read_only: Whether this list is read-only. See also :py:meth:`_writable`.
        """
        super().__init__()
        self.__content = list(content)
        self.__owner_by_observer = weakref.WeakValueDictionary()
        self.__read_only = read_only

    def _writable(self) -> "List[T]":
        """
        Return a writable proxy, even if this list is read-only.
        """
        writable_list = copy.copy(self)
        writable_list.__read_only = False
        return writable_list

    def __eq__(self, other):
        return (isinstance(other, list) or isinstance(other, List)) and (len(self) == len(other)) \
               and all(self[i] == other[i] for i in range(len(self)))

    def __len__(self):
        return len(self.__content)

    def __getitem__(self, i):
        return self.__content[i]

    def __delitem__(self, i):
        self.__verify_writable()
        i = self.__correct_index(i)
        old_v = self.__content.pop(i)

        for observer in self.__observers():
            observer.item_removed(i, old_v)

    def __setitem__(self, i, v):
        self.__verify_writable()
        if i >= len(self.__content):
            return self.insert(i, v)
        
        i = self.__correct_index(i)
        old_v = self.__content[i]
        self.__content[i] = v

        for observer in self.__observers():
            observer.item_replaced(i, old_v, v)

    def __bool__(self):
        return bool(self.__content)

    def insert(self, i, v):
        self.__verify_writable()
        i = self.__correct_index(i)
        self.__content.insert(i, v)

        for observer in self.__observers():
            observer.item_added(i, v)

    def __repr__(self):
        return repr(self.__content)

    def move(self, source_index: int, target_index: int) -> None:
        """
        Move an element.

        :param source_index: The old index.
        :param target_index: The new index.
        """
        self.__verify_writable()
        target_index = self.__correct_index(target_index)
        source_index = self.__correct_index(source_index)
        item = self.__content.pop(source_index)
        self.__content.insert(target_index, item)

        for observer in self.__observers():
            observer.item_moved(source_index, target_index, item)

    def set(self, other: t.Iterable[t.Any]) -> None:
        """
        Reset this list with the content of another one.
        """
        self.__verify_writable()
        other = tuple(other)
        import klovve.variable

        with klovve.variable.pause_refreshing():
            # very similar code is also used in viwid.data.list!
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
                        self.move(i_content, i_other)
                        for k, v in content_dict.items():
                            if (v_new := tuple(i + (1 if i < i_content else 0) for i in v)) != v:
                                content_dict[k] = v_new
                else:
                    self.insert(i_other, other_item_)
                    for k, v in content_dict.items():
                        content_dict[k] = tuple(i + 1 for i in v)

    def add_observer(self, observer: "type[Observer[T]]", observer_args=None, observer_kwargs=None, *,
                     initialize_with: t.ContextManager[None]|None, owner: t.Optional[object]) -> "Observer[T]":
        """
        Add an observer to this list.

        The lifetime of an observer can either be bound to the lifetime of a given owner object, or can be handled
        manually by calling :py:meth:`remove_observer`.

        :param observer: An observer type.
        :param observer_args: The observer args.
        :param observer_kwargs: The observer kwargs.
        :param initialize_with: Optional context manager to be used for instant calls about the status quo. If unset,
                                no initialization will happen.
        :param owner: The owner. If :py:code:`None`, lifetime is handled manually.
        """
        observer_ = observer(*(observer_args or ()), **(observer_kwargs or {}))

        self.__owner_by_observer[observer_] = observer_ if owner is None else owner

        if initialize_with is not None:
            with initialize_with:
                for index, item in enumerate(self.__content):
                    observer_.item_added(index, item)

        return observer_

    def remove_observer(self, observer: "Observer[T]") -> None:
        """
        Remove an observer that was added by :py:meth:`add_observer` before.

        :param observer: The observer to stop.
        """
        self.__owner_by_observer.pop(observer)

    def __verify_writable(self) -> None:
        if self.__read_only:
            raise TypeError("this list does not support modifications")

    def __correct_index(self, i: int) -> int:
        if i < 0:
            i += len(self.__content)
        return i

    def __observers(self) -> t.Iterable["Observer[T]"]:
        return self.__owner_by_observer.keys()

    class _HashableRepresentation:

        def __init__(self, object):
            self.object = object
            self.__id = id(object)

        def __hash__(self):
            return self.__id

        def __eq__(self, other):
            return isinstance(other, List._HashableRepresentation) and self.__id == other.__id

    class Observer[T](abc.ABC):
        """
        Abstract base class for objects that can listen to changes on a :py:class:`List`.
        """

        @abc.abstractmethod
        def item_added(self, index: int, item: T) -> None:
            """
            Called when an item was added to the observed list.

            :param index: The position where the new item was inserted.
            :param item: The new item.
            """

        @abc.abstractmethod
        def item_removed(self, index: int, item: T) -> None:
            """
            Called when an item was removed from the observed list.

            :param index: The position of the item that was removed.
            :param item: The removed item.
            """

        def item_moved(self, from_index: int, to_index: int, item: T) -> None:
            """
            Called when an item was moved inside the observed list.

            :param from_index: The old position of the element that was moved.
            :param to_index: The new position of the moved element.
            :param item: The moved item.
            """
            self.item_removed(from_index, item)
            self.item_added(to_index, item)

        def item_replaced(self, index: int, old_item: T, new_item: T) -> None:
            """
            Called when an item was replaced by another one in the observed list.

            :param index: The position where the item was replaced.
            :param old_item: The old item.
            :param new_item: The new item.
            """
            self.item_removed(index, old_item)
            self.item_added(index, new_item)
