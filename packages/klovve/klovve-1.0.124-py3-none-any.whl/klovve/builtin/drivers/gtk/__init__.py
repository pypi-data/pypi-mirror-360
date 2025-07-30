#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
Graphical GTK-based Klovve driver.

This is the primary driver (and the only fully supported on).
"""
import abc
import os
import pathlib
import typing as t

import klovve.data.list
import klovve.driver.loop
import klovve.object
from klovve.builtin.drivers.gtk.loop import EventLoop

import gi
gi.require_version("Gtk", "4.0")
GLib = Gtk = Gdk = GdkPixbuf = Gio = GObject = Pango = object()  # just a bit less trouble in the IDE
# noinspection PyUnresolvedReferences
from gi.repository import GLib
# noinspection PyUnresolvedReferences
from gi.repository import Gtk
# noinspection PyUnresolvedReferences
from gi.repository import Gdk
# noinspection PyUnresolvedReferences
from gi.repository import GdkPixbuf
# noinspection PyUnresolvedReferences
from gi.repository import Gio
# noinspection PyUnresolvedReferences
from gi.repository import GObject
# noinspection PyUnresolvedReferences
from gi.repository import Pango


class Driver(klovve.driver.BaseDriver[Gtk.Widget]):

    __loop = klovve.driver.loop.DefaultDriverLoop(EventLoop())
    __initialized = False

    @classmethod
    def level(cls):
        return klovve.driver.Driver.LEVEL_GRAPHICAL

    def __init__(self):
        if not Driver.__initialized:
            Driver.__initialized = True

            fg_color = Gtk.Label().get_color()
            mode = "dark" if ((fg_color.red + fg_color.green + fg_color.blue) / 3 > 0.5) else "light"

            for css_file_name in ("main.css", f"main-{mode}.css"):
                css_provider = Gtk.CssProvider()
                css_provider.load_from_path(f"{os.path.dirname(__file__)}/-data/{css_file_name}")
                Gtk.StyleContext.add_provider_for_display(Gdk.Display.get_default(), css_provider,
                                                          Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        super().__init__(Driver.__loop)

    def _show_window(self, materialization):
        materialization.native.present()

    def _close_window(self, materialization):
        materialization.native.close()
        materialization.native.destroy()

    async def _show_dialog(self, dialog, result_future, dialog_body_native, view_anchor, title, is_inline, is_modal,
                           is_closable_by_user):
        if is_inline:
            if is_closable_by_user:
                outer_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
                close_btn = Gtk.Button(label="\U0001F5D9", has_frame=False, can_focus=False, valign=Gtk.Align.START)
                close_btn.connect("clicked", lambda *_: result_future.set_result(None))
                outer_box.append(close_btn)
                outer_box.append(dialog_body_native)
                dialog_body_native = outer_box

            popover = Gtk.Popover(autohide=is_modal)
            popover.set_child(dialog_body_native)
            popover.insert_after(view_anchor._materialization.native, None)

            def __closed(*_):
                if is_modal:
                    if not is_closable_by_user:
                        if not result_future.done():
                            popover.popup()
                        return
                result_future.set_result(None)
            popover.connect("closed", __closed)

            popover.popup()
            await result_future
            popover.popdown()

        else:
            dlg = Gtk.Window(transient_for=self.__view_anchor_window(view_anchor), modal=is_modal,
                             deletable=is_closable_by_user, title=title)
            dlg.set_child(dialog_body_native)

            def __close_request(*_):
                if not is_closable_by_user:
                    return True
                result_future.set_result(None)
            dlg.connect("close-request", __close_request)

            dlg.present()
            await result_future
            dlg.close()
            dlg.destroy()

    async def _show_special_dialog(self, dialog, result_future, view_anchor, title, is_inline, is_modal,
                                   is_closable_by_user):
        if isinstance(dialog, (klovve.ui.dialog.Filesystem.OpenFileDialog,
                               klovve.ui.dialog.Filesystem.SaveFileDialog,
                               klovve.ui.dialog.Filesystem.OpenDirectoryDialog)):
            if isinstance(dialog, klovve.ui.dialog.Filesystem.OpenFileDialog):
                gtk_dialog_name = "open"
                filters = tuple(dialog.filters)
            elif isinstance(dialog, klovve.ui.dialog.Filesystem.SaveFileDialog):
                gtk_dialog_name = "save"
                filters = tuple(dialog.filters)
            elif isinstance(dialog, klovve.ui.dialog.Filesystem.OpenDirectoryDialog):
                gtk_dialog_name = "select_folder"
                filters = None
            else:
                raise RuntimeError("internal error")

            if filters is None:
                gtk_filters = None
            else:
                gtk_filters = Gio.ListStore()
                for filter_patterns, filter_label in filters:
                    Gtk.FileFilter(name=filter_label, patterns=tuple(filter_patterns))
                    gtk_filters.append(Gtk.FileFilter(name=filter_label or None, patterns=tuple(filter_patterns)))

            gtk_file_dialog = Gtk.FileDialog(
                title=title, modal=is_modal, accept_label=klovve.ui.utils.tr("OK"), filters=gtk_filters,
                initial_folder=(Gio.File.new_for_path(str(dialog.start_in_directory))
                                if dialog.start_in_directory else None))
            getattr(gtk_file_dialog, gtk_dialog_name)(
                self.__view_anchor_window(view_anchor), None,
                (lambda _, gtk_async_result: self.__show_special_dialog__set_result(
                    gtk_file_dialog, result_future, gtk_async_result, gtk_dialog_name)))

            await result_future

        else:
            raise RuntimeError(f"invalid special dialog {dialog!r}")

    def __view_anchor_window(self, view_anchor):
        view_anchor_window = view_anchor._materialization.native
        while not isinstance(view_anchor_window, (Gtk.Window, type(None))):
            view_anchor_window = view_anchor_window.get_parent()
        return view_anchor_window

    def __show_special_dialog__set_result(self, gtk_file_dialog, result_future, gtk_async_result, gtk_dialog_name):
        try:
            result = getattr(gtk_file_dialog, f"{gtk_dialog_name}_finish")(gtk_async_result).get_path()
        except GLib.GError:
            result_future.set_result(None)
            return
        result_future.set_result(pathlib.Path(result))

    @staticmethod
    def __1em_in_px():
        pango_context = Gtk.Label().get_pango_context()
        metrics = pango_context.get_metrics(pango_context.get_font_description(), pango_context.get_language())
        return (metrics.get_ascent() + metrics.get_descent()) / Pango.SCALE

    _1em_in_px = __1em_in_px()


def em_to_px(em: float, *, as_int: bool = True) -> float:
    result = em * Driver._1em_in_px
    if as_int:
        result = round(result)
    return result


class ViewMaterialization[TPiece: "klovve.ui.Piece"](Driver._BaseViewMaterialization[TPiece, Gtk.Widget, type[Gtk.Widget]], abc.ABC):

    def new_native(self, native_type_spec, view=None, **kwargs):
        # this avoids the Python-side of widgets get GCed (which would e.g. break effects on them)
        view_native = super().new_native(native_type_spec, view, **kwargs)
        view_native.connect("direction-changed", lambda *_: view_native and None)
        return view_native

    @classmethod
    def _internal_new_native_by_type_spec(cls, gtk_widget_type, property_values):
        return gtk_widget_type(**property_values)

    @classmethod
    def _internal_native_property_value(cls, gtk_widget, key):
        return gtk_widget.get_property(key)

    @classmethod
    def _internal_set_native_property_value(cls, gtk_widget, key, value):
        # do not use gtk_object.set_property because there is/was a Gtk memory leak
        getattr(gtk_widget, f"set_{key}")(value)

    @classmethod
    def _internal_add_native_property_changed_handler(cls, gtk_widget, key, handler):
        gtk_widget.connect(f"notify::{key}", lambda *_: handler())

    @classmethod
    def _internal_set_common_property_value(cls, gtk_widget, prop, value):
        match prop:
            case klovve.ui.View.is_visible:
                gtk_widget.set_visible(value)
            case klovve.ui.View.is_enabled:
                gtk_widget.set_sensitive(value)
            case klovve.ui.View.horizontal_layout:
                ViewMaterialization.__apply_positioning(value, "h", gtk_widget)
            case klovve.ui.View.vertical_layout:
                ViewMaterialization.__apply_positioning(value, "v", gtk_widget)
            case klovve.ui.View.margin:
                gtk_widget.set_margin_top(em_to_px(value.top_em))
                gtk_widget.set_margin_end(em_to_px(value.right_em))
                gtk_widget.set_margin_bottom(em_to_px(value.bottom_em))
                gtk_widget.set_margin_start(em_to_px(value.left_em))

    @staticmethod
    def __apply_positioning(layout: "klovve.ui.Layout", gtk_axis_name: str, gtk_widget: Gtk.Widget) -> None:
        getattr(gtk_widget, f"set_{gtk_axis_name}expand")(layout.align == klovve.ui.Align.FILL_EXPANDING)
        getattr(gtk_widget, f"set_{gtk_axis_name}expand_set")(True)

        getattr(gtk_widget, f"set_{gtk_axis_name}align")({klovve.ui.Align.START: Gtk.Align.START,
                                                          klovve.ui.Align.CENTER: Gtk.Align.CENTER,
                                                          klovve.ui.Align.END: Gtk.Align.END,
                                                          klovve.ui.Align.FILL: Gtk.Align.FILL,
                                                          klovve.ui.Align.FILL_EXPANDING: Gtk.Align.FILL
                                                          }[layout.align])

        if gtk_axis_name == "h":
            gtk_widget.set_size_request(ViewMaterialization.__apply_positioning__min_size(layout.min_size_em),
                                        gtk_widget.get_size_request().height)
        else:
            gtk_widget.set_size_request(gtk_widget.get_size_request().width,
                                        ViewMaterialization.__apply_positioning__min_size(layout.min_size_em))

    @staticmethod
    def __apply_positioning__min_size(min_size_em: t.Optional[float]):
        return -1 if (min_size_em is None) else em_to_px(min_size_em)

    class MaterializingViewsInGtkBoxObserver(klovve.ui.utils.MaterializingViewListObserver):

        def __init__(self, view_materialization, gtk_box,
                     get_child_view_func: t.Callable[[t.Any], klovve.ui.View] = None):
            super().__init__(get_child_view_func)
            self.__view_materialization = view_materialization
            self.__gtk_box = gtk_box

        def _add_view_native(self, index, view_native):
            gtk_insert_before_child = self.__gtk_box.get_first_child()
            for _ in range(index):
                gtk_insert_before_child = gtk_insert_before_child.get_next_sibling()

            if gtk_insert_before_child is None:
                self.__gtk_box.append(view_native)
            else:
                view_native.insert_before(self.__gtk_box, gtk_insert_before_child)

        def _pop_view_native(self, index):
            view_native = self.__gtk_box.get_first_child()
            for _ in range(index):
                view_native = view_native.get_next_sibling()
            self.__gtk_box.remove(view_native)
            return view_native

        def _materialize_view(self, view):
            return self.__view_materialization.materialize_child(view)

    class MaterializingViewEffect(klovve.effect.Effect):

        def __init__(self, outer_materialization: "ViewMaterialization", gtk_outer_widget: Gtk.Widget,
                     get_child_view_func: t.Callable[[], klovve.ui.View]):
            super().__init__()
            self.__outer_materialization = outer_materialization
            self.__gtk_outer_widget = gtk_outer_widget
            self.__get_child_view_func = get_child_view_func

        def run(self):
            if child_view := self.__get_child_view_func():
                self.__show_view_native(self.__outer_materialization.materialize_child(child_view).native)
            else:
                self.__show_view_native(None)

        def __show_view_native(self, view_native):
            if isinstance(self.__gtk_outer_widget, Gtk.Box):
                while gtk_old_child := self.__gtk_outer_widget.get_first_child():
                    self.__gtk_outer_widget.remove(gtk_old_child)
                if view_native:
                    self.__gtk_outer_widget.append(view_native)

            else:
                self.__gtk_outer_widget.set_child(view_native)
