#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import klovve.builtin.drivers.gtk
from klovve.builtin.drivers.gtk import Gtk


class HeadBar(klovve.builtin.drivers.gtk.ViewMaterialization[klovve.views.HeadBar]):

    def create_native(self):
        gtk_outer_box = self.new_native(
            Gtk.Box, self.piece, css_classes=self.bind._css_classes, orientation=Gtk.Orientation.VERTICAL)
        gtk_outer_box.append(gtk_inner_box := self.new_native(Gtk.Box))
        gtk_inner_box.append(gtk_inner_left_box := self.new_native(Gtk.Box, halign=Gtk.Align.START))
        gtk_inner_box.append(gtk_inner_center_box := self.new_native(Gtk.Box, halign=Gtk.Align.CENTER, hexpand=True))
        gtk_inner_center_box.append(self.new_native(Gtk.Spinner, visible=self.bind._is_spinner_visible,  # TODO is .bind to "__..." private variables broken?
                                                    spinning=self.bind._is_spinner_visible))
        gtk_inner_center_box.append(gtk_state_image := self.new_native(Gtk.Image))
        gtk_inner_center_box.append(self.new_native(
            Gtk.Label, css_classes=["klv_head_bar_title"], label=self.piece.bind.title))
        gtk_inner_box.append(gtk_inner_right_box := self.new_native(Gtk.Box, halign=Gtk.Align.END))
        gtk_outer_box.append(self.new_native(Gtk.ProgressBar, fraction=self.bind._progress_float,
                                             opacity=self.bind._progress_bar_opacity, margin_top=3))

        klovve.effect.activate_effect(self.__refresh_state_icon_name_in_ui, (gtk_state_image,), owner=self)
        self.piece._introspect.observe_list_property(
            klovve.views.HeadBar.primary_header_items,
            self.MaterializingViewsInGtkBoxObserver, (self, gtk_inner_left_box), owner=self)
        self.piece._introspect.observe_list_property(
            klovve.views.HeadBar.secondary_header_items,
            self.MaterializingViewsInGtkBoxObserver, (self, gtk_inner_right_box), owner=self)

        return gtk_outer_box

    def _(self):
        return self.piece.style == klovve.views.HeadBar.Style.BUSY
    _is_spinner_visible: bool = klovve.ui.computed_property(_)

    def _(self):
        return self.piece.progress or 0
    _progress_float: float = klovve.ui.computed_property(_)

    def _(self):
        return 0 if self.piece.progress is None else 1
    _progress_bar_opacity: float = klovve.ui.computed_property(_)

    def _(self):
        result = ["klv_head_bar"]
        match self.piece.style:
            case klovve.views.HeadBar.Style.SUCCESSFUL:
                result.append("klv_head_bar__successful")
            case klovve.views.HeadBar.Style.SUCCESSFUL_WITH_WARNING:
                result.append("klv_head_bar__successful_with_warning")
            case klovve.views.HeadBar.Style.FAILED:
                result.append("klv_head_bar__failed")
        return tuple(result)
    _css_classes = klovve.ui.computed_property(_)

    def __refresh_state_icon_name_in_ui(self, gtk_state_image):
        icon_name = {klovve.views.HeadBar.Style.FAILED: "dialog-error",
                     klovve.views.HeadBar.Style.SUCCESSFUL: "dialog-ok",
                     klovve.views.HeadBar.Style.SUCCESSFUL_WITH_WARNING: "dialog-warning"}.get(self.piece.style)
        gtk_state_image.set_from_icon_name(icon_name)
        gtk_state_image.set_visible(bool(icon_name))
