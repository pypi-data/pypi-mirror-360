#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
Canvases are the drawing area where visual elements paint their visual representations. See also :py:class:`Canvas`.
They can be modifiable (see :py:class:`ModifiableCanvas`), but some canvases are computed and read-only.

Canvases are the API for widgets to paint their visual representation, but they are also heavily used internally. The
content painted to the screen is internally represented by a canvas that is a composition of the current application's
screen layer canvases, which in turn are compositions of their child widgets' canvases. Even for each widget, there
is one modifiable canvas for its painting, and an outer canvas that composes it with its child widgets. Note that this
applies recursively, so a lot of canvas computation is constantly going on in the background.
"""
import abc
import functools
import typing as t

import viwid.data.color
import viwid.styling
import viwid.text


class BlockAttributes:
    """
    Styling attributes for a block, i.e. a cell on the terminal screen. This is somewhat similar to
    :py:class:`viwid.styling.Theme.Layer.Class.Style`, but already boiled down in some regards for performance reasons
    (e.g. it uses :py:class:`viwid.PlainColor` for colors).
    """

    #: The foreground color. Text will be printed in this color.
    foreground_color: viwid.PlainColor

    #: The background color.
    background_color: viwid.PlainColor

    def __init__(self, foreground_color: viwid.PlainColor, background_color: viwid.PlainColor):
        """
        Usually you do not create instances directly. See :py:meth:`BlockAttributes.get`.
        """
        self.foreground_color = foreground_color
        self.background_color = background_color

    @staticmethod
    def get(*, foreground_color: viwid.data.color.TPlainColorInput,
            background_color: viwid.data.color.TPlainColorInput) -> "BlockAttributes":
        """
        Return a :py:class:`BlockAttributes` with the given data.

        :param foreground_color: The foreground color. Text will be printed in this color.
        :param background_color: The background color.
        """
        return BlockAttributes(foreground_color=viwid.PlainColor.get(foreground_color),
                               background_color=viwid.PlainColor.get(background_color))


class Canvas(abc.ABC):
    """
    Base class for canvases that are at least readable.

    For modifiable canvases, see :py:class:`ModifiableCanvas`.
    """

    _DEFAULT_BLOCK_ATTRIBUTES = BlockAttributes.get(foreground_color=viwid.PlainColor.TRANSPARENT,
                                                    background_color=viwid.PlainColor.TRANSPARENT)
    _DEFAULT_GRAPHEME = viwid.text.Grapheme.SPACE

    def __init__(self):
        super().__init__()
        self.__repainted_handlers = []
        self.__resized_handlers = []

    @property
    @abc.abstractmethod
    def size(self) -> viwid.Size:
        """
        The canvas size.
        """

    @abc.abstractmethod
    def line(self, y: int) -> tuple[t.Sequence[BlockAttributes], t.Sequence[viwid.text.Grapheme|None]]:
        """
        Return the content and styling information for one horizontal line of this canvas.

        :param y: The y-coordinate. It must fulfill `0 <= y < size.height`, otherwise it might fail in arbitrary ways.
        """

    def add_repainted_handler(self, repainted_handler: t.Callable[[int, int], None]) -> None:
        """
        Add a function that gets called whenever a part of this canvas got repainted.

        Its arguments are the start line index and the stop line index. All lines in this range were potentially
        repainted (with the stop line index being exclusive, like in Python ranges).

        See also :py:meth:`remove_repainted_handler`.

        :param repainted_handler: The function to add.
        """
        self.__repainted_handlers.append(repainted_handler)

    def remove_repainted_handler(self, repainted_handler: t.Callable[[int, int], None]) -> None:
        """
        Remove a function added by :py:meth:`add_repainted_handler`.

        If the function was added more than once, it gets removed once. If it was not added, ValueError gets raised.

        :param repainted_handler: The function to remove.
        """
        self.__repainted_handlers.remove(repainted_handler)

    def add_resized_handler(self, resized_handler: t.Callable[[], None]) -> None:
        """
        Add a function that gets called whenever the canvas got resized.

        That function does not get any arguments.

        When a canvas got larger in at least one dimension, this usually also implies the demand to react similar to
        some or all lines being repainted (after all, there is now new content in that new space that you have not
        seen yet).

        See also :py:meth:`remove_resized_handler`.

        :param resized_handler: The function to add.
        """
        self.__resized_handlers.append(resized_handler)

    def remove_resized_handler(self, resized_handler: t.Callable[[], None]) -> None:
        """
        Remove a function added by :py:meth:`add_resized_handler`.

        If the function was added more than once, it gets removed once. If it was not added, ValueError gets raised.

        :param resized_handler: The function to remove.
        """
        self.__resized_handlers.remove(resized_handler)

    def _call_repainted_handlers(self, from_line: int, to_line: int) -> None:
        """
        Call all repainted handlers.

        :param from_line: The start line index.
        :param to_line: The stop line index (exclusive, as in Python ranges).
        """
        from_line = min(max(0, from_line), self.size.height)
        to_line = min(max(from_line, to_line), self.size.height)

        for repainted_handler in self.__repainted_handlers:
            repainted_handler(from_line, to_line)

    def _call_resized_handlers(self) -> None:
        """
        Call all resize handlers.
        """
        for resized_handler in self.__resized_handlers:
            resized_handler()


class ModifiableCanvas(Canvas, abc.ABC):
    """
    Base class for canvases that actually can be painted on.

    See also :py:class:`OffScreenCanvas`.
    """

    @abc.abstractmethod
    def fill(self,
             attributes: "BlockAttributes|viwid.data.color.TPlainColorInput|viwid.styling.Theme.Layer.Class.Style", *,
             rectangle: viwid.Rectangle|None = None) -> None:
        """
        Fill the given rectangle with the given styling attributes.

        This affects setting the foreground as well as the background color, but it does not actually print any text
        contents. Instead, it removes all text contents in this rectangle (technically, it will fill it with space
        characters).

        :param attributes: The styling attributes to fill the given rectangle with.
        :param rectangle: The rectangle to fill. It may exceed the canvas area in any direction, but will have no effect
                          there. If unspecified, the entire canvas gets filled.
        """

    @abc.abstractmethod
    def draw_text(self, text: viwid.text.TRenderedText|viwid.text.Text, *,
                  color: viwid.data.color.TPlainColorInput|None = None, rectangle: viwid.Rectangle|None = None) -> None:
        """
        Draw text into a given rectangle.

        All former text content in this rectangle gets replaced, either by the new text or empty space.

        :param text: The text to draw. Can either be a `Text` or an already rendered text. In the latter case,
                     overflowing parts will just get trimmed; there will be no reflow computation.
        :param color: The new foreground color to apply to the given rectangle. If unspecified, use the color that is
                      already specified for that block (e.g. by a former :py:meth:`fill` call).
        :param rectangle: The rectangle to draw the text into. It may exceed the canvas area in any direction, but will
                          have no effect there. If unspecified, the entire canvas gets drawn to.
        """


class OffScreenCanvas(ModifiableCanvas):
    """
    Typical implementation of a modifiable canvas.
    """

    def __init__(self, size: viwid.Size = viwid.Size.NULL):
        """
        :param size: The initial size.
        """
        super().__init__()
        self.__size = size
        self.__attributes = size.area * OffScreenCanvas._DEFAULT_BLOCK_ATTRIBUTES_BYTES
        self.__graphemes = size.area * OffScreenCanvas._DEFAULT_GRAPHEME_BYTES
        self.__driver = None

    def resize(self, size: viwid.Size) -> None:
        """
        Resize the canvas.

        :param size: The new size.
        """
        width, height = size.width, size.height
        plus_width, common_width = max(0, width - self.__size.width), min(width, self.__size.width)
        plus_height = max(0, height - self.__size.height)
        new_graphemes = bytearray()
        new_attributes = bytearray()

        plus_height_default_attributes = (plus_height * width) * OffScreenCanvas._DEFAULT_BLOCK_ATTRIBUTES_BYTES
        plus_height_default_graphemes = (plus_height * width) * OffScreenCanvas._DEFAULT_GRAPHEME_BYTES
        plus_width_default_attributes = plus_width * OffScreenCanvas._DEFAULT_BLOCK_ATTRIBUTES_BYTES
        plus_width_default_graphemes = plus_width * OffScreenCanvas._DEFAULT_GRAPHEME_BYTES
        i = 0
        for i_row in range(height):
            if i_row >= self.__size.height:
                new_attributes += plus_height_default_attributes
                new_graphemes += plus_height_default_graphemes
                break

            new_attributes += self.__attributes[self.__attributes_index(i):self.__attributes_index(i + common_width)]
            new_attributes += plus_width_default_attributes
            new_graphemes += self.__graphemes[self.__grapheme_index(i):self.__grapheme_index(i + common_width)]
            new_graphemes += plus_width_default_graphemes
            i += self.__size.width

        self.__attributes, self.__graphemes = bytes(new_attributes), bytes(new_graphemes)
        self.__size = viwid.Size(width, height)

        self._call_resized_handlers()

    def line(self, y):
        width = self.__size.width
        attributes, graphemes = width * [None], width * [None]

        i_attributes = self.__attributes_index(y * width)
        i_grapheme = self.__grapheme_index(y * width)
        for x in range(width):
            attributes[x] = OffScreenCanvas._block_attributes_from_bytes(self.__attributes, i_attributes)
            graphemes[x] = OffScreenCanvas._grapheme_from_bytes(self.__graphemes, i_grapheme)
            i_attributes += OffScreenCanvas._BLOCK_ATTRIBUTES_BYTES_LEN
            i_grapheme += OffScreenCanvas._GRAPHEME_BYTES_LEN

        return attributes, graphemes

    @property
    def size(self):
        return self.__size

    def set_line(self, y: int, attributes: t.Sequence[BlockAttributes],
                 graphemes: t.Sequence[viwid.text.Grapheme]) -> None:
        """
        Set the styling attributes and text content for one horizontal line of this canvas.

        The provided lists must be at least as long as the width of this canvas.

        :param y: The y-coordinate of the line to set.
        :param attributes: The list of styling attributes.
        :param graphemes: The list of text graphemes.
        """
        width = self.__size.width
        attributes_bytes = self.__attributes[:self.__attributes_index(y * width)]
        graphemes_bytes = self.__graphemes[:self.__grapheme_index(y * width)]

        for x in range(width):
            attributes_bytes += OffScreenCanvas._block_attributes_to_bytes(attributes[x])
            graphemes_bytes += OffScreenCanvas._grapheme_to_bytes(graphemes[x])

        attributes_bytes += self.__attributes[self.__attributes_index((y+1) * width):]
        graphemes_bytes += self.__graphemes[self.__grapheme_index((y + 1) * width):]

        self.__attributes, self.__graphemes = attributes_bytes, graphemes_bytes
        self._call_repainted_handlers(y, y+1)

    def fill(self, attributes, *, rectangle=None):
        if not self.__driver:
            self.__driver = viwid.drivers.current()

        full_rectangle = viwid.Rectangle(viwid.Point.ORIGIN, self.__size)
        rectangle = full_rectangle if rectangle is None else rectangle.clipped_by(full_rectangle)
        if rectangle.width == 0 or rectangle.height == 0:
            return
        if isinstance(attributes, viwid.styling.Theme.Layer.Class.Style):
            attributes = BlockAttributes(foreground_color=self.__driver.plain_color(attributes.foreground),
                                         background_color=self.__driver.plain_color(attributes.background))
        elif not isinstance(attributes, BlockAttributes):
            color = viwid.PlainColor.get(attributes)
            attributes = BlockAttributes(foreground_color=color, background_color=color)

        attributes_line_bytes = rectangle.width * OffScreenCanvas._block_attributes_to_bytes(attributes)
        graphemes_line_bytes = rectangle.width * OffScreenCanvas._DEFAULT_GRAPHEME_BYTES
        for y in range(rectangle.height):
            index = (rectangle.top_y + y) * self.__size.width + rectangle.left_x
            self.__overwrite_attributes(index, attributes_line_bytes)
            self.__overwrite_graphemes(index, graphemes_line_bytes)

        self._call_repainted_handlers(rectangle.top_y, rectangle.bottom_y)

    def draw_text(self, text, color=None, rectangle=None):
        if not self.__driver:
            self.__driver = viwid.drivers.current()

        full_rectangle = viwid.Rectangle(viwid.Point.ORIGIN, self.__size)
        rectangle = full_rectangle if rectangle is None else rectangle.clipped_by(full_rectangle)
        if rectangle.width == 0 or rectangle.height == 0:
            return
        if isinstance(text, viwid.text.Text):
            text = text.render(width=rectangle.width, height=rectangle.height)
        else:
            text = viwid.text.TextMeasuring.box_with_height(
                viwid.text.TextMeasuring.box_with_width(text, rectangle.width), rectangle.height)

        y = rectangle.top_y

        for character_line in text:
            if y >= rectangle.bottom_y:
                break

            x = rectangle.left_x

            for character in character_line:
                index = y * self.__size.width + x

                if character is None:
                    content_bytes = OffScreenCanvas._grapheme_to_bytes(None)
                elif x + character.width_on_screen > rectangle.right_x:
                    self.__overwrite_graphemes(index, (rectangle.right_x - x) * OffScreenCanvas._DEFAULT_GRAPHEME_BYTES)
                    break
                else:
                    content_bytes = OffScreenCanvas._grapheme_to_bytes(character)

                self.__overwrite_graphemes(index, content_bytes)
                if color:
                    block_attributes = OffScreenCanvas._block_attributes_from_bytes(self.__attributes,
                                                                                    self.__attributes_index(index))
                    block_attributes = BlockAttributes.get(foreground_color=self.__driver.plain_color(color),
                                                           background_color=block_attributes.background_color)
                    self.__overwrite_attributes(index, OffScreenCanvas._block_attributes_to_bytes(block_attributes))

                x += 1
            y += 1

        self._call_repainted_handlers(rectangle.top_y, rectangle.bottom_y)

    @staticmethod
    def _block_attributes_to_bytes(block_attributes: BlockAttributes) -> bytes:
        result = bytearray()
        for color in [block_attributes.foreground_color, block_attributes.background_color]:
            for color_part in (color.r, color.g, color.b, color.a):
                result += bytes((int(color_part * 255),))
        return bytes(result)

    @staticmethod
    def _block_attributes_from_bytes(buffer: bytes, index: int) -> BlockAttributes:
        return BlockAttributes(OffScreenCanvas.__block_attributes_from_bytes__color(buffer, index),
                               OffScreenCanvas.__block_attributes_from_bytes__color(buffer, index + 4))

    @staticmethod
    def _grapheme_to_bytes(content: viwid.text.Grapheme|None) -> bytes:
        if content is None:
            width_on_screen = 255
            content_str = ""
        else:
            width_on_screen = content.width_on_screen
            content_str = content.as_str
        return bytes((width_on_screen, *content_str.encode("utf-32"), *bytes(16)))[:17]

    @staticmethod
    def _grapheme_from_bytes(buffer: bytes, index: int) -> viwid.text.Grapheme|None:
        if OffScreenCanvas.__content_from_bytes__ascii is None:
            OffScreenCanvas.__content_from_bytes__ascii = [
                viwid.drivers.current().apps.text_measuring.grapheme(chr(i)) for i in range(128)]

        width_on_screen = buffer[index]
        if width_on_screen == 255:
            return None

        as_str = buffer[index+1:index+17].decode("utf-32").rstrip("\0")

        if len(as_str) == 1 and (i := ord(as_str)) < 128:
            return OffScreenCanvas.__content_from_bytes__ascii[i]

        return viwid.text.Grapheme(as_str, width_on_screen)

    @staticmethod
    def __attributes_index(i: int) -> int:
        return i * OffScreenCanvas._BLOCK_ATTRIBUTES_BYTES_LEN

    @staticmethod
    def __grapheme_index(i: int) -> int:
        return i * OffScreenCanvas._GRAPHEME_BYTES_LEN

    def __overwrite_attributes(self, index: int, buffer: bytes) -> None:
        self.__attributes = self.__attributes[:self.__attributes_index(index)] + buffer + self.__attributes[self.__attributes_index(index) + len(buffer):]

    def __overwrite_graphemes(self, index: int, buffer: bytes) -> None:
        self.__graphemes = self.__graphemes[:self.__grapheme_index(index)] + buffer + self.__graphemes[self.__grapheme_index(index) + len(buffer):]

    @staticmethod
    def __block_attributes_from_bytes__color(buffer: bytes, index: int) -> viwid.PlainColor:
        return viwid.PlainColor(buffer[index]/255, buffer[index+1]/255, buffer[index+2]/255, buffer[index+3]/255)

    __content_from_bytes__ascii = None

    _DEFAULT_BLOCK_ATTRIBUTES_BYTES = _block_attributes_to_bytes(Canvas._DEFAULT_BLOCK_ATTRIBUTES)
    _BLOCK_ATTRIBUTES_BYTES_LEN = len(_DEFAULT_BLOCK_ATTRIBUTES_BYTES)

    _DEFAULT_GRAPHEME_BYTES = _grapheme_to_bytes(Canvas._DEFAULT_GRAPHEME)
    _GRAPHEME_BYTES_LEN = len(_DEFAULT_GRAPHEME_BYTES)


class ComposingCanvas(Canvas):
    """
    Composition of multiple source canvases.

    Each source canvas has a position inside this composition (x- and y-coordinates), but are also ordered on the
    z-axis, describing which canvases are in front of which other ones.
    """

    def __init__(self, *, size: viwid.Size = viwid.Size.NULL):
        """
        :param size: The initial size.
        """
        super().__init__()
        self.__source_canvases: list[tuple[Canvas, viwid.Point]] = []
        self.__size = size
        self.__repainted_handlers = {}
        self.__resized_handlers = {}
        self.__source_canvases_heights = {}
        self.__cache = None
        self.__cache__invalid_lines = None

    @property
    def size(self):
        return self.__size

    def resize(self, size: viwid.Size) -> None:
        """
        Resize the canvas.

        :param size: The new size.
        """
        if self.__size != size:
            self.__size = size
            self.__cache = self.__cache__invalid_lines = None
            self._call_resized_handlers()

    def line(self, y):
        return self.__composition().line(y)

    def insert_source_canvas(self, index: int|None, canvas: Canvas, *,
                             position: viwid.Point = viwid.Point.ORIGIN) -> None:
        """
        Insert a new source canvas.

        It is not allowed to add the same canvas more than once.

        :param index: The insertion index. Source canvases with higher indexes are in front of the ones with a lower
                      index. If unspecified, insert it at the front of all others.
        :param canvas: The source canvas to insert.
        :param position: The position of the source canvas' top left corner inside this composition.
        """
        index = len(self.__source_canvases) if index is None else index
        self.__source_canvases.insert(index, (canvas, position))

        self.__repainted_handlers[canvas] = handle_source_repainted = functools.partial(self.__handle_source_repainted,
                                                                                        canvas)
        self.__resized_handlers[canvas] = handle_source_resized = functools.partial(self.__handle_source_resized,
                                                                                    canvas)
        self.__source_canvases_heights[canvas] = canvas.size.height

        canvas.add_resized_handler(handle_source_resized)
        canvas.add_repainted_handler(handle_source_repainted)

        self.__invalidate_cache_lines(position.y, position.y + canvas.size.height)

    def remove_source_canvas(self, source_canvas: Canvas|int) -> None:
        """
        Remove a source canvas that was added with :py:meth:`insert_source_canvas` before (raise `ValueError` if it does
        not exist).

        :param source_canvas: The source canvas to remove. Can be either an index or a canvas instance.
        """
        i_source_canvas, source_canvas, position = self.__find_source_canvas(source_canvas)

        self.__source_canvases.pop(i_source_canvas)

        source_canvas.remove_resized_handler(self.__resized_handlers.pop(source_canvas))
        source_canvas.remove_repainted_handler(self.__repainted_handlers.pop(source_canvas))
        self.__source_canvases_heights.pop(source_canvas)

        self.__invalidate_cache_lines(position.y, position.y + source_canvas.size.height)

    def set_source_canvas_index(self, source_canvas: Canvas|int, to_index: int) -> None:
        """
        Move a source canvas that was added with :py:meth:`insert_source_canvas` before, to a new index (raise
        `ValueError` if it does not exist).

        This changes the z-position, i.e. which other source canvases are in front of it (the source canvas with the
        highest index is in front of all others).

        :param source_canvas: The source canvas to move. Can be either an index or a canvas instance.
        :param to_index: The new index for this source canvas in this composition.
        """
        i_source_canvas, source_canvas, position = self.__find_source_canvas(source_canvas)

        if i_source_canvas == to_index:
            return

        self.__source_canvases.pop(i_source_canvas)
        self.__source_canvases.insert(to_index, (source_canvas, position))

        self.__invalidate_cache_lines(position.y, position.y + source_canvas.size.height)

    def set_source_canvas_position(self, source_canvas: Canvas|int, position: viwid.Point):
        """
        Move a source canvas to a new position (x- and y-coordinates).

        :param source_canvas: The source canvas to move. Can be either an index or a canvas instance.
        :param position: The new position for the source canvas' top left corner in this composition.
        """
        i_source_canvas, source_canvas, old_position = self.__find_source_canvas(source_canvas)

        if old_position != position:
            self.__source_canvases[i_source_canvas] = source_canvas, position

            self.__invalidate_cache_lines(old_position.y, old_position.y + source_canvas.size.height)
            self.__invalidate_cache_lines(position.y, position.y + source_canvas.size.height)

    @property
    def source_canvases(self) -> t.Sequence[Canvas]:
        """
        The source canvases.

        A source canvas index (various methods here accept or require them as arguments) is the position of a source
        canvas in this list.
        """
        return tuple([_[0] for _ in self.__source_canvases])

    def __handle_source_repainted(self, source_canvas, from_line, to_line):
        i_source_canvas, source_canvas, position = self.__find_source_canvas(source_canvas)
        self.__invalidate_cache_lines(from_line + position.y, to_line + position.y)

    def __handle_source_resized(self, source_canvas):
        i_source_canvas, source_canvas, position = self.__find_source_canvas(source_canvas)
        old_height = self.__source_canvases_heights[source_canvas]
        self.__source_canvases_heights[source_canvas] = source_canvas.size.height

        self.__invalidate_cache_lines(position.y, max(old_height, source_canvas.size.height))

    def __invalidate_cache_lines(self, from_line, to_line):
        from_line = max(from_line, 0)
        to_line = max(to_line, from_line)

        if self.__cache__invalid_lines is not None:
            self.__cache__invalid_lines += (to_line - len(self.__cache__invalid_lines)) * (False,)
            for i in range(from_line, to_line):
                self.__cache__invalid_lines[i] = True
        self._call_repainted_handlers(from_line, to_line)

    def __find_source_canvas(self, source_canvas: Canvas|int) -> tuple[int, Canvas, viwid.Point]:
        if isinstance(source_canvas, Canvas):
            for i_source_canvas, (source_canvas_, position) in enumerate(self.__source_canvases):
                if source_canvas_ is source_canvas:
                    source_canvas = i_source_canvas
                    break
            else:
                raise ValueError(f"not an existing source canvas: {source_canvas!r}")
        return (source_canvas, *self.__source_canvases[source_canvas])

    def __composition(self) -> Canvas:
        if self.__cache is None:
            self.__cache = OffScreenCanvas(size=self.__size)
            self.__cache__invalid_lines = [True for _ in range(self.__size.height)]

        for y, refresh_line in enumerate(self.__cache__invalid_lines):
            if refresh_line and 0 <= y < self.__size.height:
                self.__cache.set_line(y, *self.__composed_line(y))
        self.__cache__invalid_lines = []

        return self.__cache

    def __composed_line(self, y):
        attributes = []
        graphemes = []

        source_content_lines = []
        source_attribute_lines = []
        for source_canvas, offset in reversed(self.__source_canvases):
            if 0 <= (y - offset.y) < source_canvas.size.height:
                line_attributes, line_graphemes = source_canvas.line(y - offset.y)
            else:
                line_attributes, line_graphemes = None, None
            source_attribute_lines.append(line_attributes)
            source_content_lines.append(line_graphemes)

        last_attributes = last_attributes_foreground_color = last_attributes_background_color = None
        source_canvases = tuple(enumerate(reversed(self.__source_canvases)))
        for x in range(self.__size.width):
            foreground_color = None
            background_color = None
            content_ = False
            backgrounds_above_color = viwid.PlainColor.TRANSPARENT
            for i, (source_canvas, offset) in source_canvases:
                actual_x = x - offset.x
                actual_y = y - offset.y
                if actual_x >= 0 and actual_y >= 0 and actual_x < source_canvas.size.width and actual_y < source_canvas.size.height:
                    block_attributes = source_attribute_lines[i][actual_x]
                    content = source_content_lines[i][actual_x]

                    if content is None or content.as_str != " ":
                        if content_ is False:
                            content_ = content
                        if foreground_color is None:
                            foreground_color = block_attributes.foreground_color.with_color_in_front(backgrounds_above_color)
                    background_color = block_attributes.background_color.with_color_in_front(backgrounds_above_color)
                    if block_attributes.background_color.a > 0.99:
                        break

                    backgrounds_above_color = block_attributes.background_color.with_color_in_front(backgrounds_above_color)

            foreground_color = foreground_color or viwid.PlainColor.TRANSPARENT
            background_color = background_color or viwid.PlainColor.TRANSPARENT
            if last_attributes is None or (last_attributes_foreground_color != foreground_color) or (last_attributes_background_color != background_color):
                last_attributes_foreground_color = foreground_color
                last_attributes_background_color = background_color
                last_attributes = BlockAttributes.get(foreground_color=foreground_color, background_color=background_color)
            attributes.append(last_attributes)

            graphemes.append(Canvas._DEFAULT_GRAPHEME if (content_ is False) else content_)

        return attributes, graphemes


class BlankSemiOpaqueAreaCanvas(Canvas):
    """
    A (non-modifiable) canvas that shows a fixed character (usually space) everywhere with a given styling information.

    This is typically used for blank (often semi-transparent) layers.
    """

    _BLOCK_ATTRIBUTES = BlockAttributes.get(foreground_color="#0000", background_color="#0008")

    def __init__(self, *, block_attributes: BlockAttributes = _BLOCK_ATTRIBUTES,
                 grapheme: "viwid.text.Grapheme" = Canvas._DEFAULT_GRAPHEME, size: viwid.Size = viwid.Size.NULL):
        """
        :param block_attributes: The styling information. If unspecified, use (black text color and) a black background
                                 with 50% opacity.
        :param grapheme: The grapheme to fill the area with. If unspecified, use spaces. This must be a grapheme with
                         width on screen of 1.
        :param size: The initial size.
        """
        super().__init__()
        self.__block_attributes = block_attributes
        self.__grapheme = grapheme
        self.__size = size

    def resize(self, size: viwid.Size) -> None:
        """
        Resize the canvas.

        :param size: The new size.
        """
        self.__size = size
        self._call_resized_handlers()

    @property
    def size(self):
        return self.__size

    def line(self, y):
        return (self.__size.width * (self.__block_attributes,)), (self.__size.width * (self.__grapheme,))
