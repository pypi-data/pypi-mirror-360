#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import abc
import typing as t
import weakref

import klovve.object.object_data
import klovve.data
import klovve.variable
import klovve.debug


class AbstractComputedProperty(klovve.object.BaseProperty, abc.ABC):

    def __init__(self, *, as_list: bool, **kwargs):
        super().__init__(is_settable=False, **kwargs)
        self.__as_list = as_list

    def value(self, obj_data):
        if self.__as_list:
            is_uninitialized = self.__value__is_uninitialized__list
            create_variable_func = self.__value__create_variable__list
        else:
            is_uninitialized = self.__value__is_uninitialized__simple
            create_variable_func = self.__value__create_variable__simple

        variable = obj_data.variable(self, create_variable_func)

        if is_uninitialized(variable.value()):
            self._initialize(obj_data.object, variable)

        return variable.value()

    def set_value(self, obj_data, value: t.Any):
        raise RuntimeError("it is impossible to set the value of a computed property")

    @abc.abstractmethod
    def _initialize(self, object_: "klovve.object.Object", variable: "klovve.variable.Variable") -> None:
        pass

    @abc.abstractmethod
    def refresh(self, obj_data: "klovve.object.object_data.FullObjectData") -> None:
        pass

    def __value__is_uninitialized__simple(self, value):
        return value is self

    def __value__is_uninitialized__list(self, value):
        return len(value) == 1 and value[0] is self

    def __value__create_variable__simple(self):
        return klovve.variable.SimpleVariable(initial_value=self, is_externally_settable=False)

    def __value__create_variable__list(self):
        return klovve.variable.ListVariable(initial_content=(self,), is_externally_settable=False)


class AbstractEffectBasedComputedProperty(AbstractComputedProperty, abc.ABC):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__effects_by_variables = weakref.WeakKeyDictionary()

    def _initialize(self, object_, variable):
        self.__effects_by_variables[variable] = klovve.effect.activate_effect(self._ComputeVariableValueEffect,
                                                                              (object_, variable, self._run_effect),
                                                                              owner=variable)

    def refresh(self, obj_data: "klovve.object.object_data.FullObjectData") -> None:
        effect = self.__effects_by_variables.get(obj_data.variable(self, lambda: None))
        if effect:
            klovve.effect.rerun_effect_manually(effect)

    @abc.abstractmethod
    def _run_effect(self, object_: "klovve.object.Object", variable: "klovve.variable.Variable",
                    first_run: bool) -> None:
        pass

    class _ComputeVariableValueEffect(klovve.effect.Effect):

        def __init__(self, object_: "klovve.object.Object", variable: "klovve.variable.Variable",
                     run_effect_func):
            super().__init__()
            self.__object_weakref = weakref.ref(object_)
            self.__variable_weakref = weakref.ref(variable)
            self.__run_effect_func = run_effect_func
            self.__first_run = True

        def run(self):
            if (object_ := self.__object_weakref()) and (variable := self.__variable_weakref()):
                first_run, self.__first_run = self.__first_run, False
                return self.__run_effect_func(object_, variable, first_run)


class ComputedProperty(AbstractEffectBasedComputedProperty):

    def __init__(self, func: t.Callable[[object], t.Any], *, as_list: bool = False,
                 async_initial: t.Callable[[], t.Any], always_reset_to_async_initial: bool, **kwargs):
        super().__init__(as_list=as_list, value_has_fixed_identity=as_list, **kwargs)
        self.__func = func
        self.__async_initial = async_initial
        self.__always_reset_to_async_initial = always_reset_to_async_initial

    def _run_effect(self, object_, variable, first_run):
        new_value = self.__func(object_)

        if hasattr(new_value, "__await__"):
            if first_run or self.__always_reset_to_async_initial:
                variable.set_value(self.__async_initial(), internally=True)

            async def _():
                variable.set_value(await new_value, internally=True)

            return _()

        else:
            variable.set_value(new_value, internally=True)


class TransformedListProperty(AbstractComputedProperty):

    def __init__(self, input_list_property: "klovve.object.BaseProperty",
                 transformer: klovve.data.list_transformer.ListTransformer, **kwargs):
        super().__init__(as_list=True, **kwargs)
        self.__input_list_property = input_list_property
        self.__transformer = transformer

    def _initialize(self, object_, variable):
        variable.set_value([], internally=True)
        object_._introspect.observe_list_property(
            self.__input_list_property,
            klovve.data.list_transformer.TransformingListObserver, (variable.value()._writable(), self.__transformer),
            owner=object_)

    def refresh(self, obj_data):
        pass  # not supported so far


class ConcatenatedListProperty(AbstractComputedProperty):

    def __init__(self, *input_lists_properties: "klovve.object.BaseProperty", **kwargs):
        super().__init__(as_list=True, **kwargs)
        self.__input_lists_properties = input_lists_properties

    def _initialize(self, object_, variable):
        variable.set_value([], internally=True)
        after_lists = []
        for input_list_property in self.__input_lists_properties:
            object_._introspect.observe_list_property(
                input_list_property,
                klovve.data.list_transformer.ConcatenatingListObserver,
                (variable.value()._writable(), list(after_lists)),
                owner=object_)
            with klovve.variable.no_dependency_tracking():
                after_lists.append(object_._introspect.property_value(input_list_property))

    def refresh(self, obj_data):
        pass  # not supported so far
