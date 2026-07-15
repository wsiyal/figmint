"""Tests for the undo/redo command stack."""

from __future__ import annotations

from matplotlib.figure import Figure

from figmint.core.commands import SetArtistPropCommand
from figmint.core.history import CommandStack


def _line():
    fig = Figure()
    ax = fig.add_subplot(111)
    (line,) = ax.plot([0, 1, 2], [0, 1, 4])
    return line


def test_push_applies_and_enables_undo() -> None:
    line = _line()
    stack = CommandStack()
    assert not stack.can_undo

    stack.push(SetArtistPropCommand(line, "linewidth", 5.0, "ln"))
    assert line.get_linewidth() == 5.0
    assert stack.can_undo
    assert not stack.can_redo


def test_undo_redo_cycle() -> None:
    line = _line()
    original = line.get_linewidth()
    stack = CommandStack()
    stack.push(SetArtistPropCommand(line, "linewidth", 5.0, "ln"))

    stack.undo()
    assert line.get_linewidth() == original
    assert stack.can_redo

    stack.redo()
    assert line.get_linewidth() == 5.0


def test_push_clears_redo() -> None:
    line = _line()
    stack = CommandStack()
    stack.push(SetArtistPropCommand(line, "linewidth", 5.0, "ln"))
    stack.undo()
    assert stack.can_redo
    stack.push(SetArtistPropCommand(line, "linewidth", 2.0, "ln"))
    assert not stack.can_redo


def test_active_commands_excludes_undone() -> None:
    line = _line()
    stack = CommandStack()
    stack.push(SetArtistPropCommand(line, "linewidth", 5.0, "ln"))
    stack.push(SetArtistPropCommand(line, "alpha", 0.5, "ln"))
    assert len(stack.active_commands()) == 2
    stack.undo()
    assert len(stack.active_commands()) == 1


def test_on_change_callback_fires() -> None:
    line = _line()
    calls = {"n": 0}

    def bump() -> None:
        calls["n"] += 1

    stack = CommandStack(on_change=bump)
    stack.push(SetArtistPropCommand(line, "linewidth", 5.0, "ln"))
    stack.undo()
    stack.redo()
    assert calls["n"] == 3
