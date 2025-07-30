#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
See :py:class:`ProgressBar`.
"""
import klovve


class ProgressBar(klovve.ui.Piece):
    """
    A progress bar.
    """

    #: The current progress value. Between 0 and 1.
    value: float = klovve.ui.property(initial=0)

    vertical_layout = klovve.ui.property(initial=klovve.ui.Layout(klovve.ui.Align.CENTER))
