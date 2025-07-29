#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import klovve.builtin.drivers.viwid
import klovve.data
import klovve.ui.utils

import viwid


class Form(klovve.builtin.drivers.viwid.ViewMaterialization[klovve.views.Form]):

    def create_native(self):
        viwid_grid = self.new_native(viwid.widgets.widget.Widget, self.piece,
                                     layout=viwid.layout.GridLayout(partitioner=self.__partitioner))

        self.piece._introspect.observe_list_property(klovve.views.Form.sections, self.__ItemsObserver,
                                                     (self, viwid_grid,), owner=self)

        return viwid_grid

    def __partitioner(self, children):
        result = []
        while len(children) > 0:
            result.append(children[:3])
            children = children[3:]
        return result

    class __ItemsObserver(klovve.data.list.List.Observer):

        def __init__(self, form, viwid_grid):
            super().__init__()
            self.__form = form
            self.__viwid_grid = viwid_grid

        def item_added(self, index, item):
            viwid_section_label = viwid.widgets.label.Label()
            viwid_spacing = viwid.widgets.label.Label(text=" ")
            if isinstance(item, (str, klovve.ui.View)):
                if isinstance(item, str):
                    viwid_section_body = viwid.widgets.label.Label(text=item)
                else:
                    viwid_section_body = self.__form.materialize_child(item).native
            else:
                viwid_section_body = viwid.widgets.box.Box()

                klovve.effect.activate_effect(self.__refresh_label_in_ui,
                                              (item, viwid_section_label), owner=viwid_section_label)
                klovve.effect.activate_effect(klovve.builtin.drivers.viwid.ViewMaterialization.MaterializingViewEffect,
                                              (self.__form, viwid_section_body, lambda: item.body),
                                              owner=viwid_section_body)

            self.__viwid_grid._children.insert(index * 3, viwid_section_body)
            self.__viwid_grid._children.insert(index * 3, viwid_spacing)
            self.__viwid_grid._children.insert(index * 3, viwid_section_label)

        def item_removed(self, index, item):
            for _ in range(3):
                self.__viwid_grid._children.pop(index * 3)

        def __refresh_label_in_ui(self, section: klovve.views.Form.Section, viwid_label):
            viwid_label.text = section.label
