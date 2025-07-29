#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import abc
import contextlib
import gettext
import locale
import pathlib
import typing as t

import klovve.data.list
import klovve.ui.materialization


class MaterializingViewListObserver[TNative](klovve.data.list.List.Observer, abc.ABC):

    def __init__(self, get_child_view_native_func: t.Callable[[t.Any], "klovve.ui.View"] = None):
        super().__init__()
        self.__get_child_view_native_func = get_child_view_native_func

    @abc.abstractmethod
    def _add_view_native(self, index: int, view_native: TNative) -> None:
        pass

    @abc.abstractmethod
    def _pop_view_native(self, index: int) -> TNative:
        pass

    @abc.abstractmethod
    def _materialize_view(self, view: "klovve.ui.View[TNative]") -> "klovve.ui.materialization.ViewMaterialization[klovve.ui.View[TNative], TNative]":
        pass

    def item_added(self, index, item):
        self._add_view_native(index, (self._materialize_view(item).native if self.__get_child_view_native_func is None
                                      else self.__get_child_view_native_func(item)))

    def item_removed(self, index, item):
        self._pop_view_native(index)

    def item_moved(self, from_index, to_index, item):
        self._add_view_native(to_index, self._pop_view_native(from_index))


class InternalTranslations:

    _custom_translation_dicts = []

    @staticmethod
    def _init():
        for localedir in [None, pathlib.Path(__file__).parent / "_mo"]:
            if gettext.find("klovve", localedir):
                locale.bindtextdomain("klovve", localedir)
                gettext.bindtextdomain("klovve", localedir)
                break

    _init()

    @staticmethod
    def _translate(s: str) -> str:
        for custom_translation_dict in reversed(InternalTranslations._custom_translation_dicts):
            if (answer := custom_translation_dict.get(s)) is not None:
                return answer
        return gettext.dgettext("klovve", s)

    @staticmethod
    @contextlib.contextmanager
    def customized(custom_translation_dict: dict[str, str]):
        InternalTranslations._custom_translation_dicts.append(custom_translation_dict)
        try:
            yield
        finally:
            InternalTranslations._custom_translation_dicts.remove(custom_translation_dict)


def tr(s: str) -> str:
    return InternalTranslations._translate(s)
