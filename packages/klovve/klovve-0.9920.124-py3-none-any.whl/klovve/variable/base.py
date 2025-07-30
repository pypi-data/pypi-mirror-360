#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
Base infrastructure for variables.

See also :py:class:`Variable`.
"""
import abc
import contextlib
import contextvars
import typing as t
import weakref

import klovve.debug

_T = t.TypeVar("_T")


class Variable(t.Generic[_T], abc.ABC):
    """
    Base class for a Klovve variable.
    """

    class ChangedHandler(abc.ABC):
        """
        Base class for a variable changed handler.
        """

        @abc.abstractmethod
        def handle(self, variable: "Variable", value: _T, version: int) -> None:
            """
            Called when an observed variable has been changed.

            :param variable: The variable.
            :param value: The new value.
            :param version: The version number.
            """

    def __init__(self, *, is_externally_settable: bool = True):
        """
        :param is_externally_settable: See :py:attr:`is_externally_settable`.
        """
        klovve.debug.memory.new_object_created(Variable, self)
        self.__is_externally_settable = is_externally_settable

    def value(self) -> _T:
        """
        Return the current value of this variable (and call :py:func:`using_variable_getter_called_handler`).
        """
        if variable_getter_called_handler := _variable_getter_called_handler.get():
            variable_getter_called_handler(self)
        return self._value()

    @abc.abstractmethod
    def _value(self) -> _T:
        """
        Only return the current value of this variable.

        This is used internally by :py:meth:`value` only.
        """

    @abc.abstractmethod
    def set_value(self, value: _T, *, internally: bool = False) -> None:
        """
        Set the value of this variable.

        :param value: The new value.
        :param internally: Whether this is an internal action. If so, this will succeed even if not
                           :py:attr:`is_externally_settable`.
        """

    def is_externally_settable(self) -> bool:
        """
        Return whether this variable is settable.

        Note: Each variable is internally settable, as this is the only way a variable can be useful at all. Not all are
        intended to be writable externally, though. The exact meaning of 'internal' vs. 'external' is not precisely
        defined and not enforced in code (see the `internally` parameter of :py:meth:`set_value`). The concept is that
        there is some 'internal' code that controls a variable and sets it to a new value in some situations, but other
        code is only allowed to read the value.
        """
        return self.__is_externally_settable

    @abc.abstractmethod
    def current_version(self) -> int:
        """
        Return the current version of this variable.

        The version automatically increases whenever a new value is set to this variable.

        Note: An increased version number does not strictly imply that the value has been changed. It also increases
        when :py:meth:`set_value` is called with the value that it already had.
        """

    @abc.abstractmethod
    def add_changed_handler(self, handler: ChangedHandler) -> None:
        """
        Add a changed handler.

        It always gets called when :py:meth:`set_value` is used.

        See also :py:meth:`remove_changed_handler`.

        :param handler: The changed handler to add.
        """

    @abc.abstractmethod
    def remove_changed_handler(self, handler: ChangedHandler) -> None:
        """
        Remove a changed handler.

        :param handler: The changed handler to remove.
        """


class VariableBaseImpl(Variable[_T], t.Generic[_T], abc.ABC):
    """
    Base implementation for a :py:class:`Variable`.
    """

    def __init__(self, *, is_externally_settable: bool = True):
        """
        :param is_externally_settable: See :py:attr:`is_externally_settable`.
        """
        super().__init__(is_externally_settable=is_externally_settable)
        self.__changed_handlers_ = []
        self.__version = 0

    def current_version(self):
        return self.__version

    def add_changed_handler(self, handler):
        self.__changed_handlers()
        self.__changed_handlers_.append(weakref.ref(handler))

    def remove_changed_handler(self, handler):
        self.__changed_handlers(try_remove_handler=handler)

    def _changed(self, value: t.Any) -> None:
        """
        Called by implementations when the value has been changed, in order to do handle aspects like the variable
        version and changed handlers.

        :param value: The new value.
        """
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
    """
    Set a handler for read-accesses to all variables for a code block.

    Use it for a :code:`with` statement. There is always only one active handler! After the with-block, the former
    handler gets active again.

    :param func: The handler for read-accesses to all variables that happen inside the with-block.
    """
    old_variable_getter_called_handler = _variable_getter_called_handler.set(func)
    try:
        yield
    finally:
        _variable_getter_called_handler.reset(old_variable_getter_called_handler)


def no_dependency_tracking() -> t.ContextManager[None]:
    """
    Disable the current handler for read-accesses to variables for a code block.

    Use it for a :code:`with` statement.

    To application developers, this usually means that model property accesses do not count as a dependency in that
    :code:`with` block. It will not influence dependency tracking for other computations inside yours (i.e. if you
    access a computed property, the dependency tracking of this one will not break).
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
    """
    Pause the execution of variables' changed handlers for a code-block. Their execution does not get dropped (unless
    the redundant ones) but postponed to after the code-block.

    Use it for a :code:`with` statement.
    """
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
