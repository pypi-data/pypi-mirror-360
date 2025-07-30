#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import functools
from faulthandler import is_enabled

import viwid


if __name__ == "__main__":
    with viwid.context() as viwid_context:
        app = viwid_context.apps.start_new_application()
        app.add_layer_for_window(
            viwid.widgets.window.Window(
                body=viwid.widgets.tabbed.Tabbed(
                    tabs=[
                        tab_1 := viwid.widgets.tabbed.Tabbed.Tab(
                            body=viwid.widgets.box.Box(
                                orientation=viwid.Orientation.VERTICAL,
                                children=[
                                    viwid.widgets.label.Label(text="This is the foo tab."),
                                    tab_1_entry := viwid.widgets.entry.Entry()])),
                        tab_2 := viwid.widgets.tabbed.Tabbed.Tab(
                            is_closable_by_user=True,
                            body=viwid.widgets.box.Box(
                                orientation=viwid.Orientation.VERTICAL,
                                children=[
                                    viwid.widgets.label.Label(text="This is the bar tab."),
                                    tab_2_entry := viwid.widgets.entry.Entry()])),
                        tab_3 := viwid.widgets.tabbed.Tabbed.Tab(
                            body=viwid.widgets.box.Box(
                                orientation=viwid.Orientation.VERTICAL,
                                children=[
                                    viwid.widgets.label.Label(text="This is the baz tab."),
                                    tab_3_entry := viwid.widgets.entry.Entry()]))])))

        def _(tab, entry, default_title, *_):
            tab.title = entry.text or default_title
        for tab, entry, default_title in ((tab_1, tab_1_entry, "The Foo"),
                                          (tab_2, tab_2_entry, "The Bar"),
                                          (tab_3, tab_3_entry, "The Baz")):
            entry.listen_property("text", functools.partial(_, tab, entry, default_title))
            _(tab, entry, default_title)
