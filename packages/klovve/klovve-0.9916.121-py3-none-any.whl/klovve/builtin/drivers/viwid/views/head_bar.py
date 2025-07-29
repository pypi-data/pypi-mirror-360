#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import klovve.builtin.drivers.viwid

import viwid


class HeadBar(klovve.builtin.drivers.viwid.ViewMaterialization[klovve.views.HeadBar]):

    def create_native(self):
        viwid_outer_box = self.new_native(
            viwid.widgets.box.Box, self.piece, background=self.bind._background_color,
            orientation=viwid.Orientation.VERTICAL)
        viwid_outer_box.children.append(viwid_inner_box := self.new_native(viwid.widgets.box.Box))
        viwid_inner_box.children.append(viwid_inner_left_box := self.new_native(
            viwid.widgets.box.Box, horizontal_alignment=viwid.Alignment.START))
        viwid_inner_box.children.append(viwid_inner_center_outer_box := self.new_native(viwid.widgets.box.Box))
        viwid_inner_center_outer_box.children.append(viwid_inner_center_box := self.new_native(
            viwid.widgets.box.Box, horizontal_alignment=viwid.Alignment.CENTER))
        viwid_inner_center_box.children.append(self.new_native(
            viwid.widgets.busy_animation.BusyAnimation, is_visible=self.bind._is_spinner_visible))
        viwid_inner_center_box.children.append(viwid_state_image := self.new_native(viwid.widgets.label.Label))
        viwid_inner_center_box.children.append(self.new_native(viwid.widgets.label.Label, text=self.piece.bind.title))
        viwid_inner_box.children.append(viwid_inner_right_box := self.new_native(
            viwid.widgets.box.Box, horizontal_alignment=viwid.Alignment.END))
        viwid_outer_box.children.append(self.new_native(
            viwid.widgets.progress_bar.ProgressBar, value=self.bind._progress_float,
            is_visible=self.bind._is_progress_bar_visible))

        klovve.effect.activate_effect(self.__refresh_state_icon_name_in_ui, (viwid_state_image,), owner=self)
        self.piece._introspect.observe_list_property(
            klovve.views.HeadBar.primary_header_items,
            self.MaterializingViewsInViwidBoxObserver, (self, viwid_inner_left_box), owner=self)
        self.piece._introspect.observe_list_property(
            klovve.views.HeadBar.secondary_header_items,
            self.MaterializingViewsInViwidBoxObserver, (self, viwid_inner_right_box), owner=self)

        return viwid_outer_box

    def _(self):
        return self.piece.style == klovve.views.HeadBar.Style.BUSY
    _is_spinner_visible: bool = klovve.ui.computed_property(_)

    def _(self):
        return self.piece.progress or 0
    _progress_float: float = klovve.ui.computed_property(_)

    def _(self):
        return self.piece.progress is not None
    _is_progress_bar_visible: float = klovve.ui.computed_property(_)

    def _(self):
        match self.piece.style:
            case klovve.views.HeadBar.Style.SUCCESSFUL:
                return "#0f0"
            case klovve.views.HeadBar.Style.SUCCESSFUL_WITH_WARNING:
                return "#fb0"
            case klovve.views.HeadBar.Style.FAILED:
                return "#f00"
    _background_color = klovve.ui.computed_property(_)

    def __refresh_state_icon_name_in_ui(self, viwid_state_image):
        icon_text = {klovve.views.HeadBar.Style.FAILED: "×",
                     klovve.views.HeadBar.Style.SUCCESSFUL: "✓",
                     klovve.views.HeadBar.Style.SUCCESSFUL_WITH_WARNING: "❗"}.get(self.piece.style, "")
        viwid_state_image.text = icon_text
        viwid_state_image.is_visible = bool(icon_text)
