#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
Foundation for Klovve applications.

See :py:class:`BaseApplication` and :py:class:`Application`.
"""
import abc
import asyncio
import typing as t

import klovve.app.runnable
import klovve.data
import klovve.driver
import klovve.event
import klovve.builtin.views.window
import klovve.builtin.views.interact
import klovve.object
import klovve.timer
import klovve.variable


class BaseApplication(abc.ABC):
    """
    Base class for Klovve applications.

    You should not directly subclass it. See :py:class:`Application`.
    """

    class ActionTriggeredEvent(klovve.event.Event):
        """
        Event that occurs when an action was triggered, usually by the user clicking on a button or similar.
        """

        def __init__(self, triggering_view: klovve.ui.View, action_name: str):
            super().__init__()
            self.__triggering_view = triggering_view
            self.__action_name = action_name

        @property
        def action_name(self) -> str:
            """
            The action name.
            """
            return self.__action_name

        @property
        def triggering_view(self) -> klovve.ui.View:
            """
            The triggering view (e.g. the button that was clicked).

            Often used in order to visually align a dialog to that view.
            """
            return self.__triggering_view

    @property
    @abc.abstractmethod
    def windows(self) -> klovve.data.list.List["klovve.builtin.views.window.Window"]:
        """
        List of application windows.
        """

    @abc.abstractmethod
    async def dialog(self, dialog: type["klovve.ui.dialog.BaseDialog"]|klovve.builtin.views.interact.AbstractInteract,
                     dialog_args=None, dialog_kwargs=None, *, view_anchor) -> t.Any:
        """
        Show a dialog to the user and return the dialog result.

        :param dialog: The dialog to show. Either a subclass of :py:class:`klovve.ui.dialog.BaseDialog` or an
                       :code:`interact` view.
        :param dialog_args: The dialog args.
        :param dialog_kwargs: The dialog kwargs.
        :param view_anchor: The parent view to visually align the dialog to.
        """

    @abc.abstractmethod
    def _handle_event(self, event):
        pass

    @property
    @abc.abstractmethod
    def _is_running(self) -> bool:
        """
        Whether this application is running.
        """

    @abc.abstractmethod
    async def _wait_until_finished(self) -> None:
        """
        Wait until this application has been finished.
        """

    @property
    @abc.abstractmethod
    def driver_compatibility(self) -> "klovve.driver.Driver.CompatibilitySpecification":
        """
        The driver compatibility specification for this application.
        """

    @abc.abstractmethod
    def _started(self, driver: "klovve.driver.Driver") -> None:
        """
        Called just after this application has been started.

        :param driver: The Klovve driver.
        """

    def enqueue_task(self, coro):
        """
        Enqueue a task to the driver loop.

        :param coro: The coroutine to add as a new task.
        """
        klovve.driver.Driver.get().loop.enqueue(coro)

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class Application(klovve.object.Object, klovve.event._EventHandlingObject, klovve.timer._TimingObject,
                  klovve.object.WithPublicBind, BaseApplication):

    def __init__(self, **kwargs):
        super().__init__()
        self._set_data_by_kwargs(kwargs)
        self.__windows = klovve.data.list.List["klovve.builtin.views.window.Window"]()
        self.__windows.add_observer(
            Application._RemoveWindowsWhenClosedListObserver, (self,),
            initialize_with=klovve.variable.no_dependency_tracking(), owner=self)
        self.__finished_future = None

    def _started(self, driver):
        self._initialize_timing()
        self.__finished_future = asyncio.Future()
        self.__windows.add_observer(
            Application._FinishApplicationAfterLastWindowClosedListObserver, (self, self.__finished_future),
            initialize_with=klovve.variable.no_dependency_tracking(), owner=self)

    @property
    def driver_compatibility(self):
        return Application._CompatibilitySpecification(level=klovve.driver.Driver.LEVEL_GRAPHICAL)

    @property
    def windows(self):
        return self.__windows

    @property
    def _is_running(self) -> bool:
        return (self.__finished_future is not None) and (not self.__finished_future.done())

    async def dialog(self, dialog, dialog_args=None, dialog_kwargs=None, *, view_anchor, title: str|None = None,
                     is_inline: bool|None = None, is_modal: bool|None = None, is_closable_by_user: bool|None = None):
        if isinstance(dialog, klovve.ui.View):
            dialog = klovve.ui.dialog._InteractDialog[dialog]

        return await klovve.driver.Driver.get().dialog_host.show_dialog(
            self, view_anchor, dialog, dialog_args, dialog_kwargs, title=title, is_inline=is_inline, is_modal=is_modal,
            is_closable_by_user=is_closable_by_user)

    async def _wait_until_finished(self):
        await self.__finished_future

    class _CompatibilitySpecification(klovve.driver.Driver.CompatibilitySpecification):

        def __init__(self, *, level: float):
            self.__level = level

        def is_driver_compatible(self, driver):
            return driver.level() >= self.__level

    class _FinishApplicationAfterLastWindowClosedListObserver(klovve.data.list.List.Observer):

        def __init__(self, app, finished_future):
            super().__init__()
            self.__app = app
            self.__finished_future = finished_future

        def item_removed(self, index, item):
            if len(self.__app.windows) == 0:
                self.__finished_future.set_result(True)

        def item_added(self, index, item):
            pass

    class _RemoveWindowsWhenClosedListObserver(klovve.data.list.List.Observer):

        def __init__(self, app):
            super().__init__()
            self.__app = app

        def item_removed(self, index, item):
            pass

        def item_added(self, index, item):
            klovve.effect.activate_effect(Application._RemoveWindowWhenClosedEffect, (self.__app, item), owner=item)

    class _RemoveWindowWhenClosedEffect(klovve.effect.Effect):

        def __init__(self, app, window):
            super().__init__()
            self.__app = app
            self.__window = window

        def run(self):
            if self.__window._is_closed and self.__window in self.__app.windows:
                self.__app.windows.remove(self.__window)


def create(application: "BaseApplication|klovve.builtin.views.window.Window") -> "klovve.app.runnable.Runnable":
    """
    Create a new application and return a runnable for it.

    :param application: Either an application or a window (in the latter case, a minimal application is implicitly
                        constructed around it).
    """
    if isinstance(application, klovve.builtin.views.window.Window):
        window = application
        application = Application()
        application.windows.append(window)

    return _create(application, klovve.driver.Driver.get(application.driver_compatibility))


def _create(application: BaseApplication, driver: "klovve.driver.Driver") -> "klovve.app.runnable.Runnable":
    return driver.new_runnable_for_application(application)
