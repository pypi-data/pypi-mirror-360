#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
Application trees.
"""
import abc
import typing as t
import weakref


class ApplicationTree(abc.ABC):
    """
    Base class for application trees.

    An application tree allows an application node (usually views) to get its parent node (usually its parent view, or,
    for a window, the application itself).
    """

    @abc.abstractmethod
    def parent_node(self, node: t.Any) -> t.Optional[t.Any]:
        """
        The parent node of a node.

        :param node: The node.
        """


class MaterializationObservingApplicationTree(ApplicationTree, abc.ABC):
    """
    Base class for an application tree that builds up during view materialization.
    """

    @abc.abstractmethod
    def for_child(self) -> "MaterializationObservingApplicationTree":
        """
        Return a new application tree that represents a new child.
        """

    @abc.abstractmethod
    def visited(self, object_: object) -> None:
        """
        Put an object (often a view) into the root of this application tree.

        :param object_: The object to associate with this node.
        """


class _SimpleMaterializationObservingApplicationTree(MaterializationObservingApplicationTree):

    class _TreeNode:

        def __init__(self):
            self.__children = []
            self.__object_weakref = None

        @property
        def children(self) -> list["SimpleMaterializationObservingApplicationTree._TreeNode"]:
            for i, child in reversed(list(enumerate(self.__children))):  # TODO desperate
                if not child.is_alive:
                    self.__children.pop(i)
            return self.__children

        @property
        def object(self):
            return None if (self.__object_weakref is None) else self.__object_weakref()

        @object.setter
        def object(self, _):
            self.__object_weakref = weakref.ref(_)

        @property
        def is_alive(self) -> bool:
            return True if (self.__object_weakref is None) else (self.__object_weakref() is not None)

    def __init__(self, tree=None, observer_node=None):
        self.__tree = tree or SimpleMaterializationObservingApplicationTree._TreeNode()
        self.__observer_node = observer_node or self.__tree

    def for_child(self):
        new_node = SimpleMaterializationObservingApplicationTree._TreeNode()
        self.__observer_node.children.append(new_node)
        return _SimpleMaterializationObservingApplicationTree(self.__tree, new_node)

    def visited(self, object_):
        self.__observer_node.object = object_

    def parent_node(self, node):  # TODO quicker,nicer
        nodes = [(self.__tree, None)]

        while nodes:
            node_, parent_view = nodes.pop()

            if node_.object is node:
                return parent_view

            for child_node_ in node_.children:
                nodes.append((child_node_, node_.object or parent_view))


class SimpleMaterializationObservingApplicationTree(_SimpleMaterializationObservingApplicationTree):
    """
    A simple application tree that builds up during view materialization.
    """

    def __init__(self):
        super().__init__()
