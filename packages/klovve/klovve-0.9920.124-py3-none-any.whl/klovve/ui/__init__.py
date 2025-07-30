#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
Foundation for UI elements.

See :py:class:`View`.
"""
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
        """
        Materialize the view.

        This needs to be called in order to make :py:attr:`_materialization` (and implicitly a lot more) available.

        Called by the infrastructure.

        :param materializer: The piece materializer to use for creating the materializations.
        """

    @builtins.property
    @abc.abstractmethod
    def _materialization(self) -> "klovve.ui.materialization.ViewMaterialization[t.Self, TMaterialization]":
        """
        The view materialization.

        Only allowed to be queried on materialized views. See :py:meth:`_materialize`.
        """

    @builtins.property
    @abc.abstractmethod
    def application(self) -> "klovve.app.BaseApplication":
        """
        The associated application.

        Only allowed to be queried on materialized views. See :py:meth:`_materialize`.
        """

    @abc.abstractmethod
    def trigger_event(self, event: "klovve.event.Event") -> None:
        """
        Trigger an event on this view, usually bubbling upwards the ancestors, until the event propagation gets stopped.

        Only allowed to be called on materialized views. See :py:meth:`_materialize`.

        :param event: The event to trigger.
        """


class Align(enum.Enum):
    """
    How to align a view.
    """

    #: Align the view to the start location (i.e. left for horizontal and top for vertical definitions).
    START = enum.auto()

    #: Align the view to the center.
    CENTER = enum.auto()

    #: Align the view to the end location (i.e. right for horizontal and bottom for vertical definitions).
    END = enum.auto()

    #: Align the view by filling the entire size.
    FILL = enum.auto()

    #: Align the view by filling the entire size and also claim additional space if available.
    FILL_EXPANDING = enum.auto()


class Layout(klovve.object._IsFrozen):
    """
    A layout defines how to position and size a view in its available area.
    """

    def __init__(self, align: Align = Align.FILL_EXPANDING, *, min_size_em: t.Optional[float] = None):
        """
        :param align: How to align the view.
        :param min_size_em: Minimum size of the view. In 'em'.
        """
        self.__align = align
        self.__min_size_em = min_size_em

    @builtins.property
    def align(self) -> Align:
        """
        How to align the view.
        """
        return self.__align

    @builtins.property
    def min_size_em(self) -> t.Optional[float]:
        """
        Minimum size of the view. In 'em'.
        """
        return self.__min_size_em


class Margin(klovve.object._IsFrozen):
    """
    Margin definitions.

    A margin has a size component for each edge of a view, i.e. top, right, bottom and left. All sizes are floating
    point values in 'em' unit.
    """

    def __init__(self, all_em: t.Optional[float] = None, *,
                 vertical_em: t.Optional[float] = None, horizontal_em: t.Optional[float] = None,
                 top_em: t.Optional[float] = None, right_em: t.Optional[float] = None,
                 bottom_em: t.Optional[float] = None, left_em: t.Optional[float] = None):
        """
        :param all_em: Margin value for all edges.
        :param vertical_em: Margin value for top and bottom edges.
        :param horizontal_em: Margin value for right and left edges.
        :param top_em: Margin value for the top edge.
        :param right_em: Margin value for the right edge.
        :param bottom_em: Margin value for the bottom edge.
        :param left_em: Margin value for the left edge.
        """
        self.__top_em = self.__value(top_em, vertical_em, all_em)
        self.__right_em = self.__value(right_em, horizontal_em, all_em)
        self.__bottom_em = self.__value(bottom_em, vertical_em, all_em)
        self.__left_em = self.__value(left_em, horizontal_em, all_em)

    @builtins.property
    def top_em(self) -> float:
        """
        Margin value for the top edge.
        """
        return self.__top_em

    @builtins.property
    def left_em(self) -> float:
        """
        Margin value for the left edge.
        """
        return self.__left_em

    @builtins.property
    def bottom_em(self) -> float:
        """
        Margin value for the bottom edge.
        """
        return self.__bottom_em

    @builtins.property
    def right_em(self) -> float:
        """
        Margin value for the right edge.
        """
        return self.__right_em

    def __value(self, *values: t.Optional[float]) -> float:
        for value in values:
            if value is not None:
                return value
        return 0


class View[TMaterialization](_View[TMaterialization], abc.ABC):
    """
    Base class for a view.

    Views can have reactive properties, e.g. they can be observed (mostly by the infrastructure) for read accesses
    and even changes, e.g. in order to realize the foundation of :py:mod:`klovve.effect`. They can also have timer and
    event handlers.

    View implementations usually do no directly subclass this one, but more specific ones, like
    :py:class:`Piece` or :py:class:`ComposedView`.
    """

    #: Whether this view is visible. Note: Even if :code:`True`, it might in fact be invisible, e.g. because its parent
    #: view is invisible.
    is_visible: bool = property(initial=True)

    #: Whether this view is enabled. Note: Even if :code:`True`, it might in fact be disabled, e.g. because its parent
    #: view is disabled.
    is_enabled: bool = property(initial=True)

    #: The horizontal layout.
    horizontal_layout: Layout = property(initial=Layout(Align.FILL_EXPANDING))
    #: The vertical layout.
    vertical_layout: Layout = property(initial=Layout(Align.FILL_EXPANDING))

    #: The margin.
    margin: Margin = property(initial=Margin(all_em=0))


class _BaseView[TMaterialization](View[TMaterialization], abc.ABC):
    """
    Base implementation for a view.

    This is an implementation of the materialization aspects of :py:class:`View` but only serves as an internal base
    class of some more specific ones.
    """

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
        """
        Create and return a materialization for this view, using a given piece materializer.

        :param materializer: The piece materializer to use for creating the materializations.
        """

    def trigger_event(self, event):
        with klovve.variable.no_dependency_tracking():
            self._materialization.event_controller.trigger_event(self, event)


class Piece(_BaseView):
    """
    Base class for views that can directly be translated to a native representation by the current
    :py:class:`klovve.driver.Driver`.

    Most of the views that are bundled by Klovve (see :py:mod:`klovve.views`) are pieces. Also, it is very hard to
    implement custom pieces, as this would also need to implement view materializations for each targeted driver.
    """

    def _materialization_from_materializer(self, materializer):
        """
        Return the materialization for this view, using a given piece materializer.

        :param materializer: The piece materializer to use.
        """
        return materializer.materialize_piece(self)


class ComposedView[TModel](_BaseView, abc.ABC):
    """
    Base class for views composed of child views.

    This is useful for custom views.
    """

    model: TModel = property()

    @abc.abstractmethod
    def compose(self):
        """
        Compose this view and return the root view of this composition.

        This method will automatically be called when this view gets materialized, but also later in a reactive way,
        whenever a referenced variable got changed (this does not include
        :py:attr:`klovve.object.WithPublicBind.bind` usage). So it will always refresh to the current state, even for
        direct variable references.

        Whenever you can, as always, it is recommended to use :py:attr:`klovve.object.WithPublicBind.bind` instead of
        direct variable access.
        """

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
    """
    Use custom translations for Klovve texts for a code block. Typically used in order to provide translations for
    Klovve texts in languages that are not supported natively by Klovve.

    This does not address translation for applications' own texts. They are directly handled by means of :code:`gettext`
    or any other way. It is only for the texts that come directly from Klovve. In order to find a list of them, see
    Klovve's .po files.

    Use it for a :code:`with` statement.

    :param custom_translation_dict: The dictionary that contains custom translations for some Klovve texts.
    """
    return _InternalTranslations.customized(custom_translation_dict)
