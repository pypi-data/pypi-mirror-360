#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import functools

import viwid


if __name__ == "__main__":
    with viwid.context() as viwid_context:
        app = viwid_context.apps.start_new_application()
        app.add_layer_for_window(
            viwid.widgets.window.Window(
                body=viwid.widgets.box.Box(
                    children=[
                        button_dec := viwid.widgets.button.Button(text="-", minimal_size=viwid.Size(5, 3)),
                        label := viwid.widgets.label.Label(text="42"),
                        button_inc := viwid.widgets.button.Button(text="+", minimal_size=viwid.Size(5, 3))])))

        def _(delta):
            label.text = str(int(label.text) + delta)
        button_inc.listen_event(viwid.widgets.button.Button.TriggeredEvent, functools.partial(_, 1))
        button_dec.listen_event(viwid.widgets.button.Button.TriggeredEvent, functools.partial(_, -1))
