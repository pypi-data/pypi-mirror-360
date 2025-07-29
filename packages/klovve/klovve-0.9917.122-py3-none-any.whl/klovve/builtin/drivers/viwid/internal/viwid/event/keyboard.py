#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
Events related to keyboard input.
"""
from viwid.event import Event as _BaseEvent


class KeyCombination:
    """
    A combination of keys.
    """

    TCode = tuple[int, ...]
    TCodeInput = TCode | int | bytes | str

    def __init__(self, code: TCode, char: str | None, with_shift: bool, with_alt: bool, with_ctrl: bool):
        """
        Usually you do not create instances directly. See :py:meth:`by_code`.
        """
        self.__code = code
        self.__char = char
        self.__with_shift = with_shift
        self.__with_alt = with_alt
        self.__with_ctrl = with_ctrl

    @property
    def code(self) -> TCode:
        return self.__code

    @property
    def char(self) -> str | None:
        return self.__char

    @property
    def with_shift(self) -> bool:
        return self.__with_shift

    @property
    def with_alt(self) -> bool:
        return self.__with_alt

    @property
    def with_ctrl(self) -> bool:
        return self.__with_ctrl

    @staticmethod
    def by_code(code: TCodeInput, *, with_shift: bool, with_alt: bool, with_ctrl: bool) -> "KeyCombination":
        """
        Return a key combination representation for a given key combination.

        :param code: The primary key's code.
        :param with_shift: Whether 'shift' was pressed as well.
        :param with_alt: Whether 'alt' was pressed as well.
        :param with_ctrl: Whether 'ctrl' was pressed as well.
        """
        if isinstance(code, bytes):
            code = code.decode("utf-32")
        if isinstance(code, str):
            code = (ord(code),)
        if isinstance(code, int):
            code = (code,)

        if len(code) > 0 and code[0] >= 0:
            char = "".join(chr(_) for _ in code)
            if with_shift:
                char = char.upper()
        else:
            char = None

        return KeyCombination(code, char, with_shift, with_alt, with_ctrl)


class KeyCodes:
    """
    Internal character codes for some keys. See :py:attr:`KeyPressEvent.code`.
    """
    # for a printable character, the code is the Unicode codepoints of the character without modifier keys
    # (i.e. lowercase). Most of them are not listed here.

    ARROW_UP = (-1, 0)
    ARROW_RIGHT = (-1, 1)
    ARROW_DOWN = (-1, 2)
    ARROW_LEFT = (-1, 3)
    BACKSPACE = (-1, 4)
    HOME = (-1, 5)
    END = (-1, 6)
    DEL = (-1, 7)
    INS = (-1, 8)
    F1 = (-1, 10)
    F2 = (-1, 11)
    F3 = (-1, 12)
    F4 = (-1, 13)
    F5 = (-1, 14)
    F6 = (-1, 15)
    F7 = (-1, 16)
    F8 = (-1, 17)
    F9 = (-1, 18)
    F10 = (-1, 19)
    F11 = (-1, 20)
    F12 = (-1, 21)
    PRINT = (-1, 22)
    PAGE_UP = (-1, 23)
    PAGE_DOWN = (-1, 24)
    TAB = (9,)
    ENTER = (10,)
    SPACE = (32,)
    ESC = (27,)


class _Event(_BaseEvent):
    pass


class KeyPressEvent(_Event):
    """
    Event that occurs when the user presses a key (or a combination of keys).

    The flags for the modifier keys :py:attr:`with_shift`, :py:attr:`with_alt` and :py:attr:`with_ctrl` only work in
    some combinations. That needs to be tested. Some combinations might work in some terminal implementations but not
    in others.
    """

    def __init__(self, key_combination: KeyCombination):
        super().__init__()
        self.__key_combination = key_combination

    @property
    def _key_combination(self) -> KeyCombination:
        return self.__key_combination

    @property
    def code(self) -> KeyCombination.TCode:
        """
        The code of the primary pressed key (i.e. without modifier keys).

        For printable characters, when combined with 'shift', this will be the code for the modified character (e.g.
        the uppercase variant).

        It is recommended to check :py:attr:`char` first and only fall back to the code if it is `None`. See
        :py:class:`KeyCodes`.
        """
        return self.__key_combination.code

    @property
    def char(self) -> str|None:
        """
        The string representation of the primary pressed key (i.e. without modifier keys) or `None` if there is no
        printable character associated to it. For that case, see :py:attr:`code`.

        When combined with 'shift', this will be the modified character (e.g. the uppercase variant).
        """
        return self.__key_combination.char

    @property
    def with_shift(self) -> bool:
        """
        Whether 'shift' was pressed as well.
        """
        return self.__key_combination.with_shift

    @property
    def with_alt(self) -> bool:
        """
        Whether 'alt' was pressed as well.
        """
        return self.__key_combination.with_alt

    @property
    def with_ctrl(self) -> bool:
        """
        Whether 'ctrl' was pressed as well.
        """
        return self.__key_combination.with_ctrl
