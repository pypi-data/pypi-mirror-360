#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import inspect
import traceback
import typing as t

import klovve.driver
import klovve.error


class Event:

    def __init__(self):
        self.__stopped = False

    def stop_processing(self) -> None:
        self.__stopped = True

    @property
    def processing_stopped(self) -> bool:
        return self.__stopped


def event_handler[TEvent](for_type: type[TEvent]|t.Callable[[Event], t.Any]|None = None):
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
