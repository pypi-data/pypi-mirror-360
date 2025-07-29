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
                        label := viwid.widgets.label.Label(text="42"),
                        change_button := viwid.widgets.button.Button(text="Change value")],
                    margin=viwid.Margin(all=1),
                    orientation=viwid.Orientation.VERTICAL)))

        def _(event):
            change_value()
        change_button.listen_event(viwid.widgets.button.Button.TriggeredEvent, _)

        def change_value():
            app.add_layer_for_window(
                dialog := viwid.widgets.window.Window(
                    is_closable_by_user=False,
                    is_movable_by_user=False,
                    is_resizable_by_user=False,
                    body=viwid.widgets.box.Box(
                        children=[
                            viwid.widgets.label.Label(text="Please enter the new value."),
                            entry := viwid.widgets.entry.Entry(text=label.text),
                            button_ok := viwid.widgets.button.Button(text="OK")],
                        margin=viwid.Margin(all=1),
                        orientation=viwid.Orientation.VERTICAL)), layer_style_name="popup")

            def _(event):
                label.text = entry.text
                dialog.request_close()
            button_ok.listen_event(viwid.widgets.button.Button.TriggeredEvent, _)
