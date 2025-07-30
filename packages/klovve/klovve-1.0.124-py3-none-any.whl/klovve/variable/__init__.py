#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
Klovve variables can store arbitrary data and can be observed in order to handle changes.

They are mostly used internally, e.g. by properties of :py:class:`klovve.model.Model`, UI elements, and some others.
They are part of the foundation for their reactive behavior. Klovve applications do not use them directly.
"""
from .base import Variable, no_dependency_tracking, using_variable_getter_called_handler, pause_refreshing
from .list import ListVariable
from .simple import SimpleVariable
