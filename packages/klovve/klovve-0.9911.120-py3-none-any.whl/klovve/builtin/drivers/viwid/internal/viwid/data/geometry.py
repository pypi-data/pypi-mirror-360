#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
Data structures for geometry.
"""
import enum
import typing as t


class Orientation(enum.Enum):
    """
    Specifies on which axis to align elements.
    """

    #: Vertical orientation.
    VERTICAL = enum.auto()

    #: Horizontal orientation.
    HORIZONTAL = enum.auto()


class Alignment(enum.Enum):
    """
    Specifies how an elements want to align within its available space on a particular axis.

    Usually, the available space is at least the space that a widget demanded, or more.
    """

    #: The elements wants to align to the start of the available range.
    START = enum.auto()

    #: The elements wants to align to the center of the available range.
    CENTER = enum.auto()

    #: The elements wants to align to the end of the available range.
    END = enum.auto()

    #: The elements wants to fill the available range completely, but is not greedy about how much that is.
    FILL = enum.auto()

    #: The elements wants to fill the available range completely and wants to get as much space as possible.
    FILL_EXPANDING = enum.auto()


class _Point:

    @t.overload
    def __init__(self, x: int, y: int):
        """
        :param x: The x-coordinate.
        :param y: The y-coordinate.
        """

    @t.overload
    def __init__(self, point_or_offset: "_Point"):
        """
        :param point_or_offset: the point or offset to copy.
        """

    def __init__(self, x, y=None):
        if y is None:
            x, y = x.x, x.y
        self.__x = x
        self.__y = y

    @property
    def x(self) -> int:
        """
        The x-coordinate.
        """
        return self.__x

    @property
    def y(self) -> int:
        """
        The y-coordinate.
        """
        return self.__y

    @t.overload
    def moved_by(self, offset: "Offset") -> t.Self:
        """
        Return this point or offset, moved by a given offset.

        :param offset: The offset to add.
        """

    @t.overload
    def moved_by(self, x: int = 0, y: int = 0) -> t.Self:
        """
        Return this point or offset, moved by given x- and y-values.

        :param x: The offset value for the x-coordinate.
        :param y: The offset value for the y-coordinate.
        """

    def moved_by(self, x=0, y=0):
        if isinstance(x, _Point):
            x, y = x.x, x.y
        if x == 0 and y == 0:
            return self
        return type(self)(self.__x+x, self.__y+y)

    def with_x(self, x: int) -> "Point":
        """
        Return this point or offset, but with another x-coordinate.

        :param x: The new x-coordinate.
        """
        return Point(x, self.__y)

    def with_y(self, y: int) -> "Point":
        """
        Return this point or offset, but with another y-coordinate.

        :param y: The new y-coordinate.
        """
        return Point(self.__x, y)

    def __eq__(self, o: object) -> bool:
        return isinstance(o, _Point) and (self.__x == o.__x) and (self.__y == o.__y)

    def __hash__(self) -> int:
        return self.__x - self.__y

    def __add__(self, other):
        return self.moved_by(other)

    def __sub__(self, other):
        return self + Offset(-other.__x, -other.__y)


class Point(_Point):
    """
    A point in a 2-dimensional surface, with x- and y-coordinates.
    """

    # The origin point (x=0, y=0).
    ORIGIN: t.ClassVar["Point"]

    def __repr__(self):
        return f"Point(x={self.x!r}, y={self.y!r})"


Point.ORIGIN = Point(0, 0)


class Offset(_Point):
    """
    An offset in a 2-dimensional surface, with x- and y-coordinates. This is technically identical to a
    :py:class:`Point` but signals a different purpose (a movement instead of a position).
    """

    # The null offset (x=0, y=0).
    NULL: t.ClassVar["Offset"]

    def __repr__(self):
        return f"Offset(x={self.x!r}, y={self.y!r})"

    def __rmul__(self, other: int):
        return Offset(other * self.x, other * self.y)

    def __neg__(self):
        return Offset(-self.x, -self.y)

    def __add__(self, other):
        return Offset(self.x+other.x, self.y+other.y)

    def __sub__(self, other):
        return Offset(self.x-other.x, self.y-other.y)


Offset.NULL = Offset(0, 0)


class Size:
    """
    A 2-dimensional size, with a width and a height.
    """

    # The null size (width=0, height=0).
    NULL: t.ClassVar["Size"]

    @t.overload
    def __init__(self, width: int, height: int):
        """
        :param width: The size's width component.
        :param height: The size's height component.
        """

    @t.overload
    def __init__(self, offset: "Offset"):
        """
        :param offset: The offset to interpret as size (using `x` as `width` and `y` as `height`).
        """

    def __init__(self, width, height=None):
        if height is None:
            width, height = width.x, width.y

        self.__width = width
        self.__height = height

    @property
    def width(self) -> int:
        """
        The size's width component.
        """
        return self.__width

    @property
    def height(self) -> int:
        """
        The size's height component.
        """
        return self.__height

    @property
    def area(self) -> int:
        """
        The area (i.e. width*height) of this size.
        """
        return self.__width * self.__height

    @t.overload
    def extended_by(self, size: "Size") -> "Size":
        """
        Return this size extended by another one (i.e. with component-wise addition).

        :param size: The other size to add.
        """

    @t.overload
    def extended_by(self, offset: Offset) -> "Size":
        """
        Return this size extended by a given offset (i.e. with component-wise addition).

        :param offset: The offset to add.
        """

    @t.overload
    def extended_by(self, width: int = 0, height: int = 0) -> "Size":
        """
        Return this size extended by given width and height values (i.e. with component-wise addition).

        :param width: The width to add.
        :param height: The height to add.
        """

    def extended_by(self, width=0, height=0):
        if isinstance(width, Size):
            width, height = width.width, width.height
        elif isinstance(width, _Point):
            width, height = width.x, width.y
        if width == 0 and height == 0:
            return self
        return Size(self.__width+width, self.__height+height)

    @t.overload
    def shrunk_by(self, size: "Size") -> "Size":
        """
        Return this size shrunk by another one (i.e. with component-wise subtraction).

        :param size: The other size to subtract.
        """

    @t.overload
    def shrunk_by(self, offset: Offset) -> "Size":
        """
        Return this size shrunk by a given offset (i.e. with component-wise subtraction).

        :param offset: The offset to subtract.
        """

    @t.overload
    def shrunk_by(self, width: int = 0, height: int = 0) -> "Size":
        """
        Return this size shrunk by given width and height values (i.e. with component-wise subtraction).

        :param width: The width to subtract.
        :param height: The height to subtract.
        """

    def shrunk_by(self, width=0, height=0):
        if isinstance(width, Size):
            width, height = width.width, width.height
        elif isinstance(width, _Point):
            width, height = width.x, width.y
        return self.extended_by(-width, -height)

    def with_width(self, width: int) -> "Size":
        """
        Return this size, but with another width component.

        :param width: The new width component.
        """
        return Size(width, self.__height)

    def with_height(self, height: int) -> "Size":
        """
        Return this size, but with another height component.

        :param height: The new height component.
        """
        return Size(self.__width, height)

    def __repr__(self):
        return f"Size(width={self.__width!r}, height={self.__height!r})"

    def __eq__(self, other):
        return isinstance(other, Size) and self.__width == other.__width and self.__height == other.__height

    def __hash__(self):
        return self.__width - self.__height

    def __add__(self, other):
        return self.extended_by(other)

    def __sub__(self, other):
        return self.shrunk_by(other)


Size.NULL = Size(0, 0)


class Rectangle:
    """
    A rectangle in a 2-dimensional space with its origin in the top left corner (the y-axis going down).
    """

    # The null rectangle (x1=0, y1=0, x2=0, y2=0).
    NULL: t.ClassVar["Rectangle"]

    def __init__(self, from_point: Point, to: t.Union[Point, Size]):
        """
        :param from_point: The top left corner of the rectangle.
        :param to: Either the bottom left corner or the size of the rectangle. In the former case, coordinates
                   automatically get turned if they are in the wrong order.
        """
        if isinstance(to, Size):
            to = from_point.moved_by(to.width, to.height)
        self.__top_left = Point(min(from_point.x, to.x), min(from_point.y, to.y))
        self.__bottom_right = Point(max(from_point.x, to.x), max(from_point.y, to.y))

    @property
    def top_left(self) -> Point:
        """
        The top left corner of the rectangle.
        """
        return self.__top_left

    @property
    def bottom_right(self) -> Point:
        """
        The top bottom right of the rectangle.
        """
        return self.__bottom_right

    @property
    def left_x(self) -> int:
        """
        The x-coordinate of the left side of the rectangle.

        This is (assuming the rectangle area is not 0) the first x-coordinate inside the rectangle.
        """
        return self.__top_left.x

    @property
    def right_x(self) -> int:
        """
        The x-coordinate of the right side of the rectangle.

        This is the first x-coordinate behind the rectangle (i.e. considered to be not inside it anymore).
        """
        return self.__bottom_right.x

    @property
    def top_y(self) -> int:
        """
        The y-coordinate of the top side of the rectangle.

        This is (assuming the rectangle area is not 0) the first y-coordinate inside the rectangle.
        """
        return self.__top_left.y

    @property
    def bottom_y(self) -> int:
        """
        The y-coordinate of the bottom side of the rectangle.

        This is the first y-coordinate behind the rectangle (i.e. considered to be not inside it anymore).
        """
        return self.__bottom_right.y

    @property
    def width(self) -> int:
        """
        The width of the rectangle.
        """
        return self.right_x - self.left_x

    @property
    def height(self) -> int:
        """
        The height of the rectangle.
        """
        return self.bottom_y - self.top_y

    @property
    def size(self) -> Size:
        """
        The size of the rectangle.
        """
        return Size(self.width, self.height)

    @property
    def area(self) -> int:
        """
        The area of the rectangle.
        """
        return self.width * self.height

    @t.overload
    def moved_by(self, offset: Offset) -> "Rectangle":
        """
        Return this rectangle moved by a given offset.

        :param offset: The offset.
        """

    @t.overload
    def moved_by(self, x: int = 0, y: int = 0) -> "Rectangle":
        """
        Return this rectangle moved by given x- and y-coordinates.

        :param x: The x-coordinate offset.
        :param y: The y-coordinate offset.
        """

    def moved_by(self, x=0, y=0):
        if isinstance(x, Offset):
            x, y = x.x, x.y
        if x == 0 and y == 0:
            return self
        return Rectangle(self.__top_left.moved_by(x, y), self.size)

    def clipped_by(self, clipping_rect: "Rectangle") -> "Rectangle":
        """
        Return this rectangle clipped by another one.

        This is the largest rectangle that is completely included in this rectangle as well as the given one.

        :param clipping_rect: The clipping rectangle.
        """
        new_top_left = Point(max(self.left_x, clipping_rect.left_x), max(self.top_y, clipping_rect.top_y))
        new_bottom_right = Point(min(self.right_x, clipping_rect.right_x), min(self.bottom_y, clipping_rect.bottom_y))
        if new_top_left == self.__top_left and new_bottom_right == self.__bottom_right:
            return self
        if new_bottom_right.x < new_top_left.x:
            return Rectangle.NULL
        if new_bottom_right.y < new_top_left.y:
            return Rectangle.NULL
        return Rectangle(new_top_left, new_bottom_right)

    def contains(self, point: Point) -> bool:
        """
        Return whether a given point is inside this rectangle.

        :param point: The point.
        """
        return self.left_x <= point.x < self.right_x and self.top_y <= point.y < self.bottom_y

    def __repr__(self):
        return f"Rectangle(from_point={self.__top_left!r}, to={self.size!r})"

    def __eq__(self, other):
        return (isinstance(other, Rectangle)
                and self.__top_left == other.__top_left and self.__bottom_right == other.__bottom_right)

    def __hash__(self):
        return hash(self.__top_left) - hash(self.__bottom_right)


Rectangle.NULL = Rectangle(Point.ORIGIN, Size.NULL)


class Margin:
    """
    A margin specification with four components, one for each edge of some rectangular body.
    """

    #: The null margin (top=0, right=0, bottom=0, left=0).
    NULL: t.ClassVar["Margin"]

    @t.overload
    def __init__(self, *, all: int):
        """
        :param all: The value for all four components.
        """

    @t.overload
    def __init__(self, top: int = 0, right: int = 0, bottom: int = 0, left: int = 0):
        """
        :param top: The value for the top component.
        :param right: The value for the right component.
        :param bottom: The value for the bottom component.
        :param left: The value for the left component.
        """

    @t.overload
    def __init__(self, *, horizontal: int = 0, vertical: int = 0):
        """
        :param horizontal: The value for the left and right components.
        :param vertical: The value for the top and bottom components.
        """

    def __init__(self, top: int = 0, right: int = 0, bottom: int = 0, left: int = 0, *,
                 horizontal: int|None = None, vertical: int|None = None, all: int|None = None):
        if all is not None:
            top = right = bottom = left = all
        if (horizontal is not None) or (vertical is not None):
            right = left = horizontal or 0
            top = bottom = vertical or 0
        top, right, bottom, left = int(max(0, top)), int(max(0, right)), int(max(0, bottom)), int(max(0, left))
        self.__top, self.__right, self.__bottom, self.__left = top, right, bottom, left
        self.__width, self.__height = left + right, top + bottom

    @property
    def top(self) -> int:
        """
        The margin value for the top edge.
        """
        return self.__top

    @property
    def right(self) -> int:
        """
        The margin value for the right edge.
        """
        return self.__right

    @property
    def bottom(self) -> int:
        """
        The margin value for the bottom edge.
        """
        return self.__bottom

    @property
    def left(self) -> int:
        """
        The margin value for the left edge.
        """
        return self.__left

    @property
    def width(self) -> int:
        """
        The sum of the margin values for the left and right edge.
        """
        return self.__width

    @property
    def height(self) -> int:
        """
        The sum of the margin values for the top and bottom edge.
        """
        return self.__height


Margin.NULL = Margin(all=0)
