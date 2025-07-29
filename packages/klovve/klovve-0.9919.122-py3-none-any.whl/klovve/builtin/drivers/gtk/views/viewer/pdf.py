#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import pathlib

import klovve.builtin.drivers.gtk
from klovve.builtin.drivers.gtk import Gtk


class Pdf(klovve.builtin.drivers.gtk.ViewMaterialization[klovve.views.viewer.Pdf]):

    def create_native(self):
        gtk_overlay = self.new_native(Gtk.Overlay, self.piece)
        gtk_overlay.set_child(gtk_scrolled := self.new_native(Gtk.ScrolledWindow, hexpand=True, vexpand=True))

        try:
            import gi
         #   gi.require_version("EvinceView", "4.0")
            from gi.repository import EvinceView
            from gi.repository import EvinceDocument
            EvinceDocument.init()
            btn_toc = Gtk.Button(image=Gtk.Image(stock="gtk-file"), halign=Gtk.Align.START, valign=Gtk.Align.START, margin_top=10, margin_start=30, visible=True)
            gtk_overlay.add_overlay(btn_toc)
            popover_toc = Gtk.Popover(relative_to=btn_toc)
            tocscroll = Gtk.ScrolledWindow(propagate_natural_width=True, propagate_natural_height=True, visible=True)
            popover_toc.add(tocscroll)
            lst_toc = Gtk.TreeView(headers_visible=False, activate_on_single_click=True, visible=True)
            tocscroll.add(lst_toc)
            lst_toc.append_column(Gtk.TreeViewColumn("", Gtk.CellRendererText(), text=0))
            def showtoc(_):
                popover_toc.popup()
            btn_toc.connect("clicked", showtoc)
            docview = EvinceView.View(visible=True)
            document = EvinceDocument.Document.factory_get_document(f"file://{self.model.path}")
            docview.set_model(EvinceView.DocumentModel.new_with_document(document))
            gtk_scrolled.set_child(docview)
            def set_toc(job):
                lst_toc.set_model(job.get_model())
                topsection = lst_toc.get_model().get_iter_first()
                while topsection:
                    lst_toc.expand_row(lst_toc.get_model().get_path(topsection), False)
                    topsection = lst_toc.get_model().iter_next(topsection)
            joblinks = EvinceView.JobLinks.new(document)
            joblinks.connect("finished", set_toc)
            joblinks.run()
            def goto(_, row, __):
                foo = lst_toc.get_model().get(lst_toc.get_model().get_iter(row), 1)[0]
                docview.handle_link(foo)
            lst_toc.connect("row-activated", goto)

        except ImportError:
            gtk_scrolled.set_child(gtk_fallback_box := self.new_native(Gtk.Box, orientation=Gtk.Orientation.VERTICAL,
                                                                       visible=self.bind.has_source))
            gtk_fallback_box.append(self.new_native(Gtk.Label, label=self.piece._fallback_text, wrap=True))
            gtk_fallback_box.append(self.new_native(Gtk.LinkButton, label=self.bind.path_str, uri=self.bind.path_uri))

        return gtk_overlay

    def _(self):
        return self.piece.source is not None
    has_source: bool = klovve.ui.computed_property(_)

    def _(self):
        return self.piece.source.absolute() if self.piece.source else None
    path_absolute: pathlib.Path|None = klovve.ui.computed_property(_)

    def _(self):
        return str(self.path_absolute or "")
    path_str: str = klovve.ui.computed_property(_)

    def _(self):
        return f"file://{self.path_str}"
    path_uri: str = klovve.ui.computed_property(_)
