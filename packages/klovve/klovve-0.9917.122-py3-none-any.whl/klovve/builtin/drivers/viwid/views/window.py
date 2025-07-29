#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import klovve.builtin.drivers.viwid

import viwid


class Window(klovve.builtin.drivers.viwid.ViewMaterialization[klovve.views.Window]):

    def create_native(self):
        viwid_window = self.new_native(viwid.widgets.window.Window, self.piece,
                                       title=self.piece.bind(two_way=False).title)

        klovve.effect.activate_effect(klovve.builtin.drivers.viwid.ViewMaterialization.MaterializingViewEffect,
                                      (self, viwid_window, lambda: self.piece.body), owner=self)
        klovve.effect.activate_effect(self.__remove_native_window_when_closed, (viwid_window,), owner=self)
        viwid_window.listen_event(viwid.widgets.window.Window.RequestCloseEvent, self.__handle_request_close)

        return viwid_window

    def __handle_request_close(self, event):
        self.piece.request_close()
        event.stop_handling()

    def __remove_native_window_when_closed(self, viwid_window):
        if self.piece._is_closed:
            viwid_window.screen_layer.application.remove_layer(viwid_window.screen_layer)
