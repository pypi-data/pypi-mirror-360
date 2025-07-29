#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import viwid


if __name__ == "__main__":
    with viwid.context() as viwid_context:
        app = viwid_context.apps.start_new_application()
        my_radio_group = viwid.widgets.radio_button.RadioButton.Group()
        app.add_layer_for_window(
            viwid.widgets.window.Window(
                title="Calculator Pro",
                body=viwid.widgets.box.Box(
                    children=[
                        viwid.widgets.label.Label(text="  1"),
                        times_2_button := viwid.widgets.check_button.CheckButton(text="* 2"),
                        times_3_button := viwid.widgets.check_button.CheckButton(text="* 3"),
                        times_4_button := viwid.widgets.radio_button.RadioButton(text="* 4", group=my_radio_group),
                        times_5_button := viwid.widgets.radio_button.RadioButton(text="* 5", group=my_radio_group),
                        result_label := viwid.widgets.label.Label(text=""),
                    ],
                    orientation=viwid.Orientation.VERTICAL)))

        def _():
            term = "1"
            for button in (times_2_button, times_3_button, times_4_button, times_5_button):
                if button.is_checked:
                    term += button.text
            result_label.text = f" = {eval(term)}"
        for button in (times_2_button, times_3_button, times_4_button, times_5_button):
            button.listen_property("is_checked", _)
        _()
