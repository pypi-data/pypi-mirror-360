#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
Drivers.

See :py:class:`Driver`.
"""
import abc
import asyncio
import importlib
import pkgutil
import threading
import traceback
import typing as t
import weakref

from klovve.app.runnable import Runnable
import klovve.app.tree
import klovve.data
import klovve.debug
import klovve.driver.loop
import klovve.error
import klovve.event.controller
import klovve.object
import klovve.variable
import klovve.ui.materialization
import klovve.ui.dialog


class Driver[TNative](abc.ABC):
    """
    Internal infrastructure functionality that depends on a particular UI provider implementation.
    """

    __driver = None
    __driver_modules = ["klovve.builtin.drivers"]

    LEVEL_TERMINAL = 3
    LEVEL_GRAPHICAL = 5

    @staticmethod
    def add_driver_module(module_name: str) -> None:
        """
        Add a module that contains driver implementations.

        :param module_name: The name of the Python module that contains driver implementations in its submodules.
        """
        Driver.__driver_modules.append(module_name)

    @staticmethod
    def get(compatibility_spec: t.Optional["CompatibilitySpecification"] = None) -> "Driver":
        """
        Return the current Klovve driver.
        """
        if Driver.__driver is None:
            if compatibility_spec is None:
                raise RuntimeError("there is no klovve driver set up yet")

            for driver_type in Driver._all_available():
                if compatibility_spec.is_driver_compatible(driver_type):
                    Driver.__driver = driver = driver_type()
                    driver.__enter__()
                    klovve.error.set_error_handler(driver.handle_critical_error)
                    driver._add_on_finished_handler(Driver._on_current_driver_finished)
                    break
            else:
                raise Driver.IncompatibleError()

        elif (compatibility_spec is not None) and (not compatibility_spec.is_driver_compatible(Driver.__driver)):
            raise Driver.IncompatibleError()

        return Driver.__driver

    @staticmethod
    def _all_available() -> t.Iterable[type["Driver"]]:
        """
        Return all available Klovve drivers.
        """
        all_available = []

        for driver_module_root_name in Driver.__driver_modules:
            try:
                driver_module_root = importlib.import_module(driver_module_root_name)
                for driver_module_info in pkgutil.iter_modules(driver_module_root.__path__):
                    try:
                        driver_module = importlib.import_module(f"{driver_module_root_name}.{driver_module_info.name}")
                        driver_type = getattr(driver_module, "Driver", None)
                        all_available.append(driver_type)
                    except Exception:
                        klovve.debug.log.debug(traceback.format_exc())

            except Exception:
                klovve.debug.log.debug(traceback.format_exc())

        return sorted(all_available, key=lambda driver_type: (-driver_type.level(), driver_type.name()))

    @staticmethod
    def _on_current_driver_finished():
        klovve.error.set_error_handler(None)
        Driver.__driver.__exit__(None, None, None)
        Driver.__driver = None

    @classmethod
    @abc.abstractmethod
    def name(cls) -> str:
        """
        Return the driver name.
        """

    @classmethod
    @abc.abstractmethod
    def level(cls) -> float:
        """
        Return the driver level value.

        Usually, higher levels are better. Drivers with a higher level will be preferred.
        """

    @abc.abstractmethod
    def new_runnable_for_application(self, application: "klovve.app.BaseApplication") -> Runnable:
        """
        Return a new runnable for an application.

        :param application: The application.
        """

    _TMaterialization = klovve.ui.materialization.ViewMaterialization[t.Self, TNative]

    @abc.abstractmethod
    def piece_materializer(self, *, event_controller: "klovve.event.controller.EventController",
                           application_tree: "klovve.app.tree.MaterializationObservingApplicationTree"
                           ) -> klovve.ui.materialization.PieceMaterializer[_TMaterialization]:
        """
        Create and return a piece materializer.

        :param event_controller: The event controller to use.
        :param application_tree: The application tree to use.
        """

    @property
    @abc.abstractmethod
    def loop(self) -> "klovve.driver.loop.DriverLoop":
        """
        The driver's loop.
        """

    @property
    @abc.abstractmethod
    def applications(self) -> t.Iterable["klovve.app.BaseApplication"]:
        """
        All running applications.
        """

    @property
    @abc.abstractmethod
    def dialog_host(self) -> "klovve.ui.dialog._DialogHost":
        """
        The dialog host.
        """
        pass

    @abc.abstractmethod
    def handle_critical_error(self, message: str, details: str) -> bool|None:
        """
        Called when a critical error has occurred.

        Return :code:`True` in order to prevent the process from being stopped.

        :param message: The error message.
        :param details: Additional error details.
        """

    @abc.abstractmethod
    def _add_on_finished_handler(self, func):
        pass

    @abc.abstractmethod
    def __enter__(self):
        pass

    @abc.abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    class CompatibilitySpecification(abc.ABC):

        @abc.abstractmethod
        def is_driver_compatible(self, driver: type["Driver"]) -> bool:
            pass

    class IncompatibleError(Exception):

        def __init__(self, msg=None):
            super().__init__(msg or "there is no klovve driver available for this request or an incompatible klovve"
                                    " driver is already loaded in this process")


class BaseDriver[TNative](Driver[TNative], abc.ABC):
    """
    Simple base implementation for a Klovve driver.
    """

    def __init__(self, driver_loop: "klovve.driver.loop.DriverLoop"):
        super().__init__()
        self.__loop = driver_loop
        self.__applications = {}
        self.__dialog_host = BaseDriver._DialogHost(self, self.__applications)
        self.__effect_host_context = None
        self.__timing_host_context = None
        self.__finished_future = asyncio.Future(loop=driver_loop.event_loop)
        self.__on_finished_handlers = []
        self.__critical_error_occurred_message_already_shown = False
        self.__error_handler_lock = threading.Lock()

    @property
    def loop(self):
        return self.__loop

    @property
    def applications(self):
        return tuple(self.__applications.keys())

    @property
    def dialog_host(self):
        return self.__dialog_host

    @classmethod
    def name(cls):
        return cls.__module__.split(".")[-1]

    @abc.abstractmethod
    def _show_window(self,
                     materialization: "klovve.ui.materialization.ViewMaterialization[klovve.views.Window]") -> None:
        pass

    @abc.abstractmethod
    def _close_window(self,
                      materialization: "klovve.ui.materialization.ViewMaterialization[klovve.views.Window]") -> None:
        pass

    @abc.abstractmethod
    async def _show_dialog(self, dialog: klovve.ui.dialog.BaseDialog, result_future: asyncio.Future,
                           dialog_body_native: t.Any, view_anchor: "klovve.ui.View", title: str, is_inline: bool,
                           is_modal: bool, is_closable_by_user: bool) -> None:
        pass

    @abc.abstractmethod
    async def _show_special_dialog(self, dialog: klovve.ui.dialog._SpecialDialog, result_future: asyncio.Future,
                                   view_anchor: "klovve.ui.View", title: str, is_inline: bool, is_modal: bool,
                                   is_closable_by_user: bool) -> None:
        pass

    def piece_materializer(self, *, event_controller, application_tree):
        return BaseDriver._PieceMaterializer(self, event_controller, application_tree)

    def new_runnable_for_application(self, application):
        return BaseDriver._Runnable(self, application)

    def handle_critical_error(self, message, details):
        with self.__error_handler_lock:
            if self.__critical_error_occurred_message_already_shown:
                return True
            self.__critical_error_occurred_message_already_shown = True
            try:
                if len(applications := tuple(self.applications)) > 0:
                    if len(windows := [window for application in applications for window in application.windows]) > 0:
                        for window in windows:
                            self.loop.enqueue(window.application.dialog(klovve.views.interact.Message(
                                message="A critical internal error has occurred!\n\n"
                                        "You should try to save your data and restart it as soon as possible!\n\n"
                                        "If the error occurs regularly, you should contact the vendor.\n",
                                choices=(("OK", None),)
                            ), view_anchor=window))
                        return True
            except Exception:
                klovve.debug.log.error(traceback.format_exc())

    def _add_on_finished_handler(self, on_finished_handler):
        if self.__finished_future.done():
            on_finished_handler()
        else:
            self.__on_finished_handlers.append(on_finished_handler)

    def _start_application(self, runnable, application):
        application_tree = klovve.app.tree.SimpleMaterializationObservingApplicationTree()
        application_tree.visited(application)
        event_controller = klovve.event.controller.ApplicationTreeBasedEventController(application_tree)
        self.__applications[application] = application_tuple = (event_controller, application_tree)
        application.windows.add_observer(BaseDriver._WindowListObserver, (*application_tuple, self),
                                         initialize_with=klovve.variable.no_dependency_tracking(), owner=application)
        self.loop.enqueue(self.__handle_application_finished(application))
        application._started(self)
        application.__enter__()

    async def _wait_until_finished(self):
        await self.__finished_future

    async def __handle_application_finished(self, application: "klovve.app.BaseApplication"):
        await application._wait_until_finished()
        application.__exit__(None, None, None)
        self.__applications.pop(application)

        if len(self.__applications) == 0:
            self.__finished_future.set_result(True)
            for on_finished_handler in self.__on_finished_handlers:
                on_finished_handler()

    def __enter__(self):
        self.__effect_host_context = klovve.effect._effect_host.connect_driver_loop(self.loop)
        self.__effect_host_context.__enter__()
        self.__timing_host_context = klovve.timer._timing_host.connect_driver_loop(self.loop)
        self.__timing_host_context.__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__effect_host_context.__exit__(exc_type, exc_val, exc_tb)
        self.__effect_host_context = None
        self.__timing_host_context.__exit__(exc_type, exc_val, exc_tb)
        self.__timing_host_context = None

    class _Runnable(Runnable):

        def __init__(self, driver: "BaseDriver", application: "klovve.app.BaseApplication"):
            super().__init__()
            self.__driver = driver
            self.__application = application

        def start(self):
            if asyncio.get_running_loop() != self.__driver.loop.event_loop:
                raise RuntimeError("this is only allowed inside the klovve driver loop")

            self.__driver._start_application(self, self.__application)

        def run(self):
            async def _start():
                self.start()
            self.__driver.loop.enqueue(_start())
            self.__driver.loop.enqueue(self.__driver._wait_until_finished())
            self.__driver.loop.run_until_tasks_finished()

        @property
        def is_running(self):
            return self.__application._is_running

    class _PieceMaterializer[TNative](klovve.ui.materialization.PieceMaterializer):

        def __init__(self, driver: "BaseDriver",
                     event_controller: "klovve.event.controller.EventController[klovve.ui.View]", application_tree):
            super().__init__()
            self.__driver = driver
            self.__event_controller = event_controller
            self.__application_tree = application_tree

        def materialize_piece(self, piece):
            for piece_type_ in type(piece).mro():
                try:
                    materialization_type = importlib.import_module(
                        self.__piece_materialization_module_name(piece_type_.__module__))
                    break
                except (ValueError, ModuleNotFoundError):
                    pass
            else:
                raise RuntimeError(f"unable to materialize {piece}")

            for name_segment in piece_type_.__qualname__.split("."):
                materialization_type = getattr(materialization_type, name_segment)

            return materialization_type(piece, self.__event_controller, self.__application_tree)

        def __piece_materialization_module_name(self, piece_module_name: str) -> str:
            i_pieces_str = piece_module_name.find(".views.")
            if i_pieces_str == -1:
                raise ValueError(f"invalid piece module name {piece_module_name!r}")
            return f"{type(self.__driver).__module__}{piece_module_name[i_pieces_str:]}"

    class _BaseViewMaterialization[TPiece, TNative, TNativeTypeSpec](klovve.ui.materialization.ViewMaterialization[TPiece, TNative], klovve.object.WithPublicBind, abc.ABC):

        def materialize_child(self, view):
            return klovve.driver._materialize(view, self.event_controller, self.application_tree)

        @classmethod
        @abc.abstractmethod
        def _internal_new_native_by_type_spec(cls, native_type_spec: TNativeTypeSpec,
                                              property_values: dict[str, t.Any]) -> TNative:
            pass

        @classmethod
        @abc.abstractmethod
        def _internal_native_property_value(cls, view_native: TNative, key: str) -> t.Any:
            pass

        @classmethod
        @abc.abstractmethod
        def _internal_set_native_property_value(cls, view_native: TNative, key: str, value: t.Any) -> None:
            pass

        @classmethod
        @abc.abstractmethod
        def _internal_add_native_property_changed_handler(cls, view_native: TNative, key: str,
                                                          handler: t.Callable[[], None]) -> None:
            pass

        @classmethod
        @abc.abstractmethod
        def _internal_set_common_property_value(cls, view_native: TNative, prop, value: t.Any) -> None:
            pass

        _COMMON_PROPERTIES = {attr_name: attr for attr_name, attr in klovve.ui.View.__dict__.items()
                              if isinstance(attr, klovve.object.BaseProperty)}

        def new_native(self, native_type_spec: TNativeTypeSpec, view: t.Optional["klovve.ui.View"] = None,
                        **kwargs) -> TNative:
            value_variables = {}
            values = {}
            for prop_name, value in kwargs.items():
                if isinstance(value, klovve.variable.Variable):
                    value_variables[prop_name] = value
                else:
                    values[prop_name] = value

            view_native = self._internal_new_native_by_type_spec(native_type_spec, values)
            klovve.debug.memory.new_object_created("ViewNative", view_native)

            for prop_name, variable in value_variables.items():
                self.__bind(view_native, prop_name, None, variable)
            if view:
                for prop_name, prop in self._COMMON_PROPERTIES.items():
                    self.__bind(view_native, prop_name, prop, getattr(view.bind, prop_name))

            return view_native

        def __bind(self, view_native, prop_name, base_prop, variable: klovve.variable.Variable):
            klovve.effect.activate_effect(BaseDriver._BaseViewMaterialization.__RefreshNativeProperty,
                                          (view_native, prop_name, base_prop, variable, type(self)),
                                          owner=view_native)

            if base_prop is None and variable.is_externally_settable():
                def __refresh_variable_value():
                    variable.set_value(self._internal_native_property_value(view_native, prop_name))
                self._internal_add_native_property_changed_handler(view_native, prop_name, __refresh_variable_value)

        class __RefreshNativeProperty(klovve.effect.Effect):

            def __init__(self, view_native, prop_name, base_prop, variable,
                         materialization_internal: "BaseDriver._BaseViewMaterialization"):
                super().__init__()
                self.__view_native = weakref.ref(view_native)
                self.__prop_name = prop_name
                self.__base_prop = base_prop
                self.__variable = variable
                self.__materialization_internal = materialization_internal

            def run(self):
                view_native = self.__view_native()
                if not view_native:
                    return

                new_source_value = self.__variable.value()
                if self.__base_prop is None:
                    old_source_value = self.__materialization_internal._internal_native_property_value(
                        view_native, self.__prop_name)

                    if new_source_value != old_source_value:
                        self.__materialization_internal._internal_set_native_property_value(
                            view_native, self.__prop_name, new_source_value)

                else:
                    self.__materialization_internal._internal_set_common_property_value(view_native, self.__base_prop, new_source_value)

    class _WindowListObserver(klovve.data.list.List.Observer):

        def __init__(self, event_controller, application_tree, driver):
            super().__init__()
            self.__windows = {}
            self.__event_controller = event_controller
            self.__application_tree = application_tree
            self.__driver = driver

        def item_added(self, index, item):
            window_materialization = self.__windows[item] = _materialize(item, self.__event_controller,
                                                                         self.__application_tree)
            self.__driver._show_window(window_materialization)

        def item_moved(self, from_index, to_index, item):
            pass

        def item_removed(self, index, item):
            self.__driver._close_window(self.__windows.pop(item))

    class _DialogHost(klovve.ui.dialog._DialogHost):

        def __init__(self, driver, applications):
            super().__init__()
            self.__driver = driver
            self.__applications = applications

        async def show_dialog(self, application, view_anchor, dialog, dialog_args, dialog_kwargs, *, title=None,
                              is_inline=None, is_modal=None, is_closable_by_user=None):
            event_controller, application_tree = self.__applications[application]

            result_future = BaseDriver._DialogHost._Future()

            dialog_ = dialog(*(dialog_args or ()), **(dialog_kwargs or {}))
            dialog_._set_application(application)
            dialog_._set_result_future(result_future)

            title = dialog_.title if (title is None) else title
            is_inline = dialog_.is_inline if (is_inline is None) else is_inline
            is_modal = dialog_.is_modal if (is_modal is None) else is_modal
            is_closable_by_user = dialog_.is_closable_by_user if (is_closable_by_user is None) else is_closable_by_user

            if dialog_view := dialog_.view():
                for node in (dialog_, dialog_view):
                    application_tree = application_tree.for_child()
                    application_tree.visited(node)

                dialog_view._materialize(self.__driver.piece_materializer(event_controller=event_controller,
                                                                          application_tree=application_tree))

                await self.__driver._show_dialog(dialog_, result_future, dialog_view._materialization.native,
                                                 view_anchor, title, is_inline, is_modal, is_closable_by_user)

            else:
                await self.__driver._show_special_dialog(dialog_, result_future, view_anchor, title, is_inline,
                                                         is_modal, is_closable_by_user)

            return result_future.result()

        class _Future(asyncio.Future):

            def set_result(self, result):
                if not self.done():
                    super().set_result(result)


def _materialize(view, event_controller, application_tree):
    application_tree = application_tree.for_child()
    application_tree.visited(view)

    view._materialize(Driver.get().piece_materializer(event_controller=event_controller,
                                                      application_tree=application_tree))
    return view._materialization
