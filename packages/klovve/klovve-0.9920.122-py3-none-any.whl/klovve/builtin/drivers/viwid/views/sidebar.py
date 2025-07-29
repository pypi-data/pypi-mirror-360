#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import klovve.builtin.drivers.viwid
import klovve.ui.utils

import viwid


class Sidebar(klovve.builtin.drivers.viwid.ViewMaterialization[klovve.views.Sidebar]):

    def create_native(self):
        viwid_sidebar_box = self.new_native(viwid.widgets.box.Box, self.piece, orientation=viwid.Orientation.VERTICAL,
                                          background="#7bf2")
        viwid_sidebar_box.children.append(viwid_collapse_expand_button := self.new_native(
            viwid.widgets.button.Button, horizontal_alignment=viwid.Alignment.END,
            is_focusable=False, decoration=viwid.widgets.button.Decoration.NONE))
        viwid_sidebar_box.children.append(viwid_sidebar_body_box := self.new_native(viwid.widgets.box.Box))

        klovve.effect.activate_effect(self.__collapse_effect,
                                      (viwid_sidebar_body_box, viwid_collapse_expand_button), owner=self)
        klovve.effect.activate_effect(self.__width_effect, (viwid_sidebar_body_box,), owner=self)
        klovve.effect.activate_effect(klovve.builtin.drivers.viwid.ViewMaterialization.MaterializingViewEffect,
                                      (self, viwid_sidebar_body_box, lambda: self.piece.body), owner=self)
        viwid_collapse_expand_button.listen_event(viwid.widgets.button.Button.TriggeredEvent,
                                                  lambda *_: self.piece._toggle_collapsed())

        return viwid_sidebar_box

    def __collapse_effect(self, viwid_sidebar_body_box, viwid_collapse_expand_button):
        viwid_sidebar_body_box.is_visible = not self.piece.is_collapsed
        viwid_collapse_expand_button.text = ">" if self.piece.is_collapsed else "<"

    def __width_effect(self, viwid_sidebar_body_box):
        viwid_sidebar_body_box.minimal_size = viwid.Size(
            klovve.builtin.drivers.viwid.em_to_block_count(self.piece.width_em, "horizontal"), 0)
