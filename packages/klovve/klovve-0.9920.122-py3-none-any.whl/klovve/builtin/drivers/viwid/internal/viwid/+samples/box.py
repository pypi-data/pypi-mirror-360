#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import viwid


if __name__ == "__main__":
    with viwid.context() as viwid_context:
        app = viwid_context.apps.start_new_application()
        button_args = dict(horizontal_alignment=viwid.Alignment.FILL_EXPANDING,
                           vertical_alignment=viwid.Alignment.FILL_EXPANDING)
        app.add_layer_for_window(
            window := viwid.widgets.window.Window(
                body=viwid.widgets.box.Box(
                    children=[
                        viwid.widgets.box.Box(
                            children=[
                                viwid.widgets.box.Box(
                                    children=[
                                        viwid.widgets.button.Button(text="a", **button_args),
                                        viwid.widgets.button.Button(text="b", **button_args),
                                        viwid.widgets.button.Button(text="c", **button_args),
                                        viwid.widgets.button.Button(text="d", **button_args),
                                        viwid.widgets.button.Button(text="e", **button_args)],
                                    orientation=viwid.Orientation.HORIZONTAL),
                                viwid.widgets.box.Box(
                                    children=[
                                        viwid.widgets.button.Button(text="f", **button_args),
                                        viwid.widgets.button.Button(text="g", **button_args)],
                                    orientation=viwid.Orientation.HORIZONTAL),
                                viwid.widgets.box.Box(
                                    children=[
                                        viwid.widgets.button.Button(text="h", **button_args)],
                                    orientation=viwid.Orientation.HORIZONTAL)],
                            orientation=viwid.Orientation.VERTICAL),
                        viwid.widgets.box.Box(
                            children=[
                                viwid.widgets.box.Box(
                                    children=[
                                        viwid.widgets.button.Button(text="i", **button_args),
                                        viwid.widgets.button.Button(text="j", **button_args)],
                                    orientation=viwid.Orientation.HORIZONTAL),
                                viwid.widgets.box.Box(
                                    children=[
                                        viwid.widgets.button.Button(text="k", **button_args)],
                                    orientation=viwid.Orientation.HORIZONTAL)],
                            orientation=viwid.Orientation.VERTICAL),
                        viwid.widgets.button.Button(text="l", **button_args)],
                    orientation=viwid.Orientation.HORIZONTAL)))

        def _(event):
            window.title = event.button.text.upper()
        window.listen_event(viwid.widgets.button.Button.TriggeredEvent, _)
