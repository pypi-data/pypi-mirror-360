#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
Events related to widgets.
"""
from viwid.event import Event as _BaseEvent


class ResizeEvent(_BaseEvent):
    """
    Event that occurs when the widget size has been changed (for any reason).
    """
