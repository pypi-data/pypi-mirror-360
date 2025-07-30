#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
Dialogs are additional planes of views that are displayed outside the application window for the purpose of some
interactivity with the user.

See also :py:class:`BaseDialog` and :py:class:`Dialog`.
"""
import abc
import asyncio
import pathlib
import typing as t

import klovve.event
import klovve.object
import klovve.timer


class BaseDialog(abc.ABC):
    """
    Base class for dialogs.

    Applications usually do not implement this class in order to show dialogs. Simpler and better would be to implement
    :py:class:`Dialog`. In fact, in simple cases, you would not even do that but use some of the builtin dialog
    functionality, like the :code:`interact` views. In any case, see also :py:meth:`klovve.app.BaseApplication.dialog`.
    """

    def __init__(self):
        super().__init__()
        self.__application = None
        self.__result_future = None

    @abc.abstractmethod
    def view(self) -> klovve.ui.View:
        """
        The dialog body.
        """

    @property
    @abc.abstractmethod
    def is_inline(self) -> bool:
        """
        Whether this dialog is to be displayed embedded into the main window in some way.

        This leads to a different visual representation and its behavior might also differ in details.
        The exact implementation depends on the :py:class:`klovve.driver.Driver` chosen at runtime.
        """

    @property
    @abc.abstractmethod
    def is_modal(self) -> bool:
        """
        Whether this dialog is to be modal, i.e. blocking the user to interact with its parent window.
        """

    @property
    @abc.abstractmethod
    def is_closable_by_user(self) -> bool:
        """
        Whether this dialog is to be closable by the user.

        Even if not, the custom dialog body may of course provide custom ways to close the dialog.
        """

    @property
    @abc.abstractmethod
    def title(self) -> t.Optional[str]:  # ignored if `is_inline`
        """
        The dialog title text.
        """

    @property
    def application(self) -> "klovve.app.BaseApplication":
        """
        The application that this dialog is associated to.
        """
        return self.__application

    def close(self, dialog_result: t.Any) -> None:
        """
        Close the dialog.

        :param dialog_result: The dialog result to return.
        """
        self.__result_future.set_result(dialog_result)

    def _set_application(self, application):
        self.__application = application

    def _set_result_future(self, result_future: asyncio.Future) -> None:
        self.__result_future = result_future


class Dialog(BaseDialog, klovve.object.Object, klovve.event._EventHandlingObject, klovve.timer._TimingObject, abc.ABC):
    """
    Base implementation for dialogs. See :py:class:`BaseDialog`.
    """

    def __init__(self, *, title: str|None = None, is_modal: bool = True, is_closable_by_user: bool = False,
                 is_inline: bool = True):
        """
        :param title: The dialog title text.
        :param is_modal: Whether this dialog is to be modal, i.e. blocking the user to interact with its parent window.
        :param is_closable_by_user: Whether this dialog is to be closable by the user.
        :param is_inline: Whether this dialog is to be displayed embedded into the main window in some way.
        """
        super().__init__()
        self.__title = title
        self.__is_modal = is_modal
        self.__is_closable_by_user = is_closable_by_user
        self.__is_inline = is_inline

    @property
    def title(self):
        return self.__title

    @property
    def is_modal(self):
        return self.__is_modal

    @property
    def is_closable_by_user(self):
        return self.__is_closable_by_user

    @property
    def is_inline(self):
        return self.__is_inline


class _InteractDialog(Dialog, abc.ABC):

    @property
    @abc.abstractmethod
    def _interact_view(self):
        pass

    def view(self):
        return self._interact_view

    def _handle_event(self, event):
        if isinstance(event, klovve.views.interact.AbstractInteract.AnsweredEvent):
            event.stop_processing()
            self.close(event.answer)
            return
        super()._handle_event(event)

        for event_handler in self.__event_handlers(event):
            coro = event_handler(event)
            if hasattr(coro, "__await__"):
                klovve.driver.Driver.get().loop.enqueue(coro)

    @classmethod
    def __class_getitem__(cls, item):
        class InteractDialog_(_InteractDialog):
            _interact_view = item
        return InteractDialog_


class _SpecialDialog(Dialog, abc.ABC):

    def __init__(self, *, title: str|None = None, is_modal: bool = True, is_closable_by_user: bool = False):
        super().__init__(title=title, is_modal=is_modal, is_closable_by_user=is_closable_by_user, is_inline=False)

    def view(self):
        return None

    @property
    def is_inline(self):
        return False

    is_closable_by_user = True


class Filesystem:
    """
    Filesystem dialogs.
    """

    class _FilesystemDialog(_SpecialDialog):

        def __init__(self, *, title: str | None = None, is_modal: bool = True, is_closable_by_user: bool = False,
                     start_in_directory: pathlib.Path|str|None = None):
            super().__init__(title=title, is_modal=is_modal, is_closable_by_user=is_closable_by_user)
            self.__start_in_directory = None if start_in_directory is None else pathlib.Path(start_in_directory)

        @property
        def start_in_directory(self) -> pathlib.Path|None:
            return self.__start_in_directory

    class _FileDialog(_FilesystemDialog):

        def __init__(self, *, title: str | None = None, is_modal: bool = True, is_closable_by_user: bool = False,
                     start_in_directory: pathlib.Path|str|None = None,
                     filters: t.Iterable[tuple[str, str]] = ((("*",), ""),)):
            super().__init__(title=title, is_modal=is_modal, is_closable_by_user=is_closable_by_user,
                             start_in_directory=start_in_directory)
            self.__filters = tuple(filters)

        @property
        def filters(self) -> t.Iterable[tuple[str, str]]:
            return self.__filters

    class OpenFileDialog(_FileDialog):
        """
        Open file dialog.
        """

    class SaveFileDialog(_FileDialog):
        """
        Save to file dialog.
        """

    class OpenDirectoryDialog(_FilesystemDialog):
        """
        Open directory dialog.
        """


class _DialogHost(abc.ABC):

    @abc.abstractmethod
    async def show_dialog(self, application, view_anchor, dialog: type[BaseDialog], dialog_args, dialog_kwargs, *,
                          title: str|None = None, is_inline: bool|None = None, is_modal: bool|None = None,
                          is_closable_by_user: bool|None = None) -> t.Any:
        pass
