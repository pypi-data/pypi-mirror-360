#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import viwid


if __name__ == "__main__":
    with viwid.context() as viwid_context:
        def start_app():
            app = viwid_context.apps.start_new_application()
            app.add_layer_for_window(
                viwid.widgets.window.Window(
                    is_resizable_by_user=True,
                    is_movable_by_user=True,
                    body=viwid.widgets.box.Box(
                        children=[
                            viwid.widgets.label.Label(text="Welcome!"),
                            viwid.widgets.entry.Entry(),
                            start_new_app_button := viwid.widgets.button.Button(text="Start new app"),
                            close_button := viwid.widgets.button.Button(text="Close")],
                        orientation=viwid.Orientation.VERTICAL)))

            def _(event):
                start_app()
            start_new_app_button.listen_event(viwid.widgets.button.Button.TriggeredEvent, _)

            def _(event):
                viwid_context.apps.stop_application(app)
            close_button.listen_event(viwid.widgets.button.Button.TriggeredEvent, _)

        start_app()
