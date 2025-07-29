#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import viwid


if __name__ == "__main__":
    with viwid.context() as viwid_context:
        app = viwid_context.apps.start_new_application()
        app.add_layer_for_window(
            window := viwid.widgets.window.Window(
                body=viwid.widgets.box.Box(
                    children=[
                        viwid.widgets.scrollable.Scrollable(
                            body=(word_list := viwid.widgets.list.List(
                                items=[
                                    viwid.widgets.list.List.Row(text="Äädäppelschlot"),
                                    viwid.widgets.list.List.Row(text="Fasteleer"),
                                    viwid.widgets.list.List.Row(text="Jedöns"),
                                    viwid.widgets.list.List.Row(text="Kappes"),
                                    viwid.widgets.list.List.Row(text="Pittermännche"),
                                    viwid.widgets.list.List.Row(text="Pooz"),
                                    viwid.widgets.list.List.Row(text="Schwaadlappe")])),
                            minimal_size=viwid.Size(20, 5)),
                        allow_multi_select_button := viwid.widgets.check_button.CheckButton(text="multi-select")],
                    orientation=viwid.Orientation.VERTICAL)))

        def _(event: viwid.widgets.list.List.SelectionChangedEvent):
            window.title = ", ".join([word_list.items[index].text for index in word_list.selected_item_indexes])
        word_list.listen_event(viwid.widgets.list.List.SelectionChangedEvent, _)

        def _():
            word_list.allows_multi_select = allow_multi_select_button.is_checked
        allow_multi_select_button.listen_property("is_checked", _)
        _()
