#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import abc
import asyncio
import functools
import threading
import traceback
import typing as t

import klovve.driver
import klovve.error


class DriverLoop(abc.ABC):

    @property
    @abc.abstractmethod
    def event_loop(self) -> asyncio.AbstractEventLoop:
        pass

    @abc.abstractmethod
    def enqueue(self, coro) -> asyncio.Task:
        pass

    @abc.abstractmethod
    def run_until_tasks_finished(self):
        pass


class DefaultDriverLoop(DriverLoop):

    def __init__(self, event_loop: asyncio.AbstractEventLoop):
        self.__event_loop = event_loop
        self.__tasks: list[asyncio.Task] = []

    @property
    def event_loop(self):
        return self.__event_loop

    def enqueue(self, coro):
        async def _():
            try:
                await coro
            except Exception:
                klovve.error.critical_error_occurred(f"The loop task {task} raised an exception.",
                                                     traceback.format_exc())

        task = self.__event_loop.create_task(_())
        self.__tasks.append(task)
        return task

    def run_until_tasks_finished(self):
        while any(self.__tasks):
            if not (task := self.__tasks.pop()).done():
                self.__event_loop.run_until_complete(task)


def in_driver_loop(func: t.Callable) -> t.Callable:
    """
    Function decorator that dispatches function execution to the driver loop.

    :param func: The function to call inside the mainloop.
    """
    @functools.wraps(func)
    def func_(*args, **kwargs):
        driver_event_loop = klovve.driver.Driver.get().loop.event_loop
        try:
            current_event_loop = asyncio.get_running_loop()
        except RuntimeError:
            current_event_loop = None
        result, exception, result_arrived = None, None, False

        if current_event_loop is driver_event_loop:
            return func(*args, **kwargs)

        result_arrived_condition = threading.Condition()

        async def inner_func():
            nonlocal result, exception, result_arrived
            try:
                result = func(*args, **kwargs)
            except Exception as ex:
                exception = ex
            with result_arrived_condition:
                result_arrived = True
                result_arrived_condition.notify()
        driver_event_loop.create_task(inner_func())

        with result_arrived_condition:
            while not result_arrived:
                result_arrived_condition.wait()
        if exception:
            raise exception

        if hasattr(result, "__await__"):
            async def foo():
                result_, exception_, result_arrived_ = None, None, False
                result_arrived_condition = threading.Condition()

                async def inner_func():
                    nonlocal result_, exception_, result_arrived_
                    try:
                        result_ = await result
                    except Exception as ex:
                        exception_ = ex
                    with result_arrived_condition:
                        result_arrived_ = True
                        result_arrived_condition.notify()

                driver_event_loop.create_task(inner_func())

                with result_arrived_condition:
                    while not result_arrived_:
                        result_arrived_condition.wait()
                if exception_:
                    raise exception_
                return result_


            return foo()

        return result

    return func_


class _DriverLoopObjectProxy:
    """
    Simple proxy object that is wrapped around another one, ensuring that all interactions with it take place inside the
    mainloop.
    """

    def __init__(self, obj):
        self.__obj = obj

    def __getattr__(self, item):
        def getter():
            value = getattr(self.__obj, item)

            if callable(value):
                def func_wrapper(*args, **kwargs):
                    return in_driver_loop(lambda: value(*args, **kwargs))()
                return func_wrapper

            return value
        return in_driver_loop(getter)()

    def __setattr__(self, key, value):
        if key == f"{_DriverLoopObjectProxy.__name__}__obj":
            super().__setattr__(key, value)
        else:
            def set_func():
                setattr(self.__obj, key, value)
            if threading.current_thread() == threading.main_thread():
                set_func()
            else:
                in_driver_loop(set_func)()


def object_proxy[T](obj: T) -> T:
    return _DriverLoopObjectProxy(obj)


def verify_correct_thread() -> None:
    """
    Raise an exception if called from another thread than the klovve thread (i.e. the process main thread).
    Otherwise, do nothing.
    """
    if threading.current_thread() != driver_loop_thread():
        raise RuntimeError("access to this klovve feature is not allowed from this thread")


def driver_loop_thread() -> threading.Thread:
    return threading.main_thread()
