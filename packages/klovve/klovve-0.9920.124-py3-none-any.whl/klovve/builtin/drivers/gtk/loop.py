#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import asyncio
import selectors

import gi
# noinspection PyUnresolvedReferences
from gi.repository import GLib


class EventLoop(asyncio.SelectorEventLoop):

    def __init__(self):
        self.__selector = _Selector(GLib.MainContext.default())
        super().__init__(self.__selector)

    def _call_soon(self, callback, args, context):
        result = super()._call_soon(callback, args, context)
        self.__selector.interrupt_glib_mainloop()
        return result

    def call_at(self, when, callback, *args, context=None):
        result = super().call_at(when, callback, *args, context=context)
        self.__selector.interrupt_glib_mainloop()
        return result

    def create_task(self, coro, *, name=None):
        result = super().create_task(coro, name=name)
        self.__selector.interrupt_glib_mainloop()
        return result


class _Selector(selectors._BaseSelectorImpl):

    def __init__(self, context):
        super().__init__()
        self.__glib_mainloop = GLib.MainLoop(context)
        self.__glib_mainloop_run = getattr(super(GLib.MainLoop, GLib.MainLoop), "run", GLib.MainLoop.run)
        self.__glib_event_source = _Source(self.__glib_mainloop)
        self.__glib_event_source.attach(context)

    def close(self):  # TODO order
        super().close()
        self.__glib_event_source.destroy()

    def register(self, fileobj, events, data=None):
        result = super().register(fileobj, events, data)
        self.__glib_event_source.add_fd(result.fd, events)
        return result

    def unregister(self, fileobj):
        result = super().unregister(fileobj)
        self.__glib_event_source.remove_fd(result.fd)
        return result

    def select(self, timeout=None):
        if (timeout is None) or (timeout > 0):
            self.__glib_event_source.set_ready_time(
                -1 if (timeout is None) else int(GLib.get_monotonic_time() + 1000000 * timeout))
            self.__glib_mainloop_run(self.__glib_mainloop)
        else:
            self.__glib_mainloop.get_context().iteration(False)
        return [(key, events) for key, events in
                [(key, self.__glib_event_source.get_events(key.fd) & key.events) for key in self.get_map().values()]
                if events]

    def interrupt_glib_mainloop(self):
        self.__glib_event_source.set_ready_time(0)


class _Source(GLib.Source):

    EVENT_TO_GLIB = {selectors.EVENT_READ: GLib.IOCondition.IN, selectors.EVENT_WRITE: GLib.IOCondition.OUT}.items()

    def __init__(self, main_loop):
        super().__init__()
        self.__fd_tags = {}
        self.__fd_events = {}  # TODO cleanup
        self.__main_loop = main_loop

    def prepare(self):
        return False, -1

    def check(self):
        return False

    def dispatch(self, callback, args):
        for fd, tag in self.__fd_tags.items():
            self.__fd_events[fd] = self.__fd_events.get(fd, 0) | self.__glib_to_python_events(self.query_unix_fd(tag))
        self.__main_loop.quit()
        return GLib.SOURCE_CONTINUE

    def get_events(self, fd):
        return self.__fd_events.get(fd, 0)

    def add_fd(self, fd, events):
        self.__fd_tags[fd] = self.add_unix_fd(fd, self.__python_to_glib_events(events))

    def remove_fd(self, fd):
        self.remove_unix_fd(self.__fd_tags.pop(fd))
        if fd in self.__fd_events:
            self.__fd_events.pop(fd)

    def __glib_to_python_events(self, glib_events):
        python_events = 0
        for event, glib_event in self.EVENT_TO_GLIB:
            if glib_events & glib_event:
                python_events |= event
        return python_events

    def __python_to_glib_events(self, python_events):
        glib_events = GLib.IOCondition(0)
        for python_event, glib_event in self.EVENT_TO_GLIB:
            if python_events & python_event:
                glib_events |= glib_event
        return glib_events
