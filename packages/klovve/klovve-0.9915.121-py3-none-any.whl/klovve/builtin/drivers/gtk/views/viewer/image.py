#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import sys

import klovve.builtin.drivers.gtk
import klovve.ui.utils
from klovve.builtin.drivers.gtk import Gdk, GdkPixbuf, GLib, GObject, Gtk


class Image(klovve.builtin.drivers.gtk.ViewMaterialization[klovve.views.viewer.Image]):

    def create_native(self):
        return self.new_native(_Outer, self.piece, source=self.piece.bind(two_way=False).source)


class _Outer(Gtk.Widget):

    @GObject.Property
    def pixbuf(self) -> GdkPixbuf.Pixbuf:
        return self.__image.get_pixbuf()

    @pixbuf.setter
    def pixbuf(self, pixbuf: GdkPixbuf.Pixbuf):
        self.__image.set_pixbuf(pixbuf)

    @GObject.Property
    def source(self) -> bytes:
        return self.__source

    @source.setter
    def source(self, source: bytes):
        self.__source = source
        if source:
            loader = GdkPixbuf.PixbufLoader()
            loader.write(source)
            loader.close()
            self.pixbuf = loader.get_pixbuf()
        else:
            self.pixbuf = None

    def set_source(self, source: bytes):
        self.source = source

    def do_measure(self, orientation, for_size):
        return 0, 100, -1, -1

    def do_size_allocate(self, width, height, _):
        allocation = Gdk.Rectangle()
        allocation.x, allocation.y, allocation.width, allocation.height = 0, 0, width, height
        self.__image.size_allocate(allocation, -1)
        self.__image._refresch()

    def __init__(self, **kwargs):
        self.__source = None
        self.__mouse_button_pressed_at = None
        super().__init__(**kwargs)
        self.__mx = self.__my = 0
        self.__image = _Image(visible=True)
        self.__image.insert_after(self, None)
        foo = Gtk.EventControllerScroll()
        foo.props.flags = Gtk.EventControllerScrollFlags.BOTH_AXES
        foo.connect("scroll", self.__on_mouse_wheel)
        self.add_controller(foo)
        foo = Gtk.EventControllerMotion()
        foo.connect("motion", self.__on_mouse_moved)
        self.add_controller(foo)
        foo = Gtk.GestureClick()
        foo.connect("pressed", self.__on_mouse_button_pressed)
        foo.connect("released", self.__on_mouse_button_released)
        self.add_controller(foo)

    def __on_mouse_wheel(self, _, dx, dy):
        discrete_adapt, smooth_adapt_factor = 0.1, 0.1
        zoom_factor_adapt = dy * discrete_adapt
        center_x = self.__mx / (self.__image.display_width or 1)
        center_y = self.__my / (self.__image.display_height or 1)
        self.__image.zoom_out(zoom_factor_adapt, center_x=center_x, center_y=center_y)

    def __on_mouse_moved(self, _, x, y):
        self.__mx, self.__my = x, y
        if self.__mouse_button_pressed_at:
            new_image_coordinates = self.__image.display_coordinates_to_image_coordinates(x, y)
            self.__image.props.image_offset_x += self.__mouse_button_pressed_at[0] - new_image_coordinates[0]
            self.__image.props.image_offset_y += self.__mouse_button_pressed_at[1] - new_image_coordinates[1]
            self.__mouse_button_pressed_at = self.__image.display_coordinates_to_image_coordinates(x, y)

    def __on_mouse_button_pressed(self, _, n_press, x, y):
        self.__mouse_button_pressed_at = self.__image.display_coordinates_to_image_coordinates(x, y)

    def __on_mouse_button_released(self, _, n_press, x, y):
        self.__mouse_button_pressed_at = None


class _Image(Gtk.Overlay):

    def __init__(self, **kwargs):
        self.__zoom_factor = 0.0
        self.__dist_left, self.__dist_top, self.__dist_right, self.__dist_bottom = 4, 4, 4, 4
        self.__image_offset_x = self.__image_offset_y = 0
        self.__last_scaled_pixbuf_width = -1
        self.__pixbuf = None
        super().__init__(**kwargs)
        self.__fixed = Gtk.Fixed()
        self.__image = Gtk.Image()
        self.__fixed.put(self.__image, 0, 0)
        self.set_child(self.__fixed)
        self.__buttonbox = Gtk.Box(halign=Gtk.Align.START, valign=Gtk.Align.END, margin_bottom=5, margin_start=5)
        btn_zoom_out = Gtk.Button(icon_name="zoom-out", tooltip_text=klovve.ui.utils.tr("ZOOM_OUT"),
                                  css_classes=["klv_image_zoom_out_button"])
        btn_zoom_in = Gtk.Button(icon_name="zoom-in", tooltip_text=klovve.ui.utils.tr("ZOOM_IN"),
                                 css_classes=["klv_image_zoom_in_button"])
        btn_zoom_out.connect("clicked", lambda *_: self.zoom_out())
        btn_zoom_in.connect("clicked", lambda *_: self.zoom_in())
        self.__buttonbox.append(btn_zoom_out)
        self.__buttonbox.append(btn_zoom_in)
        self.add_overlay(self.__buttonbox)

    def _refresch(self):
        GLib.idle_add(self.__refresh)

    def display_coordinates_to_image_coordinates(self, x: float, y: float) -> tuple[float, float]:
        return (self.props.image_offset_x + (x / self.props.zoom_factor),
                self.props.image_offset_y + (y / self.props.zoom_factor))

    def image_coordinates_to_display_coordinates(self, x: float, y: float) -> tuple[float, float]:
        return ((x - self.props.image_offset_x) * self.props.zoom_factor,
                (y - self.props.image_offset_y) * self.props.zoom_factor)

    def __refresh(self, widget=None, *_, force=False):
        self.__ensure_config_correct()
        if self.props.pixbuf:
            scaled_pixbuf_width = max(1, round(self.original_image_width * self.props.zoom_factor))
            scaled_pixbuf_height = max(1, round(self.original_image_height * self.props.zoom_factor))
            if force or (scaled_pixbuf_width != self.__last_scaled_pixbuf_width):
                scaled_pixbuf = self.props.pixbuf.scale_simple(scaled_pixbuf_width, scaled_pixbuf_height,
                                                               GdkPixbuf.InterpType.BILINEAR)
                self.__image.set_from_pixbuf(scaled_pixbuf)
                self.__image.set_size_request(scaled_pixbuf_width, scaled_pixbuf_height)
                self.__last_scaled_pixbuf_width = scaled_pixbuf_width
            image_moveto_x = int(-self.props.image_offset_x * self.props.zoom_factor)
            image_moveto_y = int(-self.props.image_offset_y * self.props.zoom_factor)

            now_x, now_y = self.__fixed.get_child_position(self.__image)

            if (now_x != image_moveto_x) or (now_y != image_moveto_y):
                move = lambda: self.__fixed.move(self.__image, image_moveto_x, image_moveto_y)
                if widget and False:
                    GLib.idle_add(move)
                else:
                    move()
        else:
            self.__image.clear()

    def __ensure_config_correct(self):
        self.__dist_bottom = self.__dist_top + self.__buttonbox.get_allocated_height()
        disted_display_width = max(0, self.display_width - self.__dist_left - self.__dist_right)
        disted_display_height = max(0, self.display_height - self.__dist_top - self.__dist_bottom)
        min_zoom_factor = max(0.0001, min(disted_display_width / (self.original_image_width or sys.maxsize),
                                          disted_display_height / (self.original_image_height or sys.maxsize)))
        self.__zoom_factor = min(max(min_zoom_factor, self.__zoom_factor), 2.0)
        max_image_offset_x = self.original_image_width - (self.display_width - self.__dist_right) / self.__zoom_factor
        max_image_offset_y = self.original_image_height - (self.display_height
                                                           - self.__dist_bottom) / self.__zoom_factor

        if max_image_offset_x < 0:
            max_image_offset_x /= 2
        if max_image_offset_y < 0:
            max_image_offset_y /= 2

        self.__image_offset_x = int(min(max(-self.__dist_left / self.__zoom_factor, self.__image_offset_x),
                                        max_image_offset_x))
        self.__image_offset_y = int(min(max(-self.__dist_top / self.__zoom_factor, self.__image_offset_y),
                                        max_image_offset_y))

    @GObject.Property
    def pixbuf(self) -> GdkPixbuf.Pixbuf:
        return self.__pixbuf

    @pixbuf.setter
    def pixbuf(self, pixbuf: GdkPixbuf.Pixbuf):
        self.__pixbuf = pixbuf
        self.__refresh(force=True)

    def get_pixbuf(self):
        return self.pixbuf

    def set_pixbuf(self, pixbuf):
        self.pixbuf = pixbuf

    @GObject.Property
    def zoom_factor(self) -> float:
        return self.__zoom_factor

    @zoom_factor.setter
    def zoom_factor(self, zoom_factor):
        self.__zoom_factor = zoom_factor
        self.__refresh()

    @GObject.Property
    def image_offset_x(self) -> int:
        return self.__image_offset_x

    @image_offset_x.setter
    def image_offset_x(self, image_offset_x):
        self.__image_offset_x = image_offset_x
        self.__refresh()

    @GObject.Property
    def image_offset_y(self) -> int:
        return self.__image_offset_y

    @image_offset_y.setter
    def image_offset_y(self, image_offset_y):
        self.__image_offset_y = image_offset_y
        self.__refresh()

    @property
    def original_image_width(self) -> int:
        return self.__pixbuf.props.width if self.__pixbuf else 0

    @property
    def original_image_height(self) -> int:
        return self.__pixbuf.props.height if self.__pixbuf else 0

    @property
    def display_width(self) -> int:
        return self.get_allocated_width()

    @property
    def display_height(self) -> int:
        return self.get_allocated_height()

    def zoom_in(self, by: float = 0.1, *, center_x: float = 0.5, center_y: float = 0.5) -> None:
        image_display_width_before = self.display_width / self.props.zoom_factor
        image_display_height_before = self.display_height / self.props.zoom_factor
        self.zoom_factor = self.props.zoom_factor * (1 + by)
        image_display_width_after = self.display_width / self.props.zoom_factor
        image_display_height_after = self.display_height / self.props.zoom_factor
        self.props.image_offset_x += (image_display_width_before - image_display_width_after) * center_x
        self.props.image_offset_y += (image_display_height_before - image_display_height_after) * center_y

    def zoom_out(self, by: float = 0.1, *, center_x: float = 0.5, center_y: float = 0.5) -> None:
        self.zoom_in(-by, center_x=center_x, center_y=center_y)
