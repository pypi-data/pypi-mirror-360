#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import abc
import contextlib
import contextvars
import typing as t
import weakref

import klovve.debug

_T = t.TypeVar("_T")


class Variable(t.Generic[_T], abc.ABC):

    class ChangedHandler(abc.ABC):

        @abc.abstractmethod
        def handle(self, variable: "Variable", value: _T, version: int) -> None:
            pass

    def __init__(self):
        klovve.debug.memory.new_object_created(Variable, self)

    def value(self) -> _T:
        if variable_getter_called_handler := _variable_getter_called_handler.get():
            variable_getter_called_handler(self)
        return self._value()

    @abc.abstractmethod
    def _value(self) -> _T:
        pass

    @abc.abstractmethod
    def set_value(self, value: _T, *, internally: bool = False) -> None:
        pass

    @abc.abstractmethod
    def is_externally_settable(self) -> bool:
        pass

    @abc.abstractmethod
    def current_version(self) -> int:
        pass

    @abc.abstractmethod
    def add_changed_handler(self, handler: ChangedHandler) -> None:
        pass

    @abc.abstractmethod
    def remove_changed_handler(self, handler: ChangedHandler) -> None:
        pass


class VariableBaseImpl(Variable[_T], t.Generic[_T], abc.ABC):

    def __init__(self, *, is_externally_settable: bool = True):
        super().__init__()
        self.__changed_handlers_ = []
        self.__version = 0
        self.__is_externally_settable = is_externally_settable

    def is_externally_settable(self):
        return self.__is_externally_settable

    def current_version(self):
        return self.__version

    def add_changed_handler(self, handler):
        self.__changed_handlers()
        self.__changed_handlers_.append(weakref.ref(handler))

    def remove_changed_handler(self, handler):
        self.__changed_handlers(try_remove_handler=handler)

    def _changed(self, value: t.Any) -> None:
        self.__version = version = self.__version + 1

        for changed_handler in self.__changed_handlers():
            _call_changed_handler(changed_handler, self, value, version)

    def __changed_handlers(self, *, try_remove_handler=None) -> t.Iterable[Variable.ChangedHandler]:
        result = []
        for i, changed_handler_weakref in reversed(list(enumerate(self.__changed_handlers_))):
            changed_handler = changed_handler_weakref()
            if (changed_handler is None) or (changed_handler is try_remove_handler):
                self.__changed_handlers_.pop(i)
            else:
                result.append(changed_handler)
        return result


_variable_getter_called_handler: contextvars.ContextVar[t.Optional[t.Callable]] = \
    contextvars.ContextVar("_variable_getter_called_handlers", default=None)


@contextlib.contextmanager
def using_variable_getter_called_handler(func: t.Callable[[Variable], None]) -> t.Generator[None, None, None]:
    old_variable_getter_called_handler = _variable_getter_called_handler.set(func)
    try:
        yield
    finally:
        _variable_getter_called_handler.reset(old_variable_getter_called_handler)


def no_dependency_tracking() -> t.ContextManager[None]:
    """
    Disable dependency tracking of the current computation for a code block.

    Use it for a :code:`with` statement. Model property accesses do not count as a dependency in that :code:`with`
    block.

    It will not influence dependency tracking for other computations inside yours (i.e. if you access a computed
    property, the dependency tracking of this one will not break).
    """
    return using_variable_getter_called_handler(_noop)


def _noop(*args, **kwargs):
    pass


def _call_changed_handler(changed_handler: Variable.ChangedHandler, variable: Variable, value: t.Any,
                          version: int) -> None:
    global _defer_changed_handling, _defer_changed_handling_for

    if _defer_changed_handling_for is None:
        changed_handler.handle(variable, value, version)

    else:
        _defer_changed_handling_for.append((changed_handler, variable, value, version))


_defer_changed_handling = 0
_defer_changed_handling_for: t.Optional[list[tuple[Variable.ChangedHandler, Variable, t.Any, int]]] = None


@contextlib.contextmanager
def pause_refreshing() -> t.Generator[None, None, None]:
    global _defer_changed_handling, _defer_changed_handling_for

    if _defer_changed_handling == 0:
        _defer_changed_handling_for = []
    _defer_changed_handling += 1

    try:
        yield

    finally:
        _defer_changed_handling -= 1
        if _defer_changed_handling == 0:
            change_tuples = []
            change_tuples_seen_prefixes = set()

            for changed_handler, variable, value, version in reversed(_defer_changed_handling_for):
                if (changed_handler, variable) not in change_tuples_seen_prefixes:
                    change_tuples_seen_prefixes.add((changed_handler, variable))
                    change_tuples.append((changed_handler, variable, value, version))

            _defer_changed_handling_for = None

            for changed_handler, variable, value, version in reversed(change_tuples):
                _call_changed_handler(changed_handler, variable, value, version)
