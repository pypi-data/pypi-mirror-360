#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
Foundation for effects.

See :py:class:`Effect`.
"""
import abc
import asyncio
import contextlib
import traceback
import typing as t
import weakref

import klovve.variable
import klovve.debug
import klovve.driver.loop
import klovve.error


class Effect(abc.ABC):
    """
    An object that implements a handler that gets called, during activation, but also in a reactive way whenever one of
    the Klovve variables change that it referred.

    See also :py:func:`activate_effect`.
    """

    def __init__(self):
        klovve.debug.memory.new_object_created(Effect, self)

    @abc.abstractmethod
    def run(self) -> t.Optional[t.Awaitable]:
        """
        Run the effect.
        """


class _EffectHost(abc.ABC):

    class Run(abc.ABC):

        @property
        @abc.abstractmethod
        def is_done(self) -> bool:
            pass

        @abc.abstractmethod
        def cancel(self):
            pass

    @abc.abstractmethod
    def run_effect(self, effect: Effect, done_func: t.Callable) -> Run:
        pass


class _EffectController(abc.ABC):

    class _ChangedHandler(klovve.variable.Variable.ChangedHandler):

        def __init__(self, effect_controller: "_EffectController"):
            self.__effect_controller = effect_controller

        def handle(self, variable, value, version):
            self.__effect_controller.run_effect()

    def __init__(self, effect: Effect, effect_host: _EffectHost):
        self.__effect = effect
        self.__effect_host = effect_host
        self.__changed_handler = _EffectController._ChangedHandler(self)
        self.__current_dependency_variables = []
        self.__run = None

    @property
    def effect(self) -> Effect:
        return self.__effect

    def run_effect(self) -> None:
        for old_dependency_variable in self.__current_dependency_variables:
            old_dependency_variable.remove_changed_handler(self.__changed_handler)
        self.__current_dependency_variables = []

        if self.__run and not self.__run.is_done:
            self.__run.cancel()
            self.__run = None

        run = self.__effect_host.run_effect(self.__effect, self.__run_effect__done)
        if not run.is_done:
            self.__run = run

    def __run_effect__done(self, dependency_variable_tuples):
        for dependency_variable, dependency_variable_version in dependency_variable_tuples:
            if dependency_variable.current_version() != dependency_variable_version:
                return self.run_effect()

        dependency_variables = [_[0] for _ in dependency_variable_tuples]

        self.__current_dependency_variables = dependency_variables

        for dependency_variable in dependency_variables:
            dependency_variable.add_changed_handler(self.__changed_handler)

    def __run_effect__append_dependency_variable(self, v):
        self.__current_dependency_variables.append(v)


_TEffectHandle = t.NewType("_TEffectHandle", object)


def activate_effect(effect: t.Union[type[Effect], t.Callable], effect_args=None, effect_kwargs=None, *,
                    owner: t.Optional[object]) -> _TEffectHandle:
    """
    Activate an effect.

    The lifetime of an effect can either be bound to the lifetime of a given owner object, or can be handled manually
    by calling :py:func:`stop_effect`.

    :param effect: An effect type or a callable.
    :param effect_args: The effect args.
    :param effect_kwargs: The effect kwargs.
    :param owner: The owner. If :py:code:`None`, lifetime is handled manually.
    """
    if isinstance(effect, type) and issubclass(effect, Effect):
        effect_type = effect
    else:
        effect_type, effect_args, effect_kwargs = _FunctionBasedEffect, (effect, effect_args, effect_kwargs), None

    effect_ = effect_type(*(effect_args or ()), **(effect_kwargs or {}))
    effect_controller = _EffectController(effect_, _effect_host)
    _owner_by_effect_controller[effect_controller] = effect_ if owner is None else owner
    effect_controller.run_effect()
    return effect_


def stop_effect(effect: _TEffectHandle) -> None:
    """
    Stop an effect that was activated by :py:func:`activate_effect` before.

    :param effect: The effect to stop.
    """
    for event_controller, owner in _owner_by_effect_controller.items():
        if event_controller.effect is effect:
            _owner_by_effect_controller.pop(event_controller)
            break


def rerun_effect_manually(effect: _TEffectHandle) -> None:
    """
    Forcefully run an effect again.

    :param effect: The effect to run again.
    """
    for event_controller, owner in _owner_by_effect_controller.items():
        if event_controller.effect is effect:
            event_controller.run_effect()
            return

    raise RuntimeError("this effect was not yet started or was already stopped")


class _FunctionBasedEffect(Effect):

    def __init__(self, func, func_args, func_kwargs):
        super().__init__()
        self.__func = func
        self.__func_args = func_args or ()
        self.__func_kwargs = func_kwargs or {}

    def run(self):
        return self.__func(*self.__func_args, **self.__func_kwargs)


class _DriverLoopBasedEffectHost(_EffectHost):

    class _DoneRun(_EffectHost.Run):

        @property
        def is_done(self):
            return True

        def cancel(self):
            pass

    class _EnqueuedRun(_EffectHost.Run):

        def __init__(self, task: asyncio.Task):
            self.__task = task

        @property
        def is_done(self):
            return self.__task.done()

        def cancel(self):
            self.__task.cancel()

    class _EnqueueLaterRun(_EffectHost.Run):

        def __init__(self, coro):
            self.__coro = coro
            self.__enqueued_run = None

        @property
        def coro(self):
            return self.__coro

        def set_task(self, task):
            self.__enqueued_run = _DriverLoopBasedEffectHost._EnqueuedRun(task)

        @property
        def is_done(self):
            if self.__enqueued_run is not None:
                return self.__enqueued_run.is_done

            return self.__coro is None

        def cancel(self):
            if self.__enqueued_run is not None:
                return self.__enqueued_run.cancel()

            self.__coro = None

    def __init__(self):
        self.__driver_loop = None
        self.__enqueue_later_runs = []

    @contextlib.contextmanager
    def connect_driver_loop(self, driver_loop: "klovve.driver.loop.DriverLoop"):
        if self.__driver_loop is not None:
            raise RuntimeError("there is already a driver loop connected")

        for enqueue_later_run in self.__enqueue_later_runs:
            if enqueue_later_run.coro is not None:
                enqueue_later_run.set_task(driver_loop.enqueue(enqueue_later_run.coro))
        self.__driver_loop = driver_loop
        self.__enqueue_later_runs = None
        try:
            yield
        finally:
            self.__driver_loop = None
            self.__enqueue_later_runs = []

    def run_effect(self, effect, done_func):
        dependency_variables = []

        def add_dependency_variable(variable):
            dependency_variables.append((variable, variable.current_version()))

        with klovve.variable.using_variable_getter_called_handler(add_dependency_variable):
            try:
                coro = effect.run()
            except Exception:
                coro = None
                klovve.error.critical_error_occurred(f"The effect {effect} raised an exception.",
                                                     traceback.format_exc())

        if hasattr(coro, "__await__"):
            async def continue_effect():
                with klovve.variable.using_variable_getter_called_handler(add_dependency_variable):
                    try:
                        await coro
                    except Exception:
                        klovve.error.critical_error_occurred(f"The effect {effect} raised an exception.",
                                                             traceback.format_exc())
                done_func(dependency_variables)

            if self.__driver_loop:
                return self._EnqueuedRun(self.__driver_loop.enqueue(continue_effect()))
            else:
                run = self._EnqueueLaterRun(continue_effect())
                self.__enqueue_later_runs.append(run)
                return run

        else:
            done_func(dependency_variables)
            return self._DoneRun()


_effect_host = _DriverLoopBasedEffectHost()

_owner_by_effect_controller = weakref.WeakValueDictionary()
