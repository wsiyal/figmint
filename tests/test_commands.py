"""Tests for commands (do/undo/describe/to_code)."""

from __future__ import annotations

from matplotlib.figure import Figure

from figmint.core.commands import (
    DeleteArtistCommand,
    MoveTextCommand,
    SetArtistPropCommand,
)


def _line():
    fig = Figure()
    ax = fig.add_subplot(111)
    (line,) = ax.plot([0, 1, 2], [0, 1, 4])
    return line


def test_do_and_undo_roundtrip() -> None:
    line = _line()
    original = line.get_linewidth()
    cmd = SetArtistPropCommand(line, "linewidth", 6.0, "ax.lines[0]")

    cmd.do()
    assert line.get_linewidth() == 6.0

    cmd.undo()
    assert line.get_linewidth() == original


def test_describe_is_jsonable() -> None:
    line = _line()
    cmd = SetArtistPropCommand(line, "linewidth", 3.0, "ax.lines[0]")
    rec = cmd.describe()
    assert rec == {"kind": "set_prop", "target": "ax.lines[0]", "prop": "linewidth", "value": 3.0}


def test_to_code_emits_setter() -> None:
    line = _line()
    cmd = SetArtistPropCommand(line, "linewidth", 3.0, "ax.lines[0]")
    assert cmd.to_code() == ["ax.lines[0].set_linewidth(3.0)"]


def _text():
    fig = Figure()
    ax = fig.add_subplot(111)
    return ax.text(0.1, 0.2, "note")


def test_move_text_with_explicit_old_pos() -> None:
    txt = _text()
    # Simulate a live drag: the artist already moved, old passed explicitly.
    txt.set_position((0.7, 0.8))
    cmd = MoveTextCommand(txt, (0.7, 0.8), "ax.texts[0]", old_pos=(0.1, 0.2))
    cmd.undo()
    assert txt.get_position() == (0.1, 0.2)
    cmd.do()
    assert txt.get_position() == (0.7, 0.8)
    assert cmd.to_code() == ["ax.texts[0].set_position((0.7, 0.8))"]


def test_delete_toggles_visibility() -> None:
    line = _line()
    cmd = DeleteArtistCommand(line, "ax.lines[0]")
    cmd.do()
    assert line.get_visible() is False
    cmd.undo()
    assert line.get_visible() is True
    assert cmd.to_code() == ["ax.lines[0].set_visible(False)"]
