#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import viwid


if __name__ == "__main__":
    def new_window(title, app, is_movable_by_user, is_resizable_by_user, is_closable_by_user, is_modal):
        screen_layer = app.add_layer_for_window(
            viwid.widgets.window.Window(
                title=title,
                is_movable_by_user=is_movable_by_user,
                is_resizable_by_user=is_resizable_by_user,
                is_closable_by_user=is_closable_by_user,
                body=viwid.widgets.box.Box(
                    children=[
                        viwid.widgets.box.Box(
                            children=[
                                viwid.widgets.label.Label(text="Title:"),
                                title_entry := viwid.widgets.entry.Entry()],
                            orientation=viwid.Orientation.HORIZONTAL),
                        moveable_check := viwid.widgets.check_button.CheckButton(text="moveable", is_checked=True),
                        resizable_check := viwid.widgets.check_button.CheckButton(text="resizable", is_checked=True),
                        modal_check := viwid.widgets.check_button.CheckButton(text="modal", is_checked=True),
                        closeable_check := viwid.widgets.check_button.CheckButton(text="closeable", is_checked=True),
                        create_window_button := viwid.widgets.button.Button(text="Create window",
                                                                            margin=viwid.Margin(top=1)),
                        remove_this_window_button := viwid.widgets.button.Button(text="Remove this window")],
                    orientation=viwid.Orientation.VERTICAL,
                    horizontal_alignment=viwid.Alignment.CENTER,
                    vertical_alignment=viwid.Alignment.CENTER,
                    margin=viwid.Margin(all=1))),
            is_modal=is_modal)

        def _():
            new_window(title_entry.text, app, moveable_check.is_checked, resizable_check.is_checked, closeable_check.is_checked, modal_check.is_checked)
        create_window_button.listen_event(viwid.widgets.button.Button.TriggeredEvent, _)

        def _():
            screen_layer.application.remove_layer(screen_layer)
        remove_this_window_button.listen_event(viwid.widgets.button.Button.TriggeredEvent, _)

    with viwid.context() as viwid_context:
        app = viwid_context.apps.start_new_application()
        new_window("My Window 😁", app, True, True, True, True)
