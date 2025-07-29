#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import viwid


if __name__ == "__main__":
    with viwid.context() as viwid_context:
        app = viwid_context.apps.start_new_application()
        app.add_layer_for_window(
            viwid.widgets.window.Window(
                title="Split",
                body=viwid.widgets.split.Split(
                    item_1=viwid.widgets.label.Label(text="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed"
                                                          " do eiusmod tempor incididunt ut labore et dolore magna"
                                                          " aliqua."),
                    item_2=viwid.widgets.label.Label(text="Ut enim ad minim veniam, quis nostrud exercitation ullamco"
                                                          " laboris nisi ut aliquip ex ea commodo consequat."))))
