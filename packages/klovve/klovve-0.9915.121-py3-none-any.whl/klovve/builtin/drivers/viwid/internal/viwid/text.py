#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
Text measuring and rendering, and similar things that are needed for printing text to the screen with its specified
geometry.
"""
import abc
import unicodedata
import typing as t
import weakref


class Grapheme:
    """
    Representation for a piece of text that gets rendered together in one screen block. This is usually a single
    character, but may also include 'combining characters'.

    Although rendered in a single block, this block does not always have a width of 1 on the screen!
    """

    #: The grapheme as string.
    as_str: str

    #: The width of this grapheme in screen blocks.
    width_on_screen: int

    #: The 'space' grapheme (ascii 32).
    SPACE: t.ClassVar["Grapheme"]

    def __init__(self, as_str: str, width_on_screen: int):
        """
        Usually you do not create instances directly. See :py:meth:`TextMeasuring.grapheme`.

        :param as_str: The grapheme as string.
        :param width_on_screen: The width of this grapheme in screen blocks.
        """
        self.as_str = as_str
        self.width_on_screen = width_on_screen


Grapheme.SPACE = Grapheme(" ", 1)

TRenderedText = t.Sequence[t.Sequence[Grapheme | None]]


class Text(abc.ABC):
    """
    A piece of text that can be measured and rendered.

    This is not much more than the text's string representation, but is used for internal caching purposes. You should
    reuse your instances as good as possible.

    Get instances from :py:meth:`TextMeasuring.text`.
    """

    ELLIPSIS: str = "..."

    @property
    @abc.abstractmethod
    def as_str(self) -> str:
        """
        The text as string.
        """

    @abc.abstractmethod
    def render(self, *, width: int|None = None, height: int|None = None) -> TRenderedText:
        """
        Render this text to a 2D grapheme representation (of exactly the given size) used for measurements and painting.

        This returns the same result as :py:meth:`TextMeasuring.render_text`.

        :param width: The width (default: on demand).
        :param height: The height (default: on demand).
        """

    @abc.abstractmethod
    def render_trimmed_to_width(self, max_width: int, *, ellipsis: str = ELLIPSIS) -> TRenderedText:
        """
        Render this text in a trimmed way, starting with :py:meth:`render` with no size arguments, but then trim it
        down to a given maximum width.

        This returns the same result as :py:meth:`TextMeasuring.rendered_text_trimmed_to_width`.

        :param max_width: The maximum width to trim the rendered lines down to.
        :param ellipsis: The ellipsis string to put at the end of trimmed lines.
        """

    @abc.abstractmethod
    def width(self) -> int:
        """
        Return the native width of this text, i.e. the width that the rendered text would get without any size
        parameters.

        This returns the same result as :py:meth:`TextMeasuring.text_width`.
        """

    @abc.abstractmethod
    def height(self, *, for_width: int|None = None) -> int:
        """
        Return the native height of this text, i.e. the height that the rendered text would get, either without any size
        parameters or for a given width.

        This returns the same result as :py:meth:`TextMeasuring.text_height`.

        :param for_width: The maximal available width (default: on demand).
        """


class TextMeasuring:
    """
    Does text measuring and rendering.
    """

    def __init__(self, measure_character_width_func: t.Callable[[str], int]):
        """
        Usually you do not create instances directly. See e.g.
        :py:meth:`viwid.app.manager.ApplicationManager.text_measuring`.

        :param measure_character_width_func: The function to measure the screen width for a string (representing a
                                             single grapheme).
        """
        self.__measure_character_width_func = measure_character_width_func
        self.__character_box_cache = weakref.WeakKeyDictionary()
        self.__grapheme_cache = {}

    def grapheme(self, char: str) -> Grapheme:
        """
        Return a grapheme for its string representation.

        :param char: The grapheme as string.
        """
        if not (result := self.__grapheme_cache.get(char)):
            result = self.__grapheme_cache[char] = Grapheme(char, self.__measure_character_width_func(char))
        return result

    def text(self, s: str) -> Text:
        """
        Return a text object for a string, for later measuring and rendering.

        Internally, for each existing Text instance, a lot of internal data gets cached. Try to re-use your instances.

        :param s: The text as string.
        """
        return TextMeasuring._Text(s, self)

    def text_width(self, text: Text) -> int:
        """
        Return the native width of a given text.

        This returns the same result as :py:meth:`Text.width`.

        :param text: The text to measure.
        """
        if len(text.as_str) == 0:
            return 0
        return self.__render(text, width=None, height=None)[0]

    def text_height(self, text: Text, *, for_width: int|None = None) -> int:
        """
        Return the native height of a given text, either with or without any width restrictions.

        This returns the same result as :py:meth:`Text.height`.

        :param text: The text to measure.
        :param for_width: The maximal width available.
        """
        if (len(text.as_str) == 0) or (for_width == 0):
            return 0
        return self.__render(text, width=for_width, height=None)[1]

    def render_text(self, text: Text, *, width: int|None = None, height: int|None = None) -> TRenderedText:
        """
        Render a given text to a 2D grapheme representation (of exactly the given size) used for measurements and
        painting.

        This returns the same result as :py:meth:`Text.render`.

        :param text: The text to render.
        :param width: The width (default: on demand).
        :param height: The height (default: on demand).
        """
        if (len(text.as_str) == 0) or (width == 0):
            return ()
        return self.__render(text, width=width, height=height)[2]

    def rendered_text_trimmed_to_width(self, text: TRenderedText, *, max_width: int, ellipsis: str) -> TRenderedText:
        """
        Render a given text in a trimmed way, starting with :py:meth:`render` with no size arguments, but then trim it
        down to a given maximum width.

        This returns the same result as :py:meth:`Text.render_trimmed_to_width`.

        :param text: The text to render.
        :param max_width: The maximum width to trim the rendered lines down to.
        :param ellipsis: The ellipsis string to put at the end of trimmed lines.
        """
        if max_width <= 0:
            return [[] for _ in text]
        rendered_ellipsis_line = self.render_text(self.text(ellipsis))[0]
        ellipsis_width = sum((_.width_on_screen if _ else 0) for _ in rendered_ellipsis_line)
        if max_width <= ellipsis_width:
            ellipsis_short = []
            i = 0
            remaining_width = max_width
            while True:
                grapheme = rendered_ellipsis_line[i]
                if grapheme and grapheme.width_on_screen >= remaining_width:
                    break
                ellipsis_short.append(grapheme)
                i += 1
                if grapheme:
                    remaining_width -= grapheme.width_on_screen
            while sum((_.width_on_screen if _ else 0) for _ in ellipsis_short) < max_width:
                ellipsis_short.insert(0, Grapheme.SPACE)
            return [ellipsis_short for _ in text]

        result = []
        for line in text:
            line = list(line)
            line_width = sum((_.width_on_screen if _ else 0) for _ in line)
            if line_width > max_width:
                while line_width > max_width - ellipsis_width:
                    for i_grapheme, grapheme in reversed(tuple(enumerate(line))):
                        if grapheme:
                            line_width -= grapheme.width_on_screen
                            line = line[:i_grapheme]
                            break
                while line_width < max_width - ellipsis_width:
                    line.append(Grapheme.SPACE)
                    line_width += 1
                line += rendered_ellipsis_line
            result.append(line)
        return result

    def __render(self, text: Text, *, width: int|None, height: int|None) -> tuple[int, int, TRenderedText]:
        if (cache_entry := self.__character_box_cache.get(text)) is None:
            cache_entry = self.__character_box_cache[text] = TextMeasuring._RenderCacheEntry()

        if (width is None) and (height is None) and (cache_entry.width is not None):
            return cache_entry.width, len(cache_entry.unbounded_character_box), cache_entry.unbounded_character_box

        if (cache_entry.character_box is not None) and (width == cache_entry.character_box_for_width):
            character_box = cache_entry.character_box
            height = len(character_box) if (height is None) else height
            return cache_entry.character_box_for_width, height, TextMeasuring.box_with_height(cache_entry.character_box,
                                                                                              height)

        character_box, box_width = self.__render__raw(text, width)

        if (width is None) and (height is None):
            cache_entry.width = box_width
            cache_entry.unbounded_character_box = character_box

        elif width is not None:
            cache_entry.character_box_for_width = width
            cache_entry.character_box = character_box

        if (height is not None) and (height != len(character_box)):
            character_box = TextMeasuring.box_with_height(character_box, height)

        return box_width, len(character_box), character_box

    def __render__raw(self, text: Text, width: int) -> tuple[TRenderedText, int]:
        character_box = []
        current_box_line = None
        box_width = 0
        i_text = 0
        text_str = text.as_str
        text_len = len(text_str)
        line_wrapping = False

        while i_text < text_len:
            if (next_whitespace_character := self.__render__next_whitespace_character(text_str, i_text)) is not None:
                if line_wrapping:
                    i_text += len(next_whitespace_character.as_str)
                    continue

            line_wrapping = False

            if current_box_line is None:
                character_box.append(current_box_line := [])

            if next_whitespace_character is not None:
                if next_whitespace_character.as_str == "\n":
                    box_width = max(box_width, len(current_box_line))
                    current_box_line = None
                    i_text += 1
                    continue

                if (width is None) or (len(current_box_line) + next_whitespace_character.width_on_screen <= width):
                    current_box_line.append(next_whitespace_character)
                    for _ in range(next_whitespace_character.width_on_screen - 1):
                        current_box_line.append(None)
                else:
                    box_width = max(box_width, len(current_box_line))
                    current_box_line = None
                    line_wrapping = True
                i_text += len(next_whitespace_character.as_str)
                continue

            next_non_whitespace_characters = self.__render__next_non_whitespace_characters(text_str, i_text)

            if (width is None) or (len(current_box_line)
                                   + sum(_.width_on_screen for _ in next_non_whitespace_characters) <= width):
                for character in next_non_whitespace_characters:
                    current_box_line.append(character)
                    for _ in range(character.width_on_screen-1):
                        current_box_line.append(None)
                    i_text += len(character.as_str)

            elif len(current_box_line) > 0:
                box_width = max(box_width, len(current_box_line))
                current_box_line = None
                line_wrapping = True

            else:
                if any(next_non_whitespace_characters) and next_non_whitespace_characters[0].width_on_screen > width:
                    i_text += len(next_non_whitespace_characters[0].as_str)
                    continue
                for next_non_whitespace_character in next_non_whitespace_characters:
                    if len(current_box_line) + next_non_whitespace_character.width_on_screen > width:
                        break
                    current_box_line.append(next_non_whitespace_character)
                    for _ in range(next_non_whitespace_character.width_on_screen-1):
                        current_box_line.append(None)
                    i_text += len(next_non_whitespace_character.as_str)

        if width is not None:
            box_width = width
        elif current_box_line is not None:
            box_width = max(box_width, len(current_box_line))

        return TextMeasuring.box_with_width(character_box, box_width), box_width

    @staticmethod
    def box_with_height(box: TRenderedText, height: int) -> TRenderedText:
        """
        For a given rendered text, return a rendered text that has a given height.

        This trims overflowing content and replaces missing content with empty space.

        :param box: The rendered box.
        :param height: The target height.
        """
        height = max(0, height)

        if height != len(box):
            box = list(box)
            while len(box) > height:
                box.pop()
            if len(box) < height:
                empty_line = (len(box[0]) if any(box) else 0) * (Grapheme.SPACE,)
                for _ in range(height - len(box)):
                    box.append(empty_line)
        return box

    @staticmethod
    def box_with_width(box: TRenderedText, width: int) -> TRenderedText:
        """
        For a given rendered text, return a rendered text that has a given width.

        This trims overflowing content and replaces missing content with empty space.

        :param box: The rendered box.
        :param width: The target width.
        """
        width = max(width, 0)

        box = [list(line) for line in box]
        for line in box:
            while len(line) > width:
                line.pop()
            while len(line) < width:
                line.append(Grapheme.SPACE)
        return box

    def __render__next_whitespace_character(self, text: str, index: int) -> Grapheme|None:
        codepoint = text[index]
        if unicodedata.category(codepoint) == "Zs" or codepoint == "\n":
            return self.grapheme(codepoint)

    def __render__next_non_whitespace_characters(self, text: str, index: int) -> t.Sequence[Grapheme]:
        result = []

        for codepoint in text[index:]:
            codepoint_category = unicodedata.category(codepoint)
            if codepoint_category == "Zs" or codepoint == "\n":
                break
            elif any(result) and codepoint_category.startswith("M"):
                result[-1].append(codepoint)
            else:
                result.append([codepoint])

        return [self.grapheme("".join(_)) for _ in result]

    class _Text(Text):

        def __init__(self, as_str: str, text_measuring: "TextMeasuring"):
            self.__as_str = as_str
            self.__text_measuring = text_measuring

        @property
        def as_str(self):
            return self.__as_str

        def render(self, *, width=None, height=None):
            return self.__text_measuring.render_text(self, width=width, height=height)

        def width(self):
            return self.__text_measuring.text_width(self)

        def height(self, *, for_width=None):
            return self.__text_measuring.text_height(self, for_width=for_width)

        def render_trimmed_to_width(self, max_width, *, ellipsis=Text.ELLIPSIS):
            return self.__text_measuring.rendered_text_trimmed_to_width(self.render(),
                                                                        max_width=max_width, ellipsis=ellipsis)

    class _RenderCacheEntry:

        def __init__(self):
            self.width: int | None = None
            self.unbounded_character_box: "TRenderedText|None" = None
            self.character_box: "TRenderedText|None" = None
            self.character_box_for_width: int | None = None
