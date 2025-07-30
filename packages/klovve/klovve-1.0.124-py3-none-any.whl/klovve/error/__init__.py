#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
Error handling.
"""
import sys
import typing as t

import klovve.debug


def critical_error_occurred(message: str, details: str):
    """
    Called by the infrastructure whenever a critical error occurred.

    This logs the error, calls the registered error handler (see :py:func:`set_error_handler`) or the default one,
    and maybe even terminates the current process.

    :param message: The error message.
    :param details: Additional error details.
    """
    klovve.debug.log.error(f"A critical internal error has occurred!\n{message}\nDetails:\n{details}")
    if not (_current_error_handler or _default_error_handler)(message, details):
        sys.exit(32)


_TErrorHandler = t.Callable[[str, str], bool|None]


def set_error_handler(handler: _TErrorHandler|None) -> None:
    """
    Set a handler for critical errors.

    :param handler: The new error handler.
    """
    global _current_error_handler
    if handler and _current_error_handler:
        raise RuntimeError("there is already an error handler")
    _current_error_handler = handler


_current_error_handler = None


def _default_error_handler(message: str, details: str):
    pass
