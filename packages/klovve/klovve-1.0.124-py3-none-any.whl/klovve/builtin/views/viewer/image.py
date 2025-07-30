#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
See :py:class:`Image`.
"""
import klovve


class Image(klovve.ui.Piece):
    """
    An image viewer.
    """

    #: The image source.
    source: bytes|None = klovve.ui.property()
