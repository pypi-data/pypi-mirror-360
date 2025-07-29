#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import viwid


if __name__ == "__main__":
    with viwid.context() as viwid_context:
        app = viwid_context.apps.start_new_application()
        app.add_layer_for_window(
            viwid.widgets.window.Window(
                body=viwid.widgets.box.Box(
                    children=[
                        viwid.widgets.label.Label(text="Welcome! Enter something below."),
                        entry := viwid.widgets.entry.Entry(),
                        label := viwid.widgets.label.Label()],
                    orientation=viwid.Orientation.VERTICAL)))

        def _():
            label.text = "Your text: " + entry.text[:10] + ("..." if len(entry.text) > 10 else "")
        entry.listen_property("text", _)
        _()
