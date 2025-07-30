#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import klovve


class Tabbed(klovve.ui.Piece):

    class Tab(klovve.model.Model):

        title: str = klovve.ui.property(initial="")

        body: klovve.ui.View|None = klovve.ui.property()

        is_closable: bool = klovve.ui.property(initial=False)

        class CloseRequestedEvent(klovve.event.Event):

            def __init__(self, tabbed: "Tabbed", tab: "Tabbed.Tab"):
                super().__init__()
                self.__tabbed = tabbed
                self.__tab = tab

            @property
            def tabbed(self) -> "Tabbed":
                return self.__tabbed

            @property
            def tab(self) -> "Tabbed.Tab":
                return self.__tab

    tabs: list[Tab] = klovve.ui.list_property()

    def request_close(self, tab: Tab) -> None:
        closed_requested_event = Tabbed.Tab.CloseRequestedEvent(self, tab)
        self.trigger_event(closed_requested_event)
        if not closed_requested_event.processing_stopped:
            self.tabs.remove(tab)
