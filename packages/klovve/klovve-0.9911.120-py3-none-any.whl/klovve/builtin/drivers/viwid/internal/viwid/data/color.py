#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
Data structures for color handling.
"""
import typing as t


class PlainColor:
    """
    Representation for a color (just a single one; see also :py:class:`Color`).

    It has a value (with floating point precision) for red, green, blue and for the alpha channel.
    """

    #: The red value (between 0 and 1).
    r: float
    #: The green value (between 0 and 1).
    g: float
    #: The blue value (between 0 and 1).
    b: float
    #: The alpha value (between 0 and 1).
    a: float

    #: Fully transparent color.
    TRANSPARENT: t.ClassVar["PlainColor"]

    def __init__(self, r: float, g: float, b: float, a: float = 1.0):
        """
        See also :py:meth:`get`.

        :param r: The red value (between 0 and 1).
        :param g: The green value (between 0 and 1).
        :param b: The blue value (between 0 and 1).
        :param a: The alpha value (between 0 and 1).
        """
        self.r = r
        self.g = g
        self.b = b
        self.a = a

    @staticmethod
    def get(color: "TPlainColorInput") -> "PlainColor":
        """
        Return a :py:class:`PlainColor` for a plain color input.

        :param color: A plain color in some representation.
        """
        if isinstance(color, PlainColor):
            return color
        if len(color) == 4:
            r, g, b, a = 2 * color[1], 2 * color[2], 2 * color[3], "FF"
        elif len(color) == 5:
            r, g, b, a = 2 * color[1], 2 * color[2], 2 * color[3], 2 * color[4]
        elif len(color) == 7:
            r, g, b, a = color[1:3], color[3:5], color[5:7], "FF"
        elif len(color) == 9:
            r, g, b, a = color[1:3], color[3:5], color[5:7], color[7:9]
        else:
            raise ValueError(f"invalid color {color!r}")
        return PlainColor(int(r, base=16) / 255,
                          int(g, base=16) / 255,
                          int(b, base=16) / 255,
                          int(a, base=16) / 255)

    def with_color_in_front(self, front_color: "TPlainColorInput") -> "PlainColor":
        """
        Return the result of this color being overlaid by another color in front of it.

        :param front_color: The color in front.
        """
        front_color = PlainColor.get(front_color)

        if front_color.a == 1:
            return front_color
        if front_color.a == 0:
            return self

        return PlainColor((front_color.r * front_color.a) + (self.r * (1 - front_color.a)),
                          (front_color.g * front_color.a) + (self.g * (1 - front_color.a)),
                          (front_color.b * front_color.a) + (self.b * (1 - front_color.a)),
                          1 - ((1 - front_color.a) * (1 - self.a)))

    def as_html(self) -> str:
        """
        Return the html color string.
        """
        return (f"#{PlainColor.__as_html__component(self.r)}{PlainColor.__as_html__component(self.g)}"
                f"{PlainColor.__as_html__component(self.b)}{PlainColor.__as_html__component(self.a)}")

    @staticmethod
    def __as_html__component(i) -> str:
        result = hex(int(i * 255))[2:]
        return (2 - len(result)) * "0" + result


PlainColor.TRANSPARENT = PlainColor(0, 0, 0, 0)


TPlainColorInput = PlainColor|str


class Color:
    """
    Representation for a color for different terminal capabilities.

    This includes one :py:class:`PlainColor` for the original color definition and a fallback one for low color
    capabilities. This allows the definition of two colors that are very similar, but still map to different colors on
    low color terminals.
    """

    #: The original (best) color representation.
    base: PlainColor
    #: The fallback color for terminals with low color capabilities.
    fallback: PlainColor

    #: Fully transparent color.
    TRANSPARENT: t.ClassVar["Color"]

    def __init__(self, base: PlainColor, fallback: PlainColor):
        """
        See also :py:meth:`get`.

        :param base: The original (best) color representation.
        :param fallback: The fallback color for terminals with low color capabilities.
        """
        self.base = base
        self.fallback = fallback

    @staticmethod
    def get(color: "TColorInput") -> "Color":
        """
        Return a :py:class:`Color` for a color input.

        :param color: A color in some representation.
        """
        if isinstance(color, Color):
            return color
        if isinstance(color, PlainColor):
            return Color(color, color)
        color_str = color.split(" ")
        if len(color_str) == 1:
            base = fallback = PlainColor.get(color_str[0])
        else:
            base = PlainColor.get(color_str[0])
            fallback = PlainColor.get(color_str[1])
        return Color(base, fallback)

    def with_color_in_front(self, front_color: "TColorInput") -> "Color":
        """
        Return the result of this color being overlaid by another color in front of it.

        :param front_color: The color in front.
        """
        front_color = Color.get(front_color)
        return Color(self.base.with_color_in_front(front_color.base),
                     self.fallback.with_color_in_front(front_color.fallback))


Color.TRANSPARENT = Color(PlainColor.TRANSPARENT, PlainColor.TRANSPARENT)


TColorInput = PlainColor|Color|str
