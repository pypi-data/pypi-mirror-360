"""Functionality for widgets using the ``tklife.skel.SkeletonMixin`` to have rows
appended or removed from them dynamically."""

from __future__ import annotations

import tkinter
from functools import reduce
from typing import TYPE_CHECKING, Callable

from tklife.core import CachedWidget

if TYPE_CHECKING:
    from typing import Any, Iterable, Union

    from tklife.core import CreatedWidgetDict, SkelWidget


class AppendableMixin:
    """Mixin to allow for rows to be appended to and removed from a widget.

    Must appear after SkeletonMixin, but before the tkinter Widget.

    """

    created: CreatedWidgetDict
    _global_gridargs: dict[str, Any]
    _w_cache: dict[tuple[int, int], CachedWidget]
    _widget_create: Callable[[SkelWidget | None, int, int], tkinter.Widget | None]
    _grid_widget: Callable[[int, int, tkinter.Widget | None], None]

    @property
    def widget_cache(self) -> dict[tuple[int, int], CachedWidget]:
        """Stores the widgets created as well as grid cooridates and arguments.

        Returns:
            Widget cache

        """
        # Use the super's widget cache. This mixin is only used with SkeletonMixin, so
        # we can safely assume that the super has a widget_cache attribute.
        return super()._w_cache  # type: ignore

    def append_row(self, widget_row: Iterable[Union[SkelWidget, None]]) -> int:
        """Appends a row.

        Args:
            widget_row: A row of widgets to append

        Raises:
            TypeError: Raised when row is not iterable

        Returns:
            The new row index

        """
        # Find last row in cache and add 1 for new row
        max_row = -1
        for row, __ in self._w_cache:
            if row > max_row:
                max_row = row
        new_row = max_row + 1

        # Create the widgets in the row
        for col_index, skel_widget in enumerate(widget_row):
            if w := self._widget_create(skel_widget, new_row, col_index):
                self._grid_widget(
                    new_row,
                    col_index,
                    w,
                    **self._global_gridargs,
                    # Ignore the typing error because we have already checked for None
                    **skel_widget.grid_args,  # type: ignore
                )

        return new_row

    def insert_row_at(
        self, index: int, widget_row: Iterable[Union[SkelWidget, None]]
    ) -> int:
        """Inserts a row at the given index.

        Args:
            index: The index to insert the row at
            widget_row: The row to insert

        Raises:
            TypeError: Raised when widget_row is not iterable
            IndexError: Raised when index is out of range

        Returns:
            The new row index

        """
        if index == 1 + reduce(
            lambda carry, value: max(carry, value[0]), self.widget_cache.keys(), 0
        ):
            self.append_row(widget_row)
        else:
            i_row = iter(widget_row)
            for (row, col), (widget, grid_args) in tuple(self._w_cache.items()):
                if row < index:
                    continue
                if row == index:
                    # Make the insert
                    skel_widget = next(i_row)
                    if new_widget := self._widget_create(skel_widget, row, col):
                        self._grid_widget(
                            row,
                            col,
                            new_widget,
                            **self._global_gridargs,
                            # Ignore the typing error because we have already checked
                            # for None (This check was done in __widget_create)
                            **skel_widget.grid_args,  # type: ignore
                        )
                    else:
                        self._w_cache[row, col] = CachedWidget(None, None)
                    if widget is not None:
                        self._grid_widget(
                            row + 1, col, widget, **grid_args if grid_args else {}
                        )
                    else:
                        self._w_cache[row + 1, col] = CachedWidget(None, None)
                else:
                    # Shift row
                    if (widget, grid_args) != (None, None):
                        self._grid_widget(
                            row + 1, col, widget, **grid_args
                        )  # type: ignore
                    else:
                        self._w_cache[row + 1, col] = CachedWidget(None, None)
        return index

    def destroy_row(self, row_index: int) -> None:
        """Destroys the row at given index.

        Args:
            row_index: The row index to destroy

        """
        for (row, col), (widget, grid_args) in tuple(self._w_cache.items()):
            if row == row_index:
                if widget in (c.widget for c in self.created.values()):
                    ind = [k for k, v in self.created.items() if v.widget == widget][0]
                    del self.created[ind]
                if widget is not None:
                    widget.destroy()
                del self._w_cache[row, col]
            elif row > row_index:
                w = self._w_cache[row, col]
                del self._w_cache[row, col]
                self._w_cache[row - 1, col] = w
        for (row, col), (widget, grid_args) in self._w_cache.items():
            if widget is not None and grid_args is not None:
                widget.grid(row=row, column=col, **grid_args)

    def find_row_of(self, label: str) -> Union[int, None]:
        """Finds a row of a widget having label as defined in SkelWidget.

        Args:
            label: The label of the widget to find

        Returns:
            The row index containing the given widget or None if not found

        """
        try:
            widget = self.created[label].widget
        except KeyError:
            return None
        for (row, __), cached in self.widget_cache.items():
            if widget == cached.widget:
                return row
        return None  # pragma: no cover
