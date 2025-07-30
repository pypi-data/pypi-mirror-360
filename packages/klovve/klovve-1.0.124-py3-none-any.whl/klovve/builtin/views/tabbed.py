#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
See :py:class:`Tabbed`.
"""
import klovve


class Tabbed(klovve.ui.Piece):
    """
    A panel of tabs.

    See also :py:class:`Tabbed.Tab`.
    """

    class Tab(klovve.model.Model):
        """
        A tab in a :py:class:`Tabbed`.
        """

        #: The tab title.
        title: str = klovve.ui.property(initial="")

        #: The tab body.
        body: klovve.ui.View|None = klovve.ui.property()

        #: Whether this tab is closable by the user.
        is_closable: bool = klovve.ui.property(initial=False)

        class CloseRequestedEvent(klovve.event.Event):
            """
            Event that occurs when a tab was requested to be closed.
            """

            def __init__(self, tabbed: "Tabbed", tab: "Tabbed.Tab"):
                super().__init__()
                self.__tabbed = tabbed
                self.__tab = tab

            @property
            def tabbed(self) -> "Tabbed":
                """
                The panel of tabs.
                """
                return self.__tabbed

            @property
            def tab(self) -> "Tabbed.Tab":
                """
                The tab.
                """
                return self.__tab

    #: The tabs.
    tabs: list[Tab] = klovve.ui.list_property()

    def request_close(self, tab: Tab) -> None:
        """
        Trigger a close request for a tab, and if event processing was not stopped, close the tab.

        :param tab: The tab.
        """
        closed_requested_event = Tabbed.Tab.CloseRequestedEvent(self, tab)
        self.trigger_event(closed_requested_event)
        if not closed_requested_event.processing_stopped:
            self.tabs.remove(tab)
