#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import builtins
import typing as t

import klovve.object.object_data
import klovve.variable


class Property(klovve.object.BaseProperty):

    def __init__(self, *, initial: t.Callable[[], t.Any] = lambda: None, **kwargs):
        super().__init__(**kwargs)
        self.__initial = initial

    def value(self, obj_data):
        return self.__variable(obj_data).value()

    def set_value(self, obj_data, value: t.Any):
        self.__variable(obj_data).set_value(value, internally=True)

    def __variable(self, obj_data: "klovve.object.object_data.FullObjectData") -> klovve.variable.Variable:
        return obj_data.variable(self, lambda: klovve.variable.SimpleVariable(initial_value=self.__initial(),
                                                                              is_externally_settable=self.is_settable))
