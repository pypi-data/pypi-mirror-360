#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import abc


class Runnable(abc.ABC):

    @abc.abstractmethod
    def start(self) -> None:
        """
        Start the application.

        Must be called from inside the Klovve driver loop. Returns directly after starting (non-blocking). Afterward,
        until it gets closed, :py:meth:`sleep_until_stopped` will sleep and :py:attr:`is_running` will be `True`.
        """

    @abc.abstractmethod
    def run(self) -> None:
        """
        Run the application and wait until it is closed.

        This is only allowed to be called in the main thread, and when no `asyncio` event loop is currently running in
        that thread. In particular, it is not allowed to be called when another Klovve application is already running in
        that process. For running multiple applications, use :py:meth:`start` and maybe :py:meth:`sleep_until_stopped`
        instead.
        """

    async def sleep_until_stopped(self) -> None:
        """
        Wait until the application is stopped. Also return if it was not even started yet.

        Must be called from inside the Klovve driver loop.
        """

    @property
    @abc.abstractmethod
    def is_running(self) -> bool:
        """
        Whether this application is currently running.
        """
