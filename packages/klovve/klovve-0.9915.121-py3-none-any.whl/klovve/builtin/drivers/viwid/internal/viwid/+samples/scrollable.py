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
                        scrollable := viwid.widgets.scrollable.Scrollable(
                            body=viwid.widgets.box.Box(
                                children=[
                                    viwid.widgets.label.Label(text="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
                                                              horizontal_alignment=viwid.Alignment.START),
                                    viwid.widgets.label.Label(text="Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
                                                              horizontal_alignment=viwid.Alignment.START),
                                    viwid.widgets.label.Label(text="Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.",
                                                              horizontal_alignment=viwid.Alignment.START),
                                    viwid.widgets.label.Label(text="Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
                                                              horizontal_alignment=viwid.Alignment.START)],
                                orientation=viwid.Orientation.VERTICAL),
                            minimal_size=viwid.Size(15, 4)),
                        horizontally_scrollable_check := viwid.widgets.check_button.CheckButton(
                            text="hor. scroll."),
                        vertically_scrollable_check := viwid.widgets.check_button.CheckButton(
                            text="vert. scroll.", is_checked=True)],
                    orientation=viwid.Orientation.VERTICAL),
                is_movable_by_user = True,
                is_resizable_by_user = True))

        def _():
            scrollable.is_horizontally_scrollable = horizontally_scrollable_check.is_checked
        horizontally_scrollable_check.listen_property("is_checked", _)
        _()

        def _():
            scrollable.is_vertically_scrollable = vertically_scrollable_check.is_checked
        vertically_scrollable_check.listen_property("is_checked", _)
        _()
