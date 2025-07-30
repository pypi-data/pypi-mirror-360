"""Contains behaviors for ui functionality."""

from __future__ import annotations

import abc
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Generator, Optional


__all__ = ["CommandHistory", "Command"]


class CommandHistory:
    """Saves command history for undo and redo."""

    history: list[Command]
    cursor: Optional[int]

    def __init__(self) -> None:
        """Initializes the tracking dict."""
        self.history: list[Command] = []
        # The cursor will be on the command to be undone or None if
        # all history is undone or history is empty
        self.cursor = None

    def add_history(self, command: Command) -> None:
        """Adds a command to the command chain and calls it's execute method."""
        self._clear_after_cursor()
        self.history.append(command)
        self.cursor = self.history.index(command)
        command.execute()

    def undo(self) -> Optional[int]:
        """Calls reverse on the previous command."""
        if self.cursor is None:
            return None
        command = self.history[self.cursor]
        command.reverse()
        new_cursor: Any = self.cursor - 1
        if new_cursor < 0:
            new_cursor = None
        self.cursor = new_cursor
        return self.cursor

    def redo(self) -> Optional[int]:
        """Calls execute on the next command."""
        if (
            self.cursor is None and len(self.history) == 0
        ) or self.cursor == self.history.index(self.history[-1]):
            return None
        if self.cursor is None and len(self.history) > 0:
            self.cursor = -1
        # Will never be None at this point
        self.cursor += 1  # type: ignore
        command = self.history[self.cursor]
        command.execute()
        return self.cursor

    def undo_all(self, until: Optional[int] = None) -> None:
        """Calls undo on all of the history."""
        for __ in self.history[until:]:
            self.undo()

    def reset(self) -> None:
        """Clears the history completely."""
        self.history.clear()
        self.cursor = None

    def _clear_after_cursor(self):
        """Clears the history after the cursor."""
        if self.cursor is None:
            self.history = []
            return
        self.history = self.history[: self.cursor + 1]

    def __len__(self) -> int:
        """Returns the number commands that can be reversed (undo) Useful for unsaved
        indicators and warnings."""
        return len(tuple(self.iter_history()))

    def iter_history(self) -> Generator[Command, None, None]:
        """Yields each item in history up to the cursor position Useful for displaying
        all changes."""
        for command in (
            self.history[: self.cursor + 1] if self.cursor is not None else []
        ):
            yield command


class Command(abc.ABC):
    """Abstract class for a command."""

    @abc.abstractmethod
    def execute(self) -> None:
        """Executes this command."""

    @abc.abstractmethod
    def reverse(self) -> None:
        """Reverses this command."""
