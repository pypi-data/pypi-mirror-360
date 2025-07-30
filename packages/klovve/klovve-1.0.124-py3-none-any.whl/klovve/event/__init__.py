#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
Foundation for Klovve events.
"""
import inspect
import traceback
import typing as t

import klovve.driver
import klovve.error


class Event:
    """
    Base class for Klovve events.

    Events are a mechanism to notify and handle all kinds of runtime situations like user input or relevant changes of
    the system state. Whenever something relevant happens, some piece of code can trigger an event. Objects can have
    event handlers registered for that kind of event. All these handlers get executed when an event is triggered for
    that object.

    As long as the event handling is not stopped, events usually bubble up the ancestors, so they can also be handled
    there.

    There must be one subclass for each kind of event that needs to be considered. They often also contain further
    specific information. On observer side, event handlers are registered for some of these subclasses.
    """

    def __init__(self):
        self.__stopped = False

    def stop_processing(self) -> None:
        """
        Stop all further event processing.

        No more event handlers get executed after the current one.
        """
        self.__stopped = True

    @property
    def processing_stopped(self) -> bool:
        """
        Whether all further event processing was stopped.

        See :py:meth:`stop_processing`.
        """
        return self.__stopped


def event_handler[TEvent](for_type: type[TEvent]|t.Callable[[Event], t.Any]|None = None):
    """
    On an object that can have event handlers (like Klovve views or models), decorate a function to be a handler for a
    given event type.

    :param for_type: The event type. This is optional if the function's signature contains type hints.
    """
    if not (for_type is None or isinstance(for_type, type)):
        return event_handler(None)(for_type)

    def decorator(func: t.Callable[[TEvent], t.Any]) -> t.Callable[[TEvent], t.Any]:
        nonlocal for_type
        if for_type is None:
            for_type = tuple(inspect.signature(func).parameters.values())[1].annotation
        func_handlers = func._klv_event_handler = getattr(func, "_klv_event_handler", None) or []
        func_handlers.append((for_type,))
        return func

    return decorator


def action(name: str):
    """
    On an object that can have event handlers (like Klovve views or models), decorate a function to be a handler for a
    given action.

    Actions are triggered e.g. whenever the user clicks a button. There is also an event associated to that, but
    handling it directly would require some code to check the action name.

    :param name: The action name.
    """
    def decorator(func):
        func_actions = func._klv_action = getattr(func, "_klv_action", None) or []
        func_actions.append((name,))
        return func

    return decorator


class _EventHandlingObject:

    def _handle_event(self, event):
        for event_handler_ in self.__event_handlers(event):
            coro = self.__with_error_handler(event_handler_, event)
            if hasattr(coro, "__await__"):
                klovve.driver.Driver.get().loop.enqueue(self.__with_error_handler_async(event_handler_, coro))

    def __with_error_handler(self, event_handler_, event):
        try:
            return event_handler_(event)
        except Exception:
            klovve.error.critical_error_occurred(f"The event handler {event_handler_} raised an exception.",
                                                 traceback.format_exc())

    async def __with_error_handler_async(self, event_handler_, coro):
        try:
            await coro
        except Exception:
            klovve.error.critical_error_occurred(f"The event handler {event_handler_} raised an exception.",
                                                 traceback.format_exc())

    def __event_handlers(self, event):
        result = {}

        for ttype in reversed(type(self).mro()):
            for k, v in ttype.__dict__.items():
                for (for_type,) in getattr(v, "_klv_event_handler", ()):
                    if isinstance(event, for_type):
                        result[k] = getattr(self, k)

                if isinstance(event, klovve.app.BaseApplication.ActionTriggeredEvent):
                    for (action_name,) in getattr(v, "_klv_action", ()):
                        if action_name == event.action_name:
                            result[k] = self.__action_to_event_handler(getattr(self, k))

        return result.values()

    def __action_to_event_handler(self, func):
        if len([param for param in inspect.signature(func).parameters.values()
                if param.kind in [inspect.Parameter.POSITIONAL_OR_KEYWORD]]) < 1:
            func_ = func
            func = lambda _: func_()
        return func
