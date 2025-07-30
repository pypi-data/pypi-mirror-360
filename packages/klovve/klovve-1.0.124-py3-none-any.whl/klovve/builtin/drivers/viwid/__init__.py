#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
Terminal based Klovve driver.

This is a fallback driver that only works for applications that are explicitly prepared for that.
"""
import abc
import asyncio
import os
import sys
import typing as t

import klovve.driver
import klovve.variable
import klovve.ui.materialization

sys.path.append(os.path.abspath(f"{__file__}/../internal"))

import viwid.app
import viwid.drivers


if not sys.stdin.isatty() or not sys.stdout.isatty():
    raise RuntimeError("there is no tty")


class Driver(klovve.driver.BaseDriver[viwid.widgets.widget.Widget]):

    __loop = klovve.driver.loop.DefaultDriverLoop(asyncio.new_event_loop())

    @classmethod
    def level(cls):
        return klovve.driver.Driver.LEVEL_TERMINAL

    def __init__(self):
        super().__init__(Driver.__loop)
        self.__viwid_applications = {}

    def __enter__(self):
        super().__enter__()
        viwid.drivers.start(Driver.__loop.event_loop)

    def __exit__(self, exc_type, exc_val, exc_tb):
        viwid.drivers.stop()
        super().__exit__(exc_type, exc_val, exc_tb)

    def __viwid_application_for_klovve_application(self, klovve_application: "klovve.app.BaseApplication") -> viwid.app.Application:
        if (result := self.__viwid_applications.get(klovve_application)) is None:
            result = self.__viwid_applications[klovve_application] = viwid.drivers.current().apps.start_new_application(stop_when_last_screen_layer_closed=False)
            async def _():
                await klovve_application._wait_until_finished()
                self.__viwid_applications.pop(klovve_application)
                viwid.drivers.current().apps.stop_application(result)
            self.loop.enqueue(_())

        return result

    def _show_window(self, materialization):
        viwid_window = materialization.native

        viwid_application = self.__viwid_application_for_klovve_application(materialization.piece.application)
        viwid_application.add_layer_for_window(viwid_window)

        # TODO  https://stackoverflow.com/questions/68716139/redirecting-current-runing-python-process-stdout
        # orig_stdout_fd = os.dup(1)
        # orig_stderr_fd = os.dup(2)
        ####        devnull = open('/tmp/devnull', 'w')
        #        devnull = open('/dev/null', 'w')
        #  os.dup2(devnull.fileno(), 1)
        ####        os.dup2(devnull.fileno(), 2)

    def _close_window(self, materialization):
        if materialization.native.is_materialized:
            materialization.native.screen_layer.application.remove_layer(materialization.native.screen_layer)

    async def _show_dialog(self, dialog, result_future, dialog_body_native, view_anchor, title, is_inline, is_modal,
                           is_closable_by_user):
        if is_inline:
            if is_closable_by_user:
                outer_box = viwid.widgets.box.Box(orientation=viwid.Orientation.HORIZONTAL)
                close_btn = viwid.widgets.button.Button(
                    text="x", decoration=viwid.widgets.button.Decoration.NONE, is_focusable=False,
                    vertical_alignment=viwid.Alignment.START)
                close_btn.listen_event(viwid.widgets.button.Button.TriggeredEvent,
                                       lambda *_: result_future.set_result(None))
                outer_box.children.append(close_btn)
                outer_box.children.append(dialog_body_native)
                dialog_body_native = outer_box

            dialog_body_native = viwid.widgets.box.Box(children=(dialog_body_native,),
                                                       horizontal_alignment=viwid.Alignment.CENTER,
                                                       vertical_alignment=viwid.Alignment.CENTER,
                                                       class_style_name="window")

            application = view_anchor._materialization.native.screen_layer.application
            screen_layer = application.add_layer(
                dialog_body_native, layout=viwid.app.screen.Layout(
                    only_initially=True, anchor_widget=view_anchor._materialization.native),
                is_modal=is_modal, layer_style_name="popup")

            await result_future
            application.remove_layer(screen_layer)

        else:
            dlg = viwid.widgets.window.Window(is_closable_by_user=is_closable_by_user,
                                              title=title or "", body=dialog_body_native)

            def _(event):
                result_future.set_result(None)
            dlg.listen_event(viwid.widgets.window.Window.RequestCloseEvent, _)

            application = view_anchor._materialization.native.screen_layer.application
            application.add_layer_for_window(dlg, is_modal=is_modal,
                                             is_closable_by_user=is_closable_by_user, layer_style_name="popup")
            await result_future
            application.remove_layer(dlg.screen_layer)

    async def _show_special_dialog(self, dialog, result_future, view_anchor, title, is_inline, is_modal,
                                   is_closable_by_user):
        TODO


def em_to_block_count(em: float, viwid_axis_name: str, *, as_int: bool = True) -> float:
    result = em * (1 if viwid_axis_name == "vertical" else 2)
    if as_int:
        result = round(result)
    return result


class ViewMaterialization[TPiece: "klovve.ui.Piece"](Driver._BaseViewMaterialization[TPiece, viwid.widgets.widget.Widget, type[viwid.widgets.widget.Widget]], abc.ABC):

    def new_native[T](self, native_type_spec: type[T], view: t.Optional["klovve.ui.View"] = None, **kwargs) -> T:
        return super().new_native(native_type_spec, view, **kwargs)

    @classmethod
    def _internal_new_native_by_type_spec(cls, viwid_widget_type, property_values):
        return viwid_widget_type(**property_values)

    @classmethod
    def _internal_native_property_value(cls, viwid_widget, key):
        return getattr(viwid_widget, key)

    @classmethod
    def _internal_set_native_property_value(cls, viwid_widget, key, value):
        setattr(viwid_widget, key, value)

    @classmethod
    def _internal_add_native_property_changed_handler(cls, viwid_widget, key, handler):
        viwid_widget.listen_property(key, handler)

    @classmethod
    def _internal_set_common_property_value(cls, viwid_widget, prop, value):
        match prop:
            case klovve.ui.View.is_visible:
                viwid_widget.is_visible = value
            case klovve.ui.View.is_enabled:
                viwid_widget.is_enabled = value
            case klovve.ui.View.horizontal_layout:
                ViewMaterialization.__apply_positioning(value, "horizontal", viwid_widget)
            case klovve.ui.View.vertical_layout:
                ViewMaterialization.__apply_positioning(value, "vertical", viwid_widget)
            case klovve.ui.View.margin:
                viwid_widget.margin = viwid.Margin(em_to_block_count(value.top_em, "vertical"),
                                                   em_to_block_count(value.right_em, "horizontal"),
                                                   em_to_block_count(value.bottom_em, "vertical"),
                                                   em_to_block_count(value.left_em, "horizontal"))

    @staticmethod
    def __apply_positioning(layout: "klovve.ui.Layout", viwid_axis_name: str,
                            viwid_widget: viwid.widgets.widget.Widget) -> None:
        setattr(viwid_widget, f"{viwid_axis_name}_alignment", {
            klovve.ui.Align.START: viwid.Alignment.START,
            klovve.ui.Align.CENTER: viwid.Alignment.CENTER,
            klovve.ui.Align.END: viwid.Alignment.END,
            klovve.ui.Align.FILL: viwid.Alignment.FILL,
            klovve.ui.Align.FILL_EXPANDING: viwid.Alignment.FILL_EXPANDING
        }[layout.align])

        if viwid_axis_name == "horizontal":
            viwid_widget.minimal_size = viwid.Size(ViewMaterialization.__apply_positioning__min_size(layout.min_size_em,
                                                                                                     viwid_axis_name),
                                        viwid_widget.minimal_size.height)
        else:
            viwid_widget.minimal_size = viwid.Size(viwid_widget.minimal_size.width,
                                        ViewMaterialization.__apply_positioning__min_size(layout.min_size_em,
                                                                                          viwid_axis_name))

    @staticmethod
    def __apply_positioning__min_size(min_size_em: t.Optional[float], viwid_axis_name: str) -> int|None:
        return 0 if (min_size_em is None) else em_to_block_count(min_size_em, viwid_axis_name)

    class MaterializingViewsInViwidBoxObserver(klovve.ui.utils.MaterializingViewListObserver):

        def __init__(self, view_materialization, viwid_box,
                     get_child_view_func: t.Callable[[t.Any], klovve.ui.View] = None):
            super().__init__(get_child_view_func)
            self.__view_materialization = view_materialization
            self.__viwid_box = viwid_box

        def _add_view_native(self, index, view_native):
            self.__viwid_box.children.insert(index, view_native)

        def _pop_view_native(self, index):
            return self.__viwid_box.children.pop(index)

        def _materialize_view(self, view):
            return self.__view_materialization.materialize_child(view)

    class MaterializingViewEffect(klovve.effect.Effect):

        def __init__(self, outer_materialization: "ViewMaterialization",
                     viwid_outer_widget: viwid.widgets.widget.Widget,
                     get_child_view_func: t.Callable[[], klovve.ui.View]):
            super().__init__()
            self.__outer_materialization = outer_materialization
            self.__viwid_outer_widget = viwid_outer_widget
            self.__get_child_view_func = get_child_view_func

        def run(self):
            if child_view := self.__get_child_view_func():
                self.__show_view_native(self.__outer_materialization.materialize_child(child_view).native)
            else:
                self.__show_view_native(None)

        def __show_view_native(self, view_native):
            if isinstance(self.__viwid_outer_widget, viwid.widgets.box.Box):
                self.__viwid_outer_widget.children = (view_native,) if view_native else ()
            elif isinstance(self.__viwid_outer_widget, (viwid.widgets.window.Window, viwid.widgets.tabbed.Tabbed.Tab)):
                self.__viwid_outer_widget.body = view_native
            else:
                self.__viwid_outer_widget.item = view_native
