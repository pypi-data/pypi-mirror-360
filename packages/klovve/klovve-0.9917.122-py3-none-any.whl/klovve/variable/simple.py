#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import typing as t

import klovve.debug
from klovve.variable.base import VariableBaseImpl


class SimpleVariable[T](VariableBaseImpl[T]):

    def __init__(self, *, initial_value: t.Any = None, is_externally_settable: bool = True):
        super().__init__(is_externally_settable=is_externally_settable)
        self.__value = initial_value

    def _value(self):
        klovve.debug.log.debug("get simple variable value of %s (= <%s>)", self, self.__value)
        return self.__value

    def set_value(self, value, *, internally=False):
        if not (internally or self.is_externally_settable()):
            raise RuntimeError("this variable is not externally settable")

        if self.__value != value:
            klovve.debug.log.debug("set simple variable value of %s to <%s>", self, value)
            self.__value = value
            self._changed(value)
