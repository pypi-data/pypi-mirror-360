#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
See :py:class:`Entry`.
"""
import viwid.app.screen
import viwid.event
import viwid.text
from viwid.widgets.widget import Widget as _Widget


class Entry(_Widget):
    """
    A field where the user can enter and edit a single line of text.
    """

    def __init__(self, **kwargs):
        super().__init__(**{**dict(class_style_name="entry", is_focusable=True,
                                   vertical_alignment=viwid.Alignment.CENTER), **kwargs})
        self.__cursor_position = 0
        self.__offset_x = 0
        self.__rendered_text_line = ()
        self.__rendered_text_width = 0
        self.__rendered_hint_text_line = ()

    def _materialize(self):
        super()._materialize()

        self.listen_event(viwid.event.keyboard.KeyPressEvent, self.__handle_keyboard_key_pressed,
                          implements_default_behavior=True)
        self.listen_event(viwid.event.mouse.ButtonDownEvent, self.__handle_mouse_button_down,
                          implements_default_behavior=True)

    def _dematerialize(self):
        self.unlisten_event(self.__handle_keyboard_key_pressed)
        self.unlisten_event(self.__handle_mouse_button_down)

        super()._dematerialize()

    text: str
    @_Widget.Property(default=lambda: "")
    def text(self, _):
        """
        The current text. Empty string by default.

        Only set it to text that is a single line, i.e. does not contain line breaks. It would be stripped, as the user
        would be unable to deal with it anyway.
        """
        if (i := _.find("\n")) > -1:
            self.text = self.text[:i]
            return

        self.__rendered_text_line = self._text_measuring.text(_).render()
        if len(self.__rendered_text_line) > 0:
            self.__rendered_text_line = self.__rendered_text_line[0]
        self.__rendered_text_width = sum((_.width_on_screen if _ else 0) for _ in self.__rendered_text_line)
        self._cursor_position_internal = self._cursor_position_internal

        self._request_repaint()

    hint_text: str
    @_Widget.Property(default=lambda: "")
    def hint_text(self, _):
        """
        The hint text. Empty string by default.

        It is displayed (in a modest colouring) when the text entry field is empty.
        """
        if (i := _.find("\n")) > -1:
            self.hint_text = self.hint_text[:i]
            return

        self.__rendered_hint_text_line = self._text_measuring.text(_).render()
        if len(self.__rendered_hint_text_line) > 0:
            self.__rendered_hint_text_line = self.__rendered_hint_text_line[0]
        self._request_repaint()

    @property
    def cursor_index(self) -> int:
        """
        The position of the keyboard cursor inside the entered text.
        """
        return sum((len(_.as_str) if _ else 0) for _ in self.__rendered_text_line[:self._cursor_position_internal])

    @cursor_index.setter
    def cursor_index(self, _: int) -> None:
        cursor_position_internal = 0
        cursor_position_cur = 0
        for i_grapheme, grapheme in enumerate(self.__rendered_text_line):
            if grapheme is not None:
                cursor_position_cur += len(grapheme.as_str)
            cursor_position_internal += 1
            if cursor_position_cur >= _:
                break
        self._cursor_position_internal = cursor_position_internal

    @property
    def _cursor_position_internal(self) -> int:
        return self.__cursor_position

    @_cursor_position_internal.setter
    def _cursor_position_internal(self, _: int) -> None:
        if self.size.width == 0:
            return  # TODO odd

        if not (0 <= _ <= len(self.__rendered_text_line)):
            self._cursor_position_internal = min(max(0, _), len(self.__rendered_text_line))
            return

        while _ < len(self.__rendered_text_line) and self.__rendered_text_line[_] is None:
            _ -= 1

        self.__cursor_position = min(max(0, _ or 0), self.__rendered_text_width)

        if self.__cursor_position < self.__offset_x:
            self.__offset_x = self._cursor_position_internal
        elif self.__cursor_position >= self.__offset_x + self.size.width:
            offset_x = max(0, self.__cursor_position-self.size.width+1)
            while offset_x < len(self.__rendered_text_line) and self.__rendered_text_line[offset_x] is None:
                offset_x += 1
            self.__offset_x = offset_x

        self._request_repaint()

    def _compute_width(self, minimal) -> int:
        return 1 if minimal else 10

    def _compute_height(self, width: int, minimal) -> int:
        return 1

    def _paint(self, canvas):
        if len(self.__rendered_text_line) > 0:
            canvas.draw_text((self.__rendered_text_line[self.__offset_x:],),
                             color=self._style(self.layer_style.entry).foreground)
        else:
            canvas.draw_text((self.__rendered_hint_text_line,),
                             color=self._style(self.layer_style.entry_hint).foreground)
        self._set_cursor_position(viwid.Point(self._cursor_position_internal-self.__offset_x, 0))

    def __handle_keyboard_key_pressed(self, event: viwid.event.keyboard.KeyPressEvent):
        if event.with_alt or event.with_ctrl:
            return

        if event.code == viwid.event.keyboard.KeyCodes.ARROW_LEFT:
            cursor_index = max(0, self._cursor_position_internal - 1)
            while cursor_index < len(self.__rendered_text_line) and self.__rendered_text_line[cursor_index] is None:
                cursor_index -= 1
            self._cursor_position_internal = cursor_index
        elif event.code == viwid.event.keyboard.KeyCodes.ARROW_RIGHT:
            cursor_index = self._cursor_position_internal + 1
            while cursor_index < len(self.__rendered_text_line) and self.__rendered_text_line[cursor_index] is None:
                cursor_index += 1
            self._cursor_position_internal = cursor_index
        elif event.code == viwid.event.keyboard.KeyCodes.BACKSPACE:
            if self._cursor_position_internal > 0:
                old_cursor_position = self._cursor_position_internal
                cursor_index = old_cursor_position - 1
                while self.__rendered_text_line[cursor_index] is None:
                    cursor_index -= 1
                self._cursor_position_internal = cursor_index
                self.text = "".join(
                    (_.as_str if _ else "") for _ in self.__rendered_text_line[:cursor_index]) + "".join(
                    (_.as_str if _ else "") for _ in self.__rendered_text_line[old_cursor_position:])
        elif event.code == viwid.event.keyboard.KeyCodes.HOME:
            self._cursor_position_internal = 0
        elif event.code == viwid.event.keyboard.KeyCodes.END:
            self._cursor_position_internal = self.__rendered_text_width
        elif event.code == viwid.event.keyboard.KeyCodes.DEL:
            if self._cursor_position_internal < self.__rendered_text_width:
                remove_until_cursor_position = self._cursor_position_internal + 1
                while (remove_until_cursor_position < len(self.__rendered_text_line)
                       and self.__rendered_text_line[remove_until_cursor_position] is None):
                    remove_until_cursor_position += 1
                self.text = "".join(
                    (_.as_str if _ else "") for _ in self.__rendered_text_line[:self._cursor_position_internal]
                ) + "".join(
                    (_.as_str if _ else "") for _ in self.__rendered_text_line[remove_until_cursor_position:])
        elif event.char is not None:
            self.text = "".join(
                (_.as_str if _ else "") for _ in self.__rendered_text_line[:self._cursor_position_internal]
            ) + event.char + "".join(
                (_.as_str if _ else "") for _ in self.__rendered_text_line[self._cursor_position_internal:])
            self._cursor_position_internal += self._text_measuring.grapheme(event.char).width_on_screen
        else:
            return
        event.stop_handling()

    def __handle_mouse_button_down(self, event: viwid.event.mouse.ButtonDownEvent):
        point = viwid.app.screen.translate_coordinates_from_root(event.screen_position, new_origin=self)
        self._cursor_position_internal = self.__offset_x + point.x
