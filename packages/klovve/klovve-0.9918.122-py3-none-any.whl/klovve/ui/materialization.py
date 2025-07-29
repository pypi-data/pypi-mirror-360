#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import abc
import typing as t

import klovve.app.tree
import klovve.debug
import klovve.event.controller
import klovve.object
import klovve.ui


class ViewMaterialization[TView: "klovve.ui.View", TNative](klovve.object.Object, abc.ABC):

    def __init__(self, view: TView, event_controller: "klovve.event.controller.EventController[klovve.ui.View]",
                 application_tree: "klovve.app.tree.MaterializationObservingApplicationTree"):
        self.__view = view
        super().__init__()
        klovve.debug.memory.new_object_created(ViewMaterialization, self)
        self.__event_controller = event_controller
        self.__application_tree = application_tree
        self.__native = None

    @property
    def piece(self) -> TView:
        return self.__view

    @property
    def event_controller(self) -> "klovve.event.controller.EventController[klovve.ui.View]":
        return self.__event_controller

    @property
    def application_tree(self) -> "klovve.app.tree.MaterializationObservingApplicationTree":
        return self.__application_tree

    @abc.abstractmethod
    def create_native(self) -> TNative:
        pass

    @property
    def native(self) -> TNative:
        if self.__native is None:
            self.__native = self.create_native()
        return self.__native


class PieceMaterializer[T](abc.ABC):

    @abc.abstractmethod
    def materialize_piece(self, piece) -> T:
        pass
