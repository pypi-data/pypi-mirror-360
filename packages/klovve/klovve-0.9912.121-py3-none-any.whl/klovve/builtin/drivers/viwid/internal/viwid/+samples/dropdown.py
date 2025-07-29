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
                        dropdown_1 := viwid.widgets.dropdown.DropDown(items=["Ursula", "Ulrich"]),
                        label := viwid.widgets.label.Label(text="Welcome!", minimal_size=viwid.Size(15, 0)),
                        dropdown_2 := viwid.widgets.dropdown.DropDown(items=["Wolfgang", "Horst", "Franziska"])],
                    orientation=viwid.Orientation.HORIZONTAL)))

        def _():
            label.text = dropdown_1.selected_item or ""
        dropdown_1.listen_property("selected_item", _)

        def _():
            label.text = dropdown_2.selected_item or ""
        dropdown_2.listen_property("selected_item", _)
