#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
See :py:class:`DropDown`.
"""
import typing as t
import klovve


class DropDown[T](klovve.ui.Piece):
    """
    A drop-down field.
    """

    #: The items to provide to the user.
    items: list[T] = klovve.ui.list_property()

    #: The currently selected item.
    selected_item: T|None = klovve.ui.property()

    #: The function that translates items to their textual representation.
    item_label_func: t.Callable[[T], str] = klovve.ui.property(initial=lambda: str)

    horizontal_layout = klovve.ui.property(initial=klovve.ui.Layout(klovve.ui.Align.CENTER))
    vertical_layout = klovve.ui.property(initial=klovve.ui.Layout(klovve.ui.Align.CENTER))
