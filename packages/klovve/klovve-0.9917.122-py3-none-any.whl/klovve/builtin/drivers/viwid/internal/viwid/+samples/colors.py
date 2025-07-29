#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import viwid


if __name__ == "__main__":
    def label_row(r, g):
        return [viwid.widgets.label.Label(text="  ", background=viwid.PlainColor(__color_value(r),
                                                                                 __color_value(g),
                                                                                 __color_value(b)))
                for b in range(6)]
    def label_box(r):
        return [viwid.widgets.box.Box(orientation=viwid.Orientation.VERTICAL,
                                      children=label_row(r, g))
                for g in range(6)]
    def label_boxes():
        return [viwid.widgets.box.Box(orientation=viwid.Orientation.HORIZONTAL,
                                      children=label_box(r))
                for r in range(6)]

    def __color_value(i) -> float:
        return ((95 + (i - 1) * 40) / 255) if i else 0

    with viwid.context() as viwid_context:
        app = viwid_context.apps.start_new_application()
        app.add_layer_for_window(
            window := viwid.widgets.window.Window(
                body=viwid.widgets.box.Box(
                    children=label_boxes(),
                    orientation=viwid.Orientation.HORIZONTAL)))

        def _(event):
            if event.touched_widget and (background := event.touched_widget.background):
                window.title = background.as_html()[:-2]
        window.listen_event(viwid.event.mouse.ClickEvent, _)
