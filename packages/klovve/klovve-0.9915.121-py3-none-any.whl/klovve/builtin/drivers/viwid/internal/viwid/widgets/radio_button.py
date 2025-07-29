#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
See :py:class:`RadioButton`.
"""
import typing as t

from viwid.widgets.check_button import CheckButton as _CheckButton


class RadioButton(_CheckButton):
    """
    A 'radio-checkable' button with a text label. It usually belongs to a group of radio buttons where only one can be
    selected/checked.
    """

    def __init__(self, **kwargs):
        super().__init__(**{**dict(_is_uncheckable_by_user=False), **kwargs})
        self.__group = None

    def _materialize(self):
        super()._materialize()

        self.listen_property("is_checked", self.__handle_checked_changed)

    def _dematerialize(self):
        self.unlisten_property("is_checked", self.__handle_checked_changed)

        super()._dematerialize()

    group: "Group"
    @_CheckButton.Property(default=lambda: None)
    def group(self, _):
        """
        The group this radio button belongs to. `None` by default.
        """
        if not _:
            self.group = RadioButton.Group()
            return

        if _ != self.__group:
            if self.__group:
                self.__group._unjoin_button(self)
            self.__group = _
            if _:
                _._join_button(self)

    def __handle_checked_changed(self):
        self.__group.select_button(self)

    class Group:
        """
        A group of radio buttons.

        In each group, there can be only one radio button selected.
        """

        def __init__(self):
            self.__buttons = []
            self.__selected_button = None

        def _join_button(self, button: "RadioButton") -> None:
            button.is_checked = False
            self.__buttons.append(button)

        def _unjoin_button(self, button: "RadioButton") -> None:
            self.__buttons.remove(button)

        def select_button(self, button: "RadioButton") -> None:
            if button == self.__selected_button:
                return

            if self.__selected_button:
                self.__selected_button.is_checked = False

            self.__selected_button = button
            if self.__selected_button:
                self.__selected_button.is_checked = True

        @property
        def buttons(self) -> t.Sequence["RadioButton"]:
            return tuple(self.__buttons)

        @property
        def selected_button(self) -> "RadioButton|None":
            return self.__selected_button
