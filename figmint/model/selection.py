"""Selection state: which artist is currently selected.

Plain Python (no Qt) so it is easy to unit-test. The view observes it via ``on_change``.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any


class SelectionModel:
    """Tracks the currently-selected matplotlib artist (single selection for M2)."""

    def __init__(self, on_change: Callable[[Any | None], None] | None = None) -> None:
        self._current: Any | None = None
        self._on_change = on_change

    @property
    def current(self) -> Any | None:
        """The selected artist, or ``None``."""
        return self._current

    def select(self, artist: Any | None) -> None:
        """Select ``artist`` (or clear with ``None``); notify only on a real change."""
        if artist is self._current:
            return
        self._current = artist
        if self._on_change is not None:
            self._on_change(artist)

    def clear(self) -> None:
        """Clear the selection."""
        self.select(None)

    @property
    def has_selection(self) -> bool:
        return self._current is not None
