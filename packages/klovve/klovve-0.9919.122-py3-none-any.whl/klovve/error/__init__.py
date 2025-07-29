#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import sys
import typing as t

import klovve.debug


def critical_error_occurred(message: str, details: str):
    klovve.debug.log.error(f"A critical internal error has occurred!\n{message}\nDetails:\n{details}")
    if not (_current_error_handler or _default_error_handler)(message, details):
        sys.exit(32)


_TErrorHandler = t.Callable[[str, str], bool|None]


def set_error_handler(handler: _TErrorHandler|None) -> None:
    global _current_error_handler
    if handler and _current_error_handler:
        raise RuntimeError("there is already an error handler")
    _current_error_handler = handler


_current_error_handler = None


def _default_error_handler(message: str, details: str):
    pass
