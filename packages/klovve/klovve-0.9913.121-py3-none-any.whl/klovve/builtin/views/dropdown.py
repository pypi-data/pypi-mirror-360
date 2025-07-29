#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import typing as t
import klovve


class DropDown[T](klovve.ui.Piece):

    items: list[T] = klovve.ui.list_property()

    selected_item: T|None = klovve.ui.property()

    item_label_func: t.Callable[[T], str] = klovve.ui.property(initial=lambda: str)

    horizontal_layout = klovve.ui.property(initial=klovve.ui.Layout(klovve.ui.Align.CENTER))
    vertical_layout = klovve.ui.property(initial=klovve.ui.Layout(klovve.ui.Align.CENTER))
