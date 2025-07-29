#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import abc
import typing as t
import weakref

import klovve.object
import klovve.data
import klovve.variable
import klovve.debug

if t.TYPE_CHECKING:
    import klovve.object.computed_prop


class ObjectData(abc.ABC):

    def __init__(self):
        klovve.debug.memory.new_object_created(ObjectData, self)

    @property
    @abc.abstractmethod
    def object(self) -> "klovve.object.Object":
        pass

    @abc.abstractmethod
    def property_value(self, prop) -> t.Any:
        pass

    @abc.abstractmethod
    def set_property_value(self, prop, value: t.Any) -> None:
        pass

    @abc.abstractmethod
    def is_property_settable(self, prop) -> bool:
        pass

    @abc.abstractmethod
    def is_property_initialized_lazily(self, prop) -> bool:
        pass

    @abc.abstractmethod
    def property_value_has_fixed_identity(self, prop) -> bool:
        pass

    @property
    @abc.abstractmethod
    def all_properties(self) -> dict[str, "klovve.object.BaseProperty"]:
        pass

    @abc.abstractmethod
    def property_by_name(self, name: str) -> t.Optional["klovve.object.BaseProperty"]:
        pass

    @abc.abstractmethod
    def observe_list_property(self, prop,
                              observer: "type[klovve.data.list.List.Observer]",
                              observer_args=None, observer_kwargs=None, *,
                              initialize: bool = True, owner: object) -> klovve.data.list.List.Observer:
        pass

    @abc.abstractmethod
    def stop_observe_list_property(self, prop, observer: klovve.data.list.List.Observer) -> None:
        pass

    @abc.abstractmethod
    def refresh_computed_property(self, prop) -> None:
        pass


class FullObjectData(ObjectData):

    def __init__(self, object_: "klovve.object.Object"):
        super().__init__()
        self.__object_weakref = weakref.ref(object_)
        self.__variables = {}
        self.__properties, self.__property_names = self.__properties_from_object(object_)

    @property
    def object(self):
        return self.__object_weakref()

    def property_value(self, prop):
        prop = self.__actual_property(prop)
        return prop.value(self)

    def set_property_value(self, prop, value):
        prop = self.__actual_property(prop)
        prop.set_value(self, value)

    def is_property_settable(self, prop):
        prop = self.__actual_property(prop)
        return prop.is_settable

    def is_property_initialized_lazily(self, prop):
        prop = self.__actual_property(prop)
        return prop.initialize_lazily

    def property_value_has_fixed_identity(self, prop):
        prop = self.__actual_property(prop)
        return prop.value_has_fixed_identity

    @property
    def all_properties(self):
        return dict(self.__properties)

    def property_by_name(self, name):
        prop = self.__properties.get(name)
        if isinstance(prop, klovve.object.BaseProperty):
            return prop

    def observe_list_property(self, prop, observer, observer_args=None, observer_kwargs=None, *,
                              initialize=True, owner) -> "klovve.data.list.List.Observer":
        prop = self.__actual_property(prop)
        if not prop.value_has_fixed_identity:
            raise ValueError("only properties with a fixed identity (e.g. list properties) can be observed this way")

        with klovve.variable.no_dependency_tracking():
            prop_list: klovve.data.list.List = prop.value(self)
        return prop_list.add_observer(observer, observer_args, observer_kwargs, owner=owner,
                                      initialize_with=klovve.variable.no_dependency_tracking() if initialize else None)

    def stop_observe_list_property(self, prop, observer):
        prop = self.__actual_property(prop)
        with klovve.variable.no_dependency_tracking():
            prop_list: klovve.data.list.List = prop.value(self)
        prop_list.remove_observer(observer)

    def refresh_computed_property(self, prop):
        prop = self.__actual_property(prop)
        if isinstance(prop, klovve.object.computed_prop.AbstractComputedProperty):
            prop.refresh(self)

    def initialize(self):
        with klovve.variable.no_dependency_tracking():
            for prop in self.all_properties.values():
                if not self.is_property_initialized_lazily(prop):
                    prop.value(self)

    def variable(self, anchor: t.Any, create_variable_func: t.Callable) -> klovve.variable.Variable:
        if anchor not in self.__variables:
            self.__variables[anchor] = create_variable_func()

        return self.__variables[anchor]

    def __properties_from_object(self, object_):
        properties = {}
        property_names = {}

        for object_type in reversed(type(object_).mro()):
            for name, item in object_type.__dict__.items():
                if isinstance(item, klovve.object.BaseProperty):
                    properties[name] = item
                    property_names[item] = name

        return dict(sorted(properties.items())), property_names

    def __actual_property(self, prop):
        return self.__properties[self.__property_names[prop]]
