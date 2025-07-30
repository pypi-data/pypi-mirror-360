#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
Klovve objects.

See :py:class:`Object`.
"""
import abc
import builtins
import enum
import typing as t

import klovve.data
import klovve.object.object_data
import klovve.variable
import klovve.debug
import klovve.effect


class Object:
    """
    A Klovve object.

    Klovve objects can have reactive properties, e.g. they can be observed (mostly by the infrastructure) for read
    accesses and even changes, e.g. in order to realize the foundation of :py:mod:`klovve.effect`.

    See :py:func:`property`, :py:func:`computed_property`, :py:func:`list_property` and similar.

    Do not implement this class directly. See :py:class:`klovve.model.Model`.
    """

    def __init__(self):
        klovve.debug.memory.new_object_created(Object, self)
        self.__data = klovve.object.object_data.FullObjectData(self)
        self.__data.initialize()
        self.__init_object__()

    def __getattribute__(self, item):
        if getattr(type(self), item, None) and (prop := self.__data.property_by_name(item)):
            value = self.__data.property_value(prop)
            klovve.debug.log.debug("get object property '%s' of '%s' (= <%s>)", item, self, value)
            return value

        return super().__getattribute__(item)

    def __setattr__(self, item, value):
        if getattr(type(self), item, None) and (prop := self.__data.property_by_name(item)):
            if not self.__data.is_property_settable(prop):
                raise AttributeError(f"property {item!r} of {self!r} object has no setter")
            klovve.debug.log.debug("set object property '%s' of %s to <%s>", item, self, value)
            return self.__data.set_property_value(prop, value)

        return super().__setattr__(item, value)

    def __init_object__(self):
        pass

    @builtins.property
    def _introspect(self) -> "klovve.object.object_data.ObjectData":
        return self.__data

    def _set_data_by_object(self, object_) -> None:
        self._set_data_by_kwargs({name: getattr(self._bind, name)
                                  for name, _ in object_._introspect.all_properties.items()})

    def _set_data_by_kwargs(self, kwargs) -> None:
        for name, value in kwargs.items():
            if isinstance(value, klovve.variable.Variable):
                if (prop := self._introspect.property_by_name(name)) and prop.is_settable:
                    klovve.effect.activate_effect(Object.__RefreshSelfEffect, (self, name, value), owner=self)
                if value.is_externally_settable():
                    klovve.effect.activate_effect(Object.__RefreshVariableEffect, (self, name, value), owner=self)
            else:
                setattr(self, name, value)

    class __RefreshSelfEffect(klovve.effect.Effect):

        def __init__(self, self_, prop_name, variable):
            super().__init__()
            self.__self = self_
            self.__prop_name = prop_name
            self.__variable = variable

        def run(self):
            new_value = self.__variable.value()
            klovve.debug.log.debug("refresh value of property '%s' from object %s on object side to <%s>",
                                   self.__prop_name, self.__self, new_value)
            setattr(self.__self, self.__prop_name, new_value)

    class __RefreshVariableEffect(klovve.effect.Effect):

        def __init__(self, piece, prop_name, variable):
            super().__init__()
            self.__self = piece
            self.__prop_name = prop_name
            self.__variable = variable

        def run(self):
            new_value = getattr(self.__self, self.__prop_name)
            klovve.debug.log.debug("refresh value of property '%s' from object %s on remote variable side to <%s>",
                                   self.__prop_name, self.__self, new_value)
            self.__variable.set_value(new_value)

    class _ObjectVariables[_T]:

        def __init__(self, object_: "Object", *, two_way: bool):
            self.__object = object_
            self.__two_way = two_way

        def __call__(self, *, two_way: bool) -> _T:
            return Object._ObjectVariables(self.__object, two_way=two_way)

        def __getattr__(self, item):
            prop = self.__object._introspect.property_by_name(item)
            if prop is None:
                raise AttributeError(f"{type(self.__object).__qualname__!r} object has no attribute {item!r}")

            with klovve.variable.no_dependency_tracking():
                getattr(self.__object, item)

            result = self.__object._introspect.variable(prop, lambda: None)
            if result is None:  # this should not really happen unless the property behaves oddly
                raise AttributeError(f"{type(self.__object).__qualname__!r} object has no attribute {item!r}")

            if not self.__two_way:
                result = Object._ReadOnlyWrappingVariable(result)

            return result

    @builtins.property
    def _bind(self) -> t.Self | _ObjectVariables[t.Self]:
        return Object._ObjectVariables(self, two_way=True)

    class _ReadOnlyWrappingVariable(klovve.variable.Variable):

        def __init__(self, original_variable: klovve.variable.Variable):
            super().__init__()
            self.__original_variable = original_variable

        def _value(self):
            return self.__original_variable._value()

        def set_value(self, value, *, internally=False):
            raise AttributeError("this property has no setter")

        def is_externally_settable(self):
            return False

        def current_version(self):
            return self.__original_variable.current_version()

        def add_changed_handler(self, handler):
            return self.__original_variable.add_changed_handler(handler)

        def remove_changed_handler(self, handler):
            return self.__original_variable.remove_changed_handler(handler)


class BaseProperty(abc.ABC):
    """
    Base class for a property of a Klovve object.
    """

    def __init__(self, *, is_settable: bool = True, initialize_lazily: bool = False,
                 value_has_fixed_identity: bool = False):
        """
        :param is_settable: Whether this property is settable.
        :param initialize_lazily: Whether to initialize this value lazily (relevant if initialization is expensive, like
                                  for some computed properties).
        :param value_has_fixed_identity: Whether this value has a fixed identity (like e.g. list properties).
        """
        self.__is_settable = is_settable
        self.__initialize_lazily = initialize_lazily
        self.__value_has_fixed_identity = value_has_fixed_identity

    @builtins.property
    def is_settable(self) -> bool:
        """
        Whether this property is settable.
        """
        return self.__is_settable

    @builtins.property
    def initialize_lazily(self) -> bool:
        """
        Whether to initialize this value lazily (relevant if initialization is expensive, like for some computed
        properties).
        """
        return self.__initialize_lazily

    @builtins.property
    def value_has_fixed_identity(self) -> bool:
        """
        Whether this value has a fixed identity (like e.g. list properties).
        """
        return self.__value_has_fixed_identity

    @abc.abstractmethod
    def value(self, obj_data: "klovve.object.object_data.FullObjectData") -> t.Any:
        """
        Return the value of this property from the given object data.

        :param obj_data: The object data.
        """

    @abc.abstractmethod
    def set_value(self, obj_data: "klovve.object.object_data.FullObjectData", value: t.Any) -> None:
        """
        Set the value of this property in the given object data.

        :param obj_data: The object data.
        :param value: The new value.
        """


class _IsFrozen: pass
_T = t.TypeVar("_T", bound=t.Any)
_T2 = t.TypeVar("_T2", bound=t.Any)
_TFrozenValue = t.Union[_IsFrozen, None, str, int, bool, float, enum.Enum, tuple["_TFrozenValue"]]
_TFrozenValueIterable = t.Iterable[_TFrozenValue]
_TFunc = t.Callable[[], t.Union[t.Awaitable[_T], _T]]  # actually  func: t.Callable[[object], :::]  - but IDE is stupid
_TFrozenValueOrGenerator = t.Union[_TFrozenValue, t.Callable[[], t.Any]]
__TFrozenValueIterableOrGenerator = t.Union[_TFrozenValueIterable, t.Callable[[], t.Iterable[t.Any]]]


# noinspection PyShadowingBuiltins
def property(is_settable: bool = True, initial: _TFrozenValueOrGenerator = lambda: None) -> builtins.property:
    """
    A simple scalar property.

    :param is_settable: Whether this property is settable from outside (it is always settable via introspection).
    :param initial: The initial value, either directly (if it is a simple type), or as a function that returns it.
    """
    initial = __to_generator_simple(initial)

    from klovve.object.prop import Property
    # noinspection PyTypeChecker
    return Property(is_settable=is_settable, initial=initial)


# noinspection PyShadowingBuiltins
def list_property(is_settable: bool = True,
                  initial: __TFrozenValueIterableOrGenerator = lambda: ()) -> builtins.property:
    """
    A list property.

    :param is_settable: Whether this property is settable from outside (it is always settable via introspection).
    :param initial: The initial list, either directly (if it contains only values of simple type), or as a function that
                    returns it.
    """
    initial = __to_generator_list(initial)

    from klovve.object.list_prop import ListProperty
    # noinspection PyTypeChecker
    return ListProperty(is_settable=is_settable, initial=initial)


def computed_property(func: _TFunc, *, async_initial: _TFrozenValueOrGenerator = lambda: None,
                      always_reset_to_async_initial: bool = False, initialize_lazily: bool = False) -> _T:
    """
    A computed property.

    :param func: The function that returns the property value.
    :param async_initial: If :code:`func` is async, this is the initial value, either directly (if it is a simple type),
                          or as a function that returns it.
    :param always_reset_to_async_initial: Whether to reset the property to the :code:`async_initial` value whenever the
                                          computation starts again.
    :param initialize_lazily: Whether to initialize this property lazily, i.e. compute it only as soon as accessed, not
                              during object creation.
    """
    async_initial = __to_generator_simple(async_initial)

    from klovve.object.computed_prop import ComputedProperty
    # noinspection PyTypeChecker
    return ComputedProperty(func, async_initial=async_initial,
                            always_reset_to_async_initial=always_reset_to_async_initial,
                            initialize_lazily=initialize_lazily)


def computed_list_property(func: _TFunc, *, async_initial: __TFrozenValueIterableOrGenerator = lambda: (),
                           always_reset_to_async_initial: bool = False, initialize_lazily: bool = False) -> _T:
    """
    A computed list property.

    :param func: The function that returns the property list.
    :param async_initial: If :code:`func` is async, this is the initial list, either directly (if it contains only
                          values of simple type), or as a function that returns it.
    :param always_reset_to_async_initial: Whether to reset the property to the :code:`async_initial` value whenever the
                                          computation starts again.
    :param initialize_lazily: Whether to initialize this property lazily, i.e. compute it only as soon as accessed, not
                              during object creation.
    """
    async_initial = __to_generator_list(async_initial)

    from klovve.object.computed_prop import ComputedProperty
    # noinspection PyTypeChecker
    return ComputedProperty(func, as_list=True, async_initial=async_initial,
                            always_reset_to_async_initial=always_reset_to_async_initial,
                            initialize_lazily=initialize_lazily)


ListTransformer = klovve.data.list_transformer.ListTransformer

# a better type hint for input_list_property would lead to warnings from static code analysis (e.g. in PyCharm)?
def transformed_list_property(transformer: ListTransformer[_T, _T2], *, input_list_property: object) -> list[_T2]:
    """
    A transformed list property. Each transformed list property is backed by an input list property and transforms
    elements from the input list to this list by a given transformer.

    :param transformer: The transformer that generates this list's elements out of the input list elements.
    :param input_list_property: The input list property.
    """
    from klovve.object.computed_prop import TransformedListProperty
    # noinspection PyTypeChecker
    return TransformedListProperty(input_list_property, transformer)


# a better type hint for input_list_property would lead to warnings from static code analysis (e.g. in PyCharm)?
def concatenated_list_property(*input_list_properties: object) -> list:
    """
    A concatenated list, assembled of given input lists.

    :param input_list_properties: The input list properties.
    """
    from klovve.object.computed_prop import ConcatenatedListProperty
    # noinspection PyTypeChecker
    return ConcatenatedListProperty(*input_list_properties)


def __to_generator_simple(v):
    if not callable(v):
        _v = v
        v = lambda: _v
    return v


def __to_generator_list(v):
    if not callable(v):
        _v = tuple(v or ())
        v = lambda: _v
    return v


class WithPublicBind(abc.ABC):
    """
    An object that has a :py:attr:`bind` attribute which returns the underlying variable for a property on a Klovve
    object.

    This is used for data bindings, mostly in view definitions.
    """

    @builtins.property
    @abc.abstractmethod
    def _bind(self):
        """
        Internally used by :py:attr:`bind`.
        """

    @builtins.property
    def bind(self) -> t.Self | Object._ObjectVariables[t.Self]:
        """
        A special object that returns the underlying variable for a property on this object.

        This is used for data bindings, mostly in view definitions.

        Assuming an object :code:`o` with a property :code:`o.p`, you get the bindable variable by :code:`o.bind.p`.
        """
        return self._bind
