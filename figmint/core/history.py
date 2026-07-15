"""Undo/redo stack that drives the edit log."""

from __future__ import annotations

from collections.abc import Callable

from figmint.core.commands import Command
from figmint.core.editlog import EditLog


class CommandStack:
    """Execute commands with undo/redo, recording committed edits in an :class:`EditLog`.

    Args:
        editlog: The log to append committed commands to. A fresh one is created if
            omitted.
        limit: Maximum number of undoable commands to retain.
        on_change: Optional callback invoked after any push/undo/redo (e.g. to refresh
            the UI and update enabled/disabled menu items).
    """

    def __init__(
        self,
        *,
        limit: int = 100,
        on_change: Callable[[], None] | None = None,
    ) -> None:
        self._limit = limit
        self._on_change = on_change
        self._undo: list[Command] = []
        self._redo: list[Command] = []

    @property
    def can_undo(self) -> bool:
        return bool(self._undo)

    @property
    def can_redo(self) -> bool:
        return bool(self._redo)

    def push(self, command: Command) -> None:
        """Execute ``command`` and clear the redo stack."""
        command.do()
        self._undo.append(command)
        self._redo.clear()
        if len(self._undo) > self._limit:
            self._undo.pop(0)
        self._changed()

    def active_commands(self) -> list[Command]:
        """Return the currently-applied commands in order (undone edits excluded)."""
        return list(self._undo)

    def make_editlog(self) -> EditLog:
        """Build an :class:`EditLog` from the current active commands."""
        return EditLog(self.active_commands())

    def undo(self) -> None:
        if not self._undo:
            return
        command = self._undo.pop()
        command.undo()
        self._redo.append(command)
        self._changed()

    def redo(self) -> None:
        if not self._redo:
            return
        command = self._redo.pop()
        command.do()
        self._undo.append(command)
        self._changed()

    def _changed(self) -> None:
        if self._on_change is not None:
            self._on_change()
