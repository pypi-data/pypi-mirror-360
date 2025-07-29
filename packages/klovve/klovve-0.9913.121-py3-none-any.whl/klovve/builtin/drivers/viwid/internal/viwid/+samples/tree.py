#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import viwid


if __name__ == "__main__":
    with viwid.context() as viwid_context:
        app = viwid_context.apps.start_new_application()
        app.add_layer_for_window(
            window := viwid.widgets.window.Window(
                body=viwid.widgets.scrollable.Scrollable(
                    body=(places_list := viwid.widgets.tree.Tree(
                        items=[
                            viwid.widgets.list.List.Row(
                                text="Europe",
                                items=[
                                    viwid.widgets.list.List.Row(
                                        text="Netherlands",
                                        items=[
                                            viwid.widgets.list.List.Row(text="Kerkrade"),
                                            viwid.widgets.list.List.Row(text="Haarlemmermeer")]),
                                    viwid.widgets.list.List.Row(
                                        text="Italy",
                                        items=[
                                            viwid.widgets.list.List.Row(text="Bologna"),
                                            viwid.widgets.list.List.Row(text="Imola"),
                                            viwid.widgets.list.List.Row(text="Venice")])]),
                            viwid.widgets.list.List.Row(
                                text="Asia",
                                items=[
                                    viwid.widgets.list.List.Row(
                                        text="Japan",
                                        items=[
                                            viwid.widgets.list.List.Row(text="Tokyo")]),
                                    viwid.widgets.list.List.Row(
                                        text="China",
                                        items=[
                                            viwid.widgets.list.List.Row(text="Xi'an"),
                                            viwid.widgets.list.List.Row(text="Shanghai")])]),
                            viwid.widgets.list.List.Row(
                                text="America",
                                items=[
                                    viwid.widgets.list.List.Row(
                                        text="Mexico",
                                        items=[
                                            viwid.widgets.list.List.Row(text="Puebla"),
                                            viwid.widgets.list.List.Row(text="Tijuana")]),
                                    viwid.widgets.list.List.Row(
                                        text="Canada",
                                        items=[
                                            viwid.widgets.list.List.Row(text="Quebec"),
                                            viwid.widgets.list.List.Row(text="Ottawa"),
                                            viwid.widgets.list.List.Row(text="Toronto")])])])),
                    minimal_size=viwid.Size(20, 5))))

        def _(event: viwid.widgets.list.List.SelectionChangedEvent):
            window.title = ", ".join([places_list.item_for_index(index).text
                                      for index in places_list.selected_item_indexes])
        places_list.listen_event(viwid.widgets.list.List.SelectionChangedEvent, _)
