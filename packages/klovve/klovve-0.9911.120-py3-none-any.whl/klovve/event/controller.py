#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import abc
import typing as t

import klovve.app.tree
import klovve.variable


class EventController[TNode](abc.ABC):

    @abc.abstractmethod
    def trigger_event(self, node: TNode, event) -> None:
        pass


class BaseEventController[TNode](EventController[TNode], abc.ABC):

    @abc.abstractmethod
    def parent_node(self, node: TNode) -> t.Optional[TNode]:
        pass

    def trigger_event(self, node, event):
        with klovve.variable.no_dependency_tracking():
            while node:
                node._handle_event(event)

                if event.processing_stopped:
                    break

                node = self.parent_node(node)


class ApplicationTreeBasedEventController(BaseEventController["TNode"]):

    def __init__(self, application_tree: "klovve.app.tree.ApplicationTree"):
        self.__application_tree = application_tree

    def parent_node(self, node):
        return self.__application_tree.parent_node(node)
