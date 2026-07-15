"""Commands: the unit of every edit.

A command mutates the live matplotlib figure and knows how to reverse itself
(:meth:`Command.undo`), describe itself for serialization (:meth:`Command.describe`),
and emit the matplotlib code that reproduces it (:meth:`Command.to_code`).

M1 ships a single generic command (:class:`SetArtistPropCommand`). Fable adds the rest
(move, add-annotation, inset-zoom, subplot, beautify) following this same interface.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class Command(ABC):
    """Base class for every reversible edit.

    Subclasses must implement :meth:`do`, :meth:`undo`, :meth:`describe`, and
    :meth:`to_code`. Keep enough state on the instance to invert the edit and to
    serialize it without touching live matplotlib objects.
    """

    #: Short, stable identifier used in the edit log / project file.
    kind: str = "command"

    @abstractmethod
    def do(self) -> None:
        """Apply the edit to the live figure."""

    @abstractmethod
    def undo(self) -> None:
        """Reverse the edit, restoring the previous state."""

    @abstractmethod
    def describe(self) -> dict[str, Any]:
        """Return a JSON-serializable record of this edit (for the project file)."""

    @abstractmethod
    def to_code(self) -> list[str]:
        """Return the matplotlib source lines that reproduce this edit."""


class SetArtistPropCommand(Command):
    """Set a single property on a matplotlib artist via ``set_<name>`` / ``get_<name>``.

    Args:
        artist: The matplotlib artist to modify.
        prop: Property name (e.g. ``"color"``, ``"linewidth"``, ``"fontsize"``).
        value: New value to apply.
        target_ref: Stable, human-readable reference to the artist for code/log
            (e.g. ``"ax.title"``). Used by :meth:`to_code` and :meth:`describe`.
    """

    kind = "set_prop"

    def __init__(self, artist: Any, prop: str, value: Any, target_ref: str = "artist") -> None:
        self._artist = artist
        self._prop = prop
        self._new = value
        self._target_ref = target_ref
        self._old: Any = self._get()

    def _get(self) -> Any:
        return getattr(self._artist, f"get_{self._prop}")()

    def _set(self, value: Any) -> None:
        getattr(self._artist, f"set_{self._prop}")(value)

    def do(self) -> None:
        self._set(self._new)

    def undo(self) -> None:
        self._set(self._old)

    def describe(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "target": self._target_ref,
            "prop": self._prop,
            "value": _to_jsonable(self._new),
        }

    def to_code(self) -> list[str]:
        return [f"{self._target_ref}.set_{self._prop}({self._new!r})"]


class MoveTextCommand(Command):
    """Move a text-like artist (title, label, annotation) to a new position.

    Works on any artist exposing ``get_position`` / ``set_position`` returning an
    ``(x, y)`` pair (matplotlib ``Text``). Positions are in the artist's own coordinates.
    """

    kind = "move_text"

    def __init__(
        self,
        artist: Any,
        new_pos: tuple[float, float],
        target_ref: str = "artist",
        old_pos: tuple[float, float] | None = None,
    ) -> None:
        self._artist = artist
        self._new = (float(new_pos[0]), float(new_pos[1]))
        # old_pos is passed explicitly after a live drag (current position == new).
        source = old_pos if old_pos is not None else artist.get_position()
        self._old = (float(source[0]), float(source[1]))
        self._target_ref = target_ref

    def do(self) -> None:
        self._artist.set_position(self._new)

    def undo(self) -> None:
        self._artist.set_position(self._old)

    def describe(self) -> dict[str, Any]:
        return {"kind": self.kind, "target": self._target_ref, "pos": list(self._new)}

    def to_code(self) -> list[str]:
        return [f"{self._target_ref}.set_position(({self._new[0]!r}, {self._new[1]!r}))"]


class DeleteArtistCommand(Command):
    """Remove an artist from its axes; undo re-adds it."""

    kind = "delete"

    def __init__(self, artist: Any, target_ref: str = "artist") -> None:
        self._artist = artist
        self._target_ref = target_ref

    def do(self) -> None:
        self._artist.set_visible(False)

    def undo(self) -> None:
        self._artist.set_visible(True)

    def describe(self) -> dict[str, Any]:
        return {"kind": self.kind, "target": self._target_ref}

    def to_code(self) -> list[str]:
        return [f"{self._target_ref}.set_visible(False)"]


def _to_jsonable(value: Any) -> Any:
    """Best-effort conversion of a matplotlib value to something JSON-serializable."""
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, (list, tuple)):
        return [_to_jsonable(v) for v in value]
    return str(value)
