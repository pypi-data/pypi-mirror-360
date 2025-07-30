#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
Widget layouts control how a widgets aligns its children in the allocated space.

See also :py:class:`Layout` and :py:class:`GridLayout`.
"""
import abc
import typing as t

import viwid


class Layout(abc.ABC):
    """
    Base class for a widget layout. It controls how child widgets are aligned within a widget.

    It can also take over the widget size computation for widgets that do not paint own content but are only made up of
    child widgets. The mechanism is basically the same: There is a minimal and a preferred width demand, and a minimal
    and a preferred height demand for a given width.
    """

    @abc.abstractmethod
    def apply(self, widgets: t.Sequence["viwid.widgets.widget.Widget"], size: viwid.Size, *,
              forcefully_apply_resizing_for: t.Iterable["viwid.widgets.widget.Widget"] = ()) -> None:
        """
        For a given size, compute an alignment for given widgets that fits, and apply it.

        This usually leads to children also applying their layout, in order to react to a changed size.

        :param widgets: The widgets to align in the given area.
        :param size: The size of the available area to align widgets in.
        :param forcefully_apply_resizing_for: For each of these widgets (can be any widget, but it will only have an
                                              effect if it is one of `widgets` or a descendant), enforce that it
                                              recomputes its layout in turn, even if did not change in size.
        """

    @abc.abstractmethod
    def compute_layout_width(self, widgets: t.Sequence["viwid.widgets.widget.Widget"], minimal: bool) -> int:
        """
        Return what width is required at least in order to properly apply this layout to the given widgets.

        :param widgets: The widgets to measure.
        :param minimal: Whether to calculate the minimal demand or the preferred one for comfortable usage.
        """

    @abc.abstractmethod
    def compute_layout_height(self, widgets: t.Sequence["viwid.widgets.widget.Widget"], width: int,
                              minimal: bool) -> int:
        """
        Return what height is required at least in order to properly apply this layout to the given widgets for a given
        width.

        :param widgets: The widgets to measure.
        :param width: The maximum available width.
        :param minimal: Whether to calculate the minimal demand or the preferred one for comfortable usage.
        """


class NullLayout(Layout):
    """
    A layout that demands no space and keeps the widgets untouched. Usually this will keep them practically invisible.

    This is a widget's default layout unless its implementation (or usage) specifies another one.
    """

    def apply(self, widgets, size, *, forcefully_apply_resizing_for = ()):
        pass

    def compute_layout_width(self, widgets, minimal):
        return 0

    def compute_layout_height(self, widgets, width, minimal):
        return 0


TPartitioning = t.Sequence[t.Sequence["viwid.widgets.widget.Widget"]]
TPartitioner = t.Callable[[t.Sequence["viwid.widgets.widget.Widget"]], TPartitioning]


class GridLayout(Layout):
    """
    A layout that aligns widgets in a grid geometry.

    It respects each widget's :py:attr:`viwid.widgets.widget.Widget.horizontal_alignment` and
    :py:attr:`viwid.widgets.widget.Widget.vertical_alignment` as well as
    :py:attr:`viwid.widgets.widget.Widget.minimal_size`, :py:attr:`viwid.widgets.widget.Widget.margin` and other
    relevant ones.
    """

    #: A partitioner function leading to an 1-dimensional horizontal alignment.
    HORIZONTAL_PARTITIONER = lambda children: [[child for child in children]]

    #: A partitioner function leading to an 1-dimensional vertical alignment.
    VERTICAL_PARTITIONER = lambda children: [[child] for child in children]

    def __init__(self, partitioner: TPartitioner):
        """
        :param partitioner: A function that returns the 2-dimensional logical alignment for a list of widgets
                            (i.e. where in the grid to place which widget). See also
                            :py:attr:`GridLayout.HORIZONTAL_PARTITIONER` and :py:attr:`GridLayout.VERTICAL_PARTITIONER`.
        """
        self.__partitioner = partitioner

    def compute_layout_width(self, widgets, minimal):
        columns, _ = self.__horizontally_process_partitioning(self.__partitioner(list(widgets)), minimal)
        return sum(columns)

    def compute_layout_height(self, widgets, width, minimal):
        rows = self.__process_partitioning(self.__partitioner(list(widgets)), viwid.Size(width, 0), minimal_height=minimal)[1]
        return sum(rows)

    def apply(self, widgets, size, *, forcefully_apply_resizing_for = ()):
        partitioning = self.__partitioner(list(widgets))
        columns, rows, partitioning, widget_sizes, widget_margins = self.__process_partitioning(partitioning, size)

        y = 0
        for i_row, row in enumerate(partitioning):
            x = 0
            for i_column, widget in enumerate(row):
                widget_margin = widget_margins[widget]
                new_size = viwid.Size(columns[i_column], rows[i_row])
                new_position = viwid.Point(x, y)
                widget_computed_size = viwid.Size(min(widget_sizes[widget].width, new_size.width),
                                                  min(widget_sizes[widget].height, new_size.height))

                if widget.is_visible and widget.vertical_alignment not in (viwid.Alignment.FILL,
                                                                           viwid.Alignment.FILL_EXPANDING):
                    if widget.vertical_alignment == viwid.Alignment.CENTER:
                        new_position = new_position.moved_by(y=int((new_size.height - widget_computed_size.height) / 2))
                    elif widget.vertical_alignment == viwid.Alignment.END:
                        new_position = new_position.moved_by(y=new_size.height-widget_computed_size.height)
                    new_size = new_size.with_height(widget_computed_size.height)

                if widget.is_visible and widget.horizontal_alignment not in (viwid.Alignment.FILL,
                                                                             viwid.Alignment.FILL_EXPANDING):
                    if widget.horizontal_alignment == viwid.Alignment.CENTER:
                        new_position = new_position.moved_by(x=int((new_size.width - widget_computed_size.width) / 2))
                    elif widget.horizontal_alignment == viwid.Alignment.END:
                        new_position = new_position.moved_by(x=new_size.width - widget_computed_size.width)
                    new_size = new_size.with_width(widget_computed_size.width)

                widget.align(position=new_position.moved_by(widget_margin.left, widget_margin.top),
                             size=new_size.shrunk_by(widget_margin.width, widget_margin.height),
                             forcefully_apply_resizing_for=forcefully_apply_resizing_for)

                x += columns[i_column]
            y += rows[i_row]

    def _stretch_from_partitioning(self, partitioning: TPartitioning) -> tuple[t.Sequence[bool], t.Sequence[bool]]:
        stretch_columns = [False for _ in partitioning[0]] if (len(partitioning) > 0) else []
        stretch_rows = [False for _ in partitioning]

        for i_row, row in enumerate(partitioning):
            for i_column, widget in enumerate(row):
                if widget.is_visible and widget.vertical_alignment == viwid.Alignment.FILL_EXPANDING:
                    stretch_rows[i_row] = True
                if widget.is_visible and widget.horizontal_alignment == viwid.Alignment.FILL_EXPANDING:
                    stretch_columns[i_column] = True

        return stretch_columns, stretch_rows

    def __process_partitioning(self, partitioning: TPartitioning, size: viwid.Size, minimal_height: bool|None = None):
        stretch_columns, stretch_rows = self._stretch_from_partitioning(partitioning)

        preferred_columns, computed_widths = GridLayout.__horizontally_process_partitioning(partitioning, False)
        if size.width >= sum(preferred_columns):
            columns = preferred_columns
        else:
            columns, _ = GridLayout.__horizontally_process_partitioning(partitioning, True)
            columns = GridLayout.__stretch_axis_minimals(preferred_columns, columns, size.width)
        columns = GridLayout.__finalize_axis(columns, stretch_columns, size.width)

        preferred_rows, computed_heights = GridLayout.__vertically_process_partitioning(partitioning, False, columns)
        if size.height >= sum(preferred_rows) and not minimal_height:
            rows = preferred_rows
        else:
            rows = preferred_rows
            if minimal_height is not False:
                rows, _ = GridLayout.__vertically_process_partitioning(partitioning, True, columns)
            if minimal_height is None:
                rows = GridLayout.__stretch_axis_minimals(preferred_rows, rows, size.height)
        if minimal_height is None:
            rows = GridLayout.__finalize_axis(rows, stretch_rows, size.height)

        return (columns, rows, partitioning,
                {widget: viwid.Size(width, computed_heights[widget]) for widget, width in computed_widths.items()},
                {widget: (widget.margin if widget.is_visible else viwid.Margin.NULL)
                 for widget in computed_widths.keys()})

    @staticmethod
    def __horizontally_process_partitioning(
            partitioning: TPartitioning, minimal: bool) -> tuple[list[int], dict["viwid.widgets.widget.Widget", int]]:
        columns = [0 for _ in partitioning[0]] if (len(partitioning) > 0) else []
        computed_widths = {}

        for i_row, row in enumerate(partitioning):
            for i_column, widget in enumerate(row):
                width = computed_widths[widget] = (widget.width_demand(minimal=minimal) + widget.margin.width) if widget.is_visible else 0
                columns[i_column] = max(columns[i_column], width)

        return columns, computed_widths

    @staticmethod
    def __vertically_process_partitioning(
            partitioning: TPartitioning, minimal: bool,
            columns: t.Sequence[int]) -> tuple[list[int], dict["viwid.widgets.widget.Widget", int]]:
        rows = [0 for _ in partitioning]
        computed_heights = {}

        for i_row, row in enumerate(partitioning):
            for i_column, widget in enumerate(row):
                height = computed_heights[widget] = (widget.height_demand(columns[i_column],
                                                                         minimal=minimal) + widget.margin.height) if widget.is_visible else 0
                rows[i_row] = max(rows[i_row], height)

        return rows, computed_heights

    @staticmethod
    def __stretch_axis_minimals(axis: t.Sequence[int], axis_minimal: t.Sequence[int],
                                target_size: int) -> t.Sequence[int]:
        axis = [max(x, axis_minimal[i]) for i, x in enumerate(axis)]  # so preferred size is never less than minimal
        preferred_additional_size = sum(axis) - sum(axis_minimal)
        free_size = target_size - sum(axis_minimal)

        stretched_axis = list(axis_minimal)

        while preferred_additional_size > 0 and free_size > 0:
            growing_indexes = [i for i in range(len(axis)) if axis[i] > axis_minimal[i]]
            additional_size_per_index = max(1, int(free_size / len(growing_indexes)))

            for i in growing_indexes:
                additional_size = min(additional_size_per_index, free_size, (axis[i] - axis_minimal[i]))
                stretched_axis[i] += additional_size
                free_size -= additional_size
                preferred_additional_size -= additional_size

        return stretched_axis

    @staticmethod
    def __finalize_axis(axis: t.Sequence[int], stretch_axis: t.Sequence[bool], target_size: int) -> t.Sequence[int]:
        axis = list(axis)
        free_size = target_size - sum(axis)
        stretch_cell_indexes = [i for i, x in enumerate(stretch_axis) if x]
        stretch_cell_count = len(stretch_cell_indexes)

        if stretch_cell_count > 0:
            while free_size > 0:
                additional_size_per_index = max(1, int(free_size / stretch_cell_count))

                for i in stretch_cell_indexes:
                    additional_size = min(additional_size_per_index, free_size)
                    axis[i] += additional_size
                    free_size -= additional_size

        if free_size < 0:
            for i in reversed(range(len(axis))):
                take_size = min(axis[i], -free_size)
                axis[i] -= take_size
                free_size += take_size
                if free_size == 0:
                    break

        return axis
