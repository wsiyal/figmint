"""Tests for the selection model."""

from __future__ import annotations

from figmint.model.selection import SelectionModel


def test_select_and_clear_notifies() -> None:
    events: list[object] = []
    model = SelectionModel(on_change=events.append)

    model.select("a")
    assert model.current == "a"
    assert model.has_selection

    model.select("a")  # no change -> no new event
    model.clear()
    assert model.current is None
    assert not model.has_selection
    assert events == ["a", None]


def test_no_callback_is_fine() -> None:
    model = SelectionModel()
    model.select("x")
    assert model.current == "x"
