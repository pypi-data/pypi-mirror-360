#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
See :py:class:`LogPager`.
"""
import datetime

import klovve


class LogPager(klovve.ui.Piece):
    """
    A log pager.
    """

    class Entry(klovve.model.Model):
        """
        A log entry.
        """
        #: The entry's child entries.
        entries: list["Entry"] = klovve.model.list_property()
        #: The entry's message text.
        message: str = klovve.model.property(initial="")
        #: The entry's began time.
        began_at: datetime.datetime|None = klovve.model.property()
        #: The entry's end time.
        ended_at: datetime.datetime|None = klovve.model.property()
        #: Whether this element is a single-time event (and has no end time).
        only_single_time: bool = klovve.model.property(initial=False)
        #: Whether to show this entry only in verbose mode.
        #: Note that this might hide non-verbose inner entries.
        only_verbose: bool = klovve.model.property(initial=False)

        def _(self):
            return _time_text(self.began_at)
        _began_at_str: str = klovve.model.computed_property(_)

        def _(self):
            if self.only_single_time:
                return ""
            return _time_text(self.ended_at) or (5 * " ･")
        _ended_at_str: str = klovve.model.computed_property(_)

    #: The log entries to show.
    entries: list[Entry] = klovve.ui.list_property()

    #: Whether to show entries as well that are marked to be verbose.
    show_verbose: bool = klovve.ui.property(initial=False)


def _time_text(d: datetime.datetime|None) -> str:
    if not d:
        return ""
    return d.strftime("%X")
