"""Tests for commands (do/undo/describe/to_code)."""

from __future__ import annotations

from matplotlib.figure import Figure

from figmint.core.commands import SetArtistPropCommand


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
