#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
See :py:class:`Form`.
"""
import klovve


class Form(klovve.ui.Piece):
    """
    A form.

    It shows a list of sections, one line per section, with an optional label for each section.

    See also :py:class:`Form.Section`.
    """

    class Section(klovve.model.Model):
        """
        A section in a :py:class:`Form`.
        """

        #: The section label.
        label: str = klovve.model.property(initial="")

        #: The section body.
        body: klovve.ui.View|None = klovve.model.property()

    #: The sections.
    sections: list[Section|klovve.ui.View|str] = klovve.ui.list_property()
