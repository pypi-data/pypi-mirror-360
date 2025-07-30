#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
Timers execute some routines in regular intervals.

See :py:func:`run_timed` and others.
"""
import abc
import asyncio
import contextlib
import functools
import traceback
import typing as t
import weakref

import klovve.driver
import klovve.error


class Timer(abc.ABC):
    """
    An object that implements a handler which can be executed in some regular interval.
    """

    @abc.abstractmethod
    def run(self, control: "_TimingHost.TimerControl"):
        pass


class _TimingHost(abc.ABC):

    class TimerControl(abc.ABC):

        @abc.abstractmethod
        def stop(self):
            pass

    @abc.abstractmethod
    def create_timer(self, timer: t.Union[type[Timer], t.Callable], timer_args=None, timer_kwargs=None, *,
                     interval: float, owner: t.Optional[object]) -> Timer:
        pass

    @abc.abstractmethod
    def stop_timer(self, timer: Timer) -> None:
        pass


class _FunctionBasedTimer(Timer):

    def __init__(self, func, func_args, func_kwargs):
        super().__init__()
        self.__func = func
        self.__func_args = func_args or ()
        self.__func_kwargs = func_kwargs or {}

    def run(self, control):
        return self.__func(control, *self.__func_args, **self.__func_kwargs)


class _DriverLoopBasedTimingHost(_TimingHost):

    class TimerControl(_TimingHost.TimerControl):

        def __init__(self, owner: object):
            super().__init__()
            self.__is_stopped = False
            self.__owner = weakref.ref(owner)

        def stop(self):
            self.__is_stopped = True

        @property
        def is_stopped(self) -> bool:
            return self.__is_stopped or (self.__owner() is None)

    def __init__(self):
        self.__driver_loop = None
        self.__owner_by_timer = weakref.WeakValueDictionary()
        self.__time_later = weakref.WeakValueDictionary()

    def create_timer(self, timer, timer_args=None, timer_kwargs=None, *, interval, owner):
        if isinstance(timer, type) and issubclass(timer, Timer):
            timer_type = timer
        else:
            timer_type, timer_args, timer_kwargs = _FunctionBasedTimer, (timer, timer_args, timer_kwargs), None
        timer_ = timer_type(*(timer_args or ()), **(timer_kwargs or {}))

        owner = timer_ if owner is None else owner
        driver_loop = self.__driver_loop
        timer_control = _DriverLoopBasedTimingHost.TimerControl(owner)
        if driver_loop is None:
            self.__time_later[(timer_, interval, timer_control)] = owner
        else:
            self.__enqueue(driver_loop, self.__run_func_timed(driver_loop, interval, timer_, timer_control, 0))

        self.__owner_by_timer[(timer_, timer_control)] = owner

        return timer_

    def stop_timer(self, timer):
        for timer_tuple in self.__owner_by_timer.keys():
            timer_, timer_control = timer_tuple
            if timer_ is timer:
                self.__owner_by_timer.pop(timer_tuple)
                timer_control.stop()
                break

    def __run_timer(self, timer, timer_control):
        coro = self.__with_error_handler(timer, timer_control)
        if hasattr(coro, "__await__"):
            klovve.driver.Driver.get().loop.enqueue(self.__with_error_handler_async(timer, coro))

    @contextlib.contextmanager
    def connect_driver_loop(self, driver_loop: "klovve.driver.loop.DriverLoop"):
        if self.__driver_loop is not None:
            raise RuntimeError("there is already a driver loop connected")

        for time_later_timer, time_later_interval, timer_control in self.__time_later:
            self.__enqueue(driver_loop,
                           self.__run_func_timed(driver_loop, time_later_interval, time_later_timer, timer_control, 0))
        self.__driver_loop = driver_loop
        self.__time_later = None
        try:
            yield
        finally:
            self.__driver_loop = None
            self.__time_later = weakref.WeakValueDictionary()

    def __with_error_handler(self, timer, timer_control):
        try:
            return timer.run(timer_control)
        except Exception:
            klovve.error.critical_error_occurred(f"The timer {timer} raised an exception.",
                                                 traceback.format_exc())

    async def __with_error_handler_async(self, timer, coro):
        try:
            await coro
        except Exception:
            klovve.error.critical_error_occurred(f"The timer {timer} raised an exception.",
                                                 traceback.format_exc())

    async def __run_func_timed(self, driver_loop, interval, timer, timer_control, next_interval=None):
        next_interval = interval if next_interval is None else next_interval
        await asyncio.sleep(next_interval)
        if timer_control.is_stopped:
            self.stop_timer(timer)
        else:
            self.__run_timer(timer, timer_control)
            self.__enqueue(driver_loop, self.__run_func_timed(driver_loop, interval, timer, timer_control))

    def __enqueue(self, driver_loop: "klovve.driver.loop.DriverLoop", coro):
        driver_loop.event_loop.create_task(coro)


_timing_host = _DriverLoopBasedTimingHost()


def run_timed(*, interval: float):
    """
    On an object that can have timer handlers (like Klovve views or models), decorate a function to be called in a
    given interval for the lifetime of that object.

    :param interval: The interval in seconds.
    """
    def decorator(func):
        @functools.wraps(func)
        def func_(self, _=None):
            return func(self)

        func_._klv_timed = getattr(func, "_klv_timed", [])
        func_._klv_timed.append((interval,))
        return func_
    return decorator


class _TimingObject:

    def _initialize_timing(self) -> None:
        for ttype in reversed(type(self).mro()):
            for k, v in ttype.__dict__.items():
                for (interval,) in getattr(v, "_klv_timed", ()):
                    _timing_host.create_timer(getattr(self, k), interval=interval, owner=self)
