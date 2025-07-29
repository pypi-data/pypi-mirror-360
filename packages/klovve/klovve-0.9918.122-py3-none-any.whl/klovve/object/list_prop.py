#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import typing as t

import klovve.object.object_data
import klovve.variable


class ListProperty(klovve.object.BaseProperty):

    def __init__(self, *, initial: t.Callable[[], t.Iterable[t.Any]] = lambda: (), **kwargs):
        super().__init__(value_has_fixed_identity=True, **kwargs)
        self.__initial = initial

    def value(self, obj_data):
        return self.__variable(obj_data).value()

    def set_value(self, obj_data, value: t.Iterable[t.Any]):
        self.__variable(obj_data).set_value(value, internally=True)

    def __variable(self, obj_data: "klovve.object.object_data.FullObjectData") -> klovve.variable.Variable:
        return obj_data.variable(self, lambda: klovve.variable.ListVariable(initial_content=self.__initial(),
                                                                            is_externally_settable=self.is_settable))
