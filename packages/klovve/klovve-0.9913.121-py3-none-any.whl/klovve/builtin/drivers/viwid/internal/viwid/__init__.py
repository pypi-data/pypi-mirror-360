#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
A library for user interfaces in terminals.

This is used internally by klovve as a fallback option when no better UI is available.
Not supported to be used outside klovve.
"""
import asyncio
import contextlib

from viwid.data.color import PlainColor, Color
from viwid.data.geometry import Orientation, Point, Offset, Size, Rectangle, Margin, Alignment
from viwid.data.numeric import NumericValueRange
import viwid.event
import viwid.layout
import viwid.widgets
from viwid.drivers import start as _drivers_start, stop as _drivers_stop


def _dbg(*s):
    import datetime
    with open("/tmp/viwid.log", "a") as f:
        f.write(str(datetime.datetime.now()) + "    " + " ".join(str(_) for _ in s) + "\n")


@contextlib.contextmanager
def context(event_loop: asyncio.BaseEventLoop|None = None):
    """
    Convenience function that prepares a viwid environment (i.e. it starts a driver) in a simple way.

    To be used in a `with` statement. In that context, it provides you with a :py:class:`viwid.drivers.Driver`, which
    can be used to set up the application (create the main window, wire up event handlers, etc.). As soon as you leave
    the `with`-context, the driver takes over the execution of your application (inside an event loop). As soon as no
    application is running anymore, it will stop the driver again and return.

    So, usually, virtually the entire application lifespan is happening between the end of your `with`-statement and
    the moment this function returns. Once it does, your application is considered to be terminated.

    See also the sample applications.

    There must be no event loop already running in the current thread!

    :param event_loop: The event loop to use. If unspecified, a new one will be created.
    """
    driver = _drivers_start(event_loop)
    try:
        yield driver
        async def _():
            while len(driver.apps.all_running) > 0:
                await asyncio.sleep(0)
        driver.event_loop.run_until_complete(_())
    finally:
        _drivers_stop()
