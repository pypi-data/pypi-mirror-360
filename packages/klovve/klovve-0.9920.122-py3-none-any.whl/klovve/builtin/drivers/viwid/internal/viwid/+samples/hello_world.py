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
                        viwid.widgets.label.Label(text="😀", margin=viwid.Margin(right=1)),
                        viwid.widgets.label.Label(text="Hello, World!"),
                        viwid.widgets.label.Label(text="😀", margin=viwid.Margin(left=1))])))
