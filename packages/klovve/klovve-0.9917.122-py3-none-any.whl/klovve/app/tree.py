#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import abc
import typing as t
import weakref

import klovve.ui.materialization


class ApplicationTree(abc.ABC):

    @abc.abstractmethod
    def parent_node(self, node: t.Any) -> t.Optional[t.Any]:
        pass


class MaterializationObservingApplicationTree(ApplicationTree, abc.ABC):

    @abc.abstractmethod
    def for_child(self) -> "MaterializationObservingApplicationTree":
        pass

    @abc.abstractmethod
    def visited(self, node) -> None:
        pass


class SimpleMaterializationObservingApplicationTree(MaterializationObservingApplicationTree):

    class _TreeNode:

        def __init__(self):
            self.__children = []
            self.__view = None

        @property
        def children(self) -> list["SimpleMaterializationObservingApplicationTree._TreeNode"]:
            for i, child in reversed(list(enumerate(self.__children))):  # TODO desperate
                if not child.is_alive:
                    self.__children.pop(i)
            return self.__children

        @property
        def view(self):
            return None if (self.__view is None) else self.__view()

        @property
        def is_alive(self) -> bool:
            return True if (self.__view is None) else (self.__view() is not None)

        def _set_view(self, view):
            self.__view = weakref.ref(view)

    def __init__(self, tree=None, observer_node=None):
        self.__tree = tree or SimpleMaterializationObservingApplicationTree._TreeNode()
        self.__observer_node = observer_node or self.__tree

    def for_child(self):
        new_node = SimpleMaterializationObservingApplicationTree._TreeNode()
        self.__observer_node.children.append(new_node)
        return SimpleMaterializationObservingApplicationTree(self.__tree, new_node)

    def visited(self, view):
        self.__observer_node._set_view(view)

    def parent_node(self, node):  # TODO quicker,nicer
        nodes = [(self.__tree, None)]

        while nodes:
            node_, parent_view = nodes.pop()

            if node_.view is node:
                return parent_view

            for child_node_ in node_.children:
                nodes.append((child_node_, node_.view or parent_view))
