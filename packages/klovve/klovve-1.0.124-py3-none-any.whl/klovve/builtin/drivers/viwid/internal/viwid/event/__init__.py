#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
Events provide a way to signal to the widgets that something has happened, so they can react to that. Events can be
caused directly by external sources, like user input, or can be triggered by other widgets, e.g. when a button gets
somehow triggered.

See :py:class:`Event`.
"""


class Event:
    """
    Base class for events.

    An event represents that fact that something has happened. Usually, events are instances of a subclass of `Event`,
    specifying what exactly has happened, including all information required to react to it in a useful way. For
    events coming from external sources, like user input, there are various subclasses in this package's subpackages.
    Many widgets also define their own events, so you can e.g. react on a button being triggered (in any way). You will
    find these events there.

    For handling an event, multiple widgets can be involved on the axis up all of its ancestors. A widget can register
    handlers for particular types of events, and can specify whether it wants to preview events or not. Each handler can
    also be marked to be an implementation default handler (see later what that means).

    Each event happens at one particular origin widget. At first, from the screen layer's root widget downwards to the
    origin widget, the registered 'preview' handlers get executed. Then, from the origin widget upwards to the root
    widget, the 'non-preview' handlers get executed. Only in rare cases (usually for events where this cascade does not
    make sense), event handling is restricted to the origin widget.

    Also, in all of these steps, it will at first execute all widget's event handlers that are not marked as default
    handlers and then the ones marked as default handlers.

    During the entire event handling, all further steps can be skipped by calling :py:meth:`stop_handling`. So, whenever
    you call it, you skip at least all the default handling of the current step and everything later.
    """

    def __init__(self):
        """
        Usually, events are instances of a subclass of `Event`.
        """
        self.__is_handling_stopped = False

    @property
    def is_handling_stopped(self) -> bool:
        """
        Whether the event handling was stopped by :py:meth:`stop_handling`.
        """
        return self.__is_handling_stopped

    def stop_handling(self) -> None:
        """
        Stop executing further event handlers.
        """
        self.__is_handling_stopped = True


import viwid.event.widget
import viwid.event.keyboard
import viwid.event.mouse
