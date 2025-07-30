#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
View materializations.

See :py:class:`ViewMaterialization`.
"""
import abc

import klovve.app.tree
import klovve.debug
import klovve.event.controller
import klovve.object
import klovve.ui


class ViewMaterialization[TView: "klovve.ui.View", TNative](klovve.object.Object, abc.ABC):
    """
    View materializations connect views to their application and translate them to their native, driver-specific
    representation.
    """

    def __init__(self, view: TView, event_controller: "klovve.event.controller.EventController[klovve.ui.View]",
                 application_tree: "klovve.app.tree.MaterializationObservingApplicationTree"):
        """
        :param view: The associated view.
        :param event_controller: The event controller.
        :param application_tree: The application tree.
        """
        self.__view = view
        super().__init__()
        klovve.debug.memory.new_object_created(ViewMaterialization, self)
        self.__event_controller = event_controller
        self.__application_tree = application_tree
        self.__native = None

    @property
    def piece(self) -> TView:
        """
        The associated view.
        """
        return self.__view

    @property
    def event_controller(self) -> "klovve.event.controller.EventController[klovve.ui.View]":
        """
        The event controller.
        """
        return self.__event_controller

    @property
    def application_tree(self) -> "klovve.app.tree.MaterializationObservingApplicationTree":
        """
        The application tree.
        """
        return self.__application_tree

    @abc.abstractmethod
    def create_native(self) -> TNative:
        """
        Create the native, driver-specific representation for the associated view.

        This is only used internally. See :py:attr:`native`.
        """

    @property
    def native(self) -> TNative:
        """
        The native, driver-specific representation for the associated view.
        """
        if self.__native is None:
            self.__native = self.create_native()
        return self.__native


class PieceMaterializer[T: ViewMaterialization](abc.ABC):
    """
    Piece materializers are responsible for translating a :py:class:`klovve.ui.Piece` to a
    :py:class:`ViewMaterialization`.
    """

    @abc.abstractmethod
    def materialize_piece(self, piece: "klovve.ui.Piece") -> T:
        """
        Return a :py:class:`ViewMaterialization` for a piece.

        :param piece: The piece.
        """
