#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
Data structures for numeric/arithmetic purposes.
"""
import typing as t


class NumericValueRange:
    """
    A range of numeric values with a minimal and a maximal value and a step size, used e.g. by sliders or scroll bars.

    The range is able to translate for each value between its native representation, "step numbers" and "normalized
    numbers". The latter ones can be convenient for various computation tasks.

    For step numbers, see :py:meth:`value_to_step_number`.
    For normalized numbers, see :py:meth:`value_to_normalized_number`.

    Whenever it does these translations, it automatically trims values to their allowed ranges and rounds them regarding
    the range's step size if needed. So you can always assume those numbers to represent valid values.

    It can also translate values to and from alien scales, i.e. integer scales with a minimum value of 0 and some
    maximum value. See :py:meth:`value_by_alien_scale`.
    """

    #: A numeric valid range with min_value=0, max_value=100, step_size=1.
    ZERO_TO_HUNDRED_BY_ONE: t.ClassVar["NumericValueRange"]

    def __init__(self, *, min_value: float, max_value: float, step_size: float):
        """
        :param min_value: The smallest allowed value in the range.
        :param max_value: The largest allowed value in the range. If it is < `min_value`, they automatically get turned.
        :param step_size: The interval between two allowed values. If it is negative, it automatically gets negated.
                          It must not be 0.
        """
        if min_value > max_value:
            min_value, max_value = max_value, min_value
        if step_size < 0:
            step_size *= -1
        elif step_size == 0:
            raise ValueError("step_size must not be 0")

        self.__step_count = step_count = int((max_value - min_value) / step_size + 0.5)
        max_value = min_value + step_count * step_size
        self.__min_value = min_value
        self.__max_value = max_value
        self.__step_size = step_size
        self.__value_range = max_value - min_value

    @property
    def distinct_values_count(self) -> int:
        """
        The number of distinct values in the range.
        """
        return self.__step_count + 1

    @property
    def min_value(self) -> float:
        """
        The smallest allowed value in the range.
        """
        return self.__min_value

    @property
    def max_value(self) -> float:
        """
        The largest allowed value in the range.
        """
        return self.__max_value

    @property
    def step_size(self) -> float:
        """
        The interval between two allowed values.
        """
        return self.__step_size

    def valid_value(self, value: float) -> float:
        """
        Return the input value trimmed to the allowed range and rounded to the next allowed value. So, for an input
        value that is already valid, this method is a no-op.

        :param value: The input value.
        """
        return self.step_number_to_value(self.value_to_step_number(value))

    def value_to_step_number(self, value: float) -> int:
        """
        Return the "step number" for a value, i.e. the number of steps away a given value is from the minimum value.

        This is an integer that fulfills 0 <= i < :py:attr:`distinct_values_count`.

        See also :py:meth:`step_number_to_value`.

        :param value: The value. Will automatically be trimmed to be between the range's minimum and maximum value
                      and rounded to next allowed value.
        """
        return min(max(0, int((value - self.__min_value) / self.__step_size + 0.5)), self.__step_count)

    def step_number_to_value(self, step_number: int) -> float:
        """
        Return the value associated to a given "step number" (see :py:meth:`value_to_step_number`).

        :param step_number: The step number. Will automatically be trimmed to be in the allowed range.
        """
        return self.__min_value + self.valid_step_number(step_number) * self.__step_size

    def valid_step_number(self, step_number: int) -> int:
        """
        Return the input step number (see :py:meth:`value_to_step_number`) trimmed to the allowed range. So, for an
        input step number that is already valid, this method is a no-op.

        :param step_number: The input step number.
        """
        return min(max(0, step_number), self.__step_count)

    def value_to_normalized_number(self, value: float) -> float:
        """
        Return the "normalized number" for a value, i.e. a value between 0 and 1, with 0 representing the range's
        minimum value and 1 representing its maximum value.

        See also :py:meth:`normalized_number_to_value`.

        :param value: The value. Will automatically be trimmed to be between the range's minimum and maximum value
                      and rounded to next allowed value.
        """
        if self.__value_range == 0:
            return 0.0
        return (self.valid_value(value) - self.__min_value) / self.__value_range

    def normalized_number_to_value(self, normalized_number: float) -> float:
        """
        Return the value associated to a given "normalized number" (see :py:meth:`value_to_normalized_number`).

        :param normalized_number: The normalized number. Will automatically be trimmed to be in the allowed range and
                                  rounded to the next allowed value.
        """
        return self.valid_value(self.__min_value + normalized_number * self.__value_range)

    def valid_normalized_number(self, normalized_number: float) -> float:
        """
        Return the input normalized number (see :py:meth:`value_to_normalized_number`) trimmed to the allowed range and
        rounded to the next allowed value. So, for an input normalized number that is already valid, this method is a
        no-op.

        :param normalized_number: The input normalized number.
        """
        return self.value_to_normalized_number(self.normalized_number_to_value(normalized_number))

    def value_by_alien_scale(self, *, alien_value: int, alien_max_value: int) -> float:
        """
        Translate a value from an alien scale to a valid value on this range. An alien scale is an integer scale with a
        minimum value of 0 and some maximum value.

        See also :py:meth:`value_to_alien_scale`.

        :param alien_value: The alien value to translate to a one native to this range. Will automatically be trimmed to
                            be in the allowed range.
        :param alien_max_value: The maximum value of the alien scale.
        """
        if alien_max_value == 0:
            return self.__min_value
        return self.normalized_number_to_value(alien_value / alien_max_value)

    def value_to_alien_scale(self, value: float, *, alien_max_value: int) -> int:
        """
        Translate a value from this range to an alien scale. An alien scale is an integer scale with a minimum value of
        0 and some maximum value.

        See also :py:meth:`value_by_alien_scale`.

        :param value: The value to translate to the alien scale. Will automatically be trimmed to be in the allowed
                      range and rounded to the next allowed value.
        :param alien_max_value: The maximum value of the alien scale.
        """
        if alien_max_value < 0:
            return alien_max_value
        return int(self.value_to_normalized_number(value) * alien_max_value + 0.5)


NumericValueRange.ZERO_TO_HUNDRED_BY_ONE = NumericValueRange(min_value=0, max_value=100, step_size=1)
