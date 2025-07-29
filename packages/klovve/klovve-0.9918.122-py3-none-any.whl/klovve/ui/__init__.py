#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import abc
import builtins
import enum
import typing as t

import klovve.object
import klovve.effect
import klovve.debug
import klovve.timer
import klovve.variable
import klovve.ui.materialization

from klovve.object import (property, list_property, computed_property, computed_list_property,
                           transformed_list_property, concatenated_list_property, ListTransformer)

if t.TYPE_CHECKING:
    import klovve.ui.dialog


@t.dataclass_transform(kw_only_default=True)
class _View[TMaterialization](klovve.event._EventHandlingObject, klovve.timer._TimingObject, klovve.object.Object,
                              klovve.object.WithPublicBind, abc.ABC):

    def __init__(self, **kwargs):
        super().__init__()
        self._set_data_by_kwargs(kwargs)
        self._initialize_timing()
        klovve.debug.memory.new_object_created(View, self)

    @abc.abstractmethod
    def _materialize(self, materializer: "klovve.ui.materialization.PieceMaterializer[TMaterialization]") -> None:
        pass

    @builtins.property
    @abc.abstractmethod
    def _materialization(self) -> "klovve.ui.materialization.ViewMaterialization[t.Self, TMaterialization]":
        pass

    @builtins.property
    @abc.abstractmethod
    def application(self) -> "klovve.app.BaseApplication":
        pass

    @abc.abstractmethod
    def trigger_event(self, event: "klovve.event.Event") -> None:
        pass


class Align(enum.Enum):
    START = enum.auto()
    CENTER = enum.auto()
    END = enum.auto()
    FILL = enum.auto()
    FILL_EXPANDING = enum.auto()


class Layout(klovve.object._IsFrozen):

    def __init__(self, align: Align = Align.FILL_EXPANDING, *, min_size_em: t.Optional[float] = None):
        self.__align = align
        self.__min_size_em = min_size_em

    @builtins.property
    def align(self) -> Align:
        return self.__align

    @builtins.property
    def min_size_em(self) -> t.Optional[float]:
        return self.__min_size_em


class Margin(klovve.object._IsFrozen):

    def __init__(self, all_em: t.Optional[float] = None, *,
                 vertical_em: t.Optional[float] = None, horizontal_em: t.Optional[float] = None,
                 top_em: t.Optional[float] = None, right_em: t.Optional[float] = None,
                 bottom_em: t.Optional[float] = None, left_em: t.Optional[float] = None):
        self.__top_em = self.__value(top_em, vertical_em, all_em)
        self.__right_em = self.__value(right_em, horizontal_em, all_em)
        self.__bottom_em = self.__value(bottom_em, vertical_em, all_em)
        self.__left_em = self.__value(left_em, horizontal_em, all_em)

    @builtins.property
    def top_em(self) -> float:
        return self.__top_em

    @builtins.property
    def left_em(self) -> float:
        return self.__left_em

    @builtins.property
    def bottom_em(self) -> float:
        return self.__bottom_em

    @builtins.property
    def right_em(self) -> float:
        return self.__right_em

    def __value(self, *values: t.Optional[float]) -> float:
        for value in values:
            if value is not None:
                return value
        return 0


class View[TMaterialization](_View[TMaterialization], abc.ABC):

    is_visible: bool = property(initial=True)

    is_enabled: bool = property(initial=True)

    horizontal_layout: Layout = property(initial=Layout(Align.FILL_EXPANDING))
    vertical_layout: Layout = property(initial=Layout(Align.FILL_EXPANDING))

    margin: Margin = property(initial=Margin(all_em=0))


class _BaseView[TMaterialization](View[TMaterialization], abc.ABC):

    def _materialize(self, materializer):
        self.__materialization = self._materialization_from_materializer(materializer)

    @builtins.property
    def _materialization(self):
        return getattr(self, "_BaseView__materialization", None)

    @builtins.property
    def application(self):
        result = self
        while not isinstance(result, klovve.app.BaseApplication):
            result = self._materialization.application_tree.parent_node(result)
        return result

    @abc.abstractmethod
    def _materialization_from_materializer(
            self,
            materializer: "klovve.ui.materialization.PieceMaterializer[TMaterialization]"
    ) -> "klovve.ui.materialization.ViewMaterialization[t.Self, TMaterialization]":
        pass

    def trigger_event(self, event):
        with klovve.variable.no_dependency_tracking():
            self._materialization.event_controller.trigger_event(self, event)


class Piece(_BaseView):

    def _materialization_from_materializer(self, materializer):
        return materializer.materialize_piece(self)


class ComposedView[TModel](_BaseView, abc.ABC):

    model: TModel = property()

    @abc.abstractmethod
    def compose(self):
        pass

    def _materialization_from_materializer(self, materializer):
        if self.__placeholder is None:
            self.__placeholder_ = klovve.views.Placeholder(is_visible=self.bind.is_visible,
                                                           is_enabled=self.bind.is_enabled,
                                                           horizontal_layout=self.bind.horizontal_layout,
                                                           vertical_layout=self.bind.vertical_layout,
                                                           margin=self.bind.margin)

            klovve.effect.activate_effect(self.__compose, owner=self)

            self.__placeholder._materialize(materializer)
        return self.__placeholder._materialization

    @builtins.property
    def __placeholder(self):
        return getattr(self, "_ComposedView__placeholder_", None)

    def __compose(self):
        self.__placeholder.body = self.compose()


from klovve.ui.utils import InternalTranslations as _InternalTranslations

def custom_internal_translations(custom_translation_dict: dict[str, str]) -> t.Generator[None, None, None]:
    return _InternalTranslations.customized(custom_translation_dict)
