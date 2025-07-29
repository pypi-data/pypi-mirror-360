#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import klovve.builtin.drivers.viwid

import viwid


class BusyAnimation(klovve.builtin.drivers.viwid.ViewMaterialization[klovve.views.BusyAnimation]):

    def create_native(self):
        viwid_box = self.new_native(viwid.widgets.box.Box, self.piece, orientation=self.bind._viwid_orientation)
        viwid_box.children.append(self.new_native(viwid.widgets.busy_animation.BusyAnimation))
        viwid_box.children.append(self.new_native(viwid.widgets.label.Label,
                                                  text=self.piece.bind(two_way=False)._text_str,
                                                  is_visible=self.piece.bind(two_way=False)._has_text))

        return viwid_box

    def _(self):
        return {
            klovve.views.BusyAnimation.Orientation.HORIZONTAL: viwid.Orientation.HORIZONTAL,
            klovve.views.BusyAnimation.Orientation.VERTICAL: viwid.Orientation.VERTICAL,
        }[self.piece.orientation]
    _viwid_orientation: viwid.Orientation = klovve.ui.computed_property(_)
