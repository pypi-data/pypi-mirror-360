#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
List variables.

See :py:class:`ListVariable`.
"""
import typing as t

import klovve.data
from klovve.variable.base import VariableBaseImpl


_T = t.TypeVar("_T")


class ListVariable(VariableBaseImpl[list[_T]], t.Generic[_T]):
    """
    List variables.

    A list variable is internally backed by an observable list (:py:class:`klovve.data.list.List`) that never gets
    replaced, i.e. :py:meth:`set_value` only replaces its content. Any changes on the list (either by
    :py:meth:`set_value` or by direct changes to the list by any external code) are considered as a change to this
    variable, i.e. the version will increment and the changed handlers will be called!
    """

    class _MyListObserver(klovve.data.list.List.Observer):

        def __init__(self, was_modified_func: t.Callable[[], None]):
            self.__was_modified_func = was_modified_func

        def item_added(self, index: int, item: object) -> None:
            self.__was_modified_func()

        def item_removed(self, index: int, item: object) -> None:
            self.__was_modified_func()

    def __init__(self, *, initial_content: t.Any = (), is_externally_settable: bool = True):
        """
        :param initial_content: The initial content.
        :param is_externally_settable: See :py:attr:`is_externally_settable`.
        """
        super().__init__(is_externally_settable=is_externally_settable)
        self.__list = klovve.data.list.List(initial_content, read_only=not is_externally_settable)
        self.__list.add_observer(self._MyListObserver, (lambda: self._changed(self.__list),),
                                 initialize_with=None, owner=self.__list)

    def _value(self):
        return self.__list

    def set_value(self, value, *, internally=False):
        if not (internally or self.is_externally_settable()):
            raise RuntimeError("this variable is not externally settable")

        self.__list._writable().set(value)
