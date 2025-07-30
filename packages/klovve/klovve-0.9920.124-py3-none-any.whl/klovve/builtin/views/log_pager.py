#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import datetime

import klovve


class LogPager(klovve.ui.Piece):

    class Entry(klovve.model.Model):
        entries: list["Entry"] = klovve.model.list_property()
        message: str = klovve.model.property(initial="")
        began_at: datetime.datetime|None = klovve.model.property()
        ended_at: datetime.datetime|None = klovve.model.property()
        only_single_time: bool = klovve.model.property(initial=False)
        only_verbose: bool = klovve.model.property(initial=False)

        def _(self):
            return _time_text(self.began_at)
        _began_at_str: str = klovve.model.computed_property(_)

        def _(self):
            if self.only_single_time:
                return ""
            return _time_text(self.ended_at) or (5 * " ･")
        _ended_at_str: str = klovve.model.computed_property(_)

    entries: list[Entry] = klovve.ui.list_property()

    show_verbose: bool = klovve.ui.property(initial=False)


def _time_text(d: datetime.datetime|None) -> str:
    if not d:
        return ""
    return d.strftime("%X")
