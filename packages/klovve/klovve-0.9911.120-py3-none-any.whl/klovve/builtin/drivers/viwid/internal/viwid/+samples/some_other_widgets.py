#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import viwid


if __name__ == "__main__":
    with viwid.context() as viwid_context:
        app = viwid_context.apps.start_new_application()
        app.add_layer_for_window(
            viwid.widgets.window.Window(
                title="Some other widgets",
                body=viwid.widgets.box.Box(
                    children=[
                        progress_bar := viwid.widgets.progress_bar.ProgressBar(),
                        viwid.widgets.busy_animation.BusyAnimation(),
                        slider := viwid.widgets.slider.Slider(value_range=viwid.NumericValueRange(
                            min_value=0, max_value=1, step_size=0.025))],
                    orientation=viwid.Orientation.VERTICAL)))

        def _():
            progress_bar.value = slider.value
        slider.listen_property("value", _)
