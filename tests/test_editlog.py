"""Tests for the edit log (code generation + project round-trip)."""

from __future__ import annotations

import json

import pytest
from matplotlib.figure import Figure

from figmint.core.commands import SetArtistPropCommand
from figmint.core.editlog import PROJECT_SCHEMA, EditLog
from figmint.core.history import CommandStack


def _line():
    fig = Figure()
    ax = fig.add_subplot(111)
    (line,) = ax.plot([0, 1, 2], [0, 1, 4])
    return line


def test_to_code_includes_header_and_commands() -> None:
    line = _line()
    log = EditLog([SetArtistPropCommand(line, "linewidth", 3.0, "ax.lines[0]")])
    code = log.to_code()
    assert "import matplotlib.pyplot as plt" in code
    assert "ax.lines[0].set_linewidth(3.0)" in code


def test_project_roundtrip() -> None:
    line = _line()
    log = EditLog([SetArtistPropCommand(line, "linewidth", 3.0, "ln")])
    text = log.to_project(mpl_version="3.11.0", figmint_version="0.1.0")
    doc = EditLog.load_project(text)
    assert doc["schema"] == PROJECT_SCHEMA
    assert doc["mpl_version"] == "3.11.0"
    assert doc["editlog"][0]["prop"] == "linewidth"


def test_load_project_rejects_bad_schema() -> None:
    bad = json.dumps({"schema": 999, "editlog": []})
    with pytest.raises(ValueError, match="schema"):
        EditLog.load_project(bad)


def test_editlog_from_stack_reflects_active_commands() -> None:
    line = _line()
    stack = CommandStack()
    stack.push(SetArtistPropCommand(line, "linewidth", 5.0, "ln"))
    stack.push(SetArtistPropCommand(line, "alpha", 0.5, "ln"))
    stack.undo()
    # Undone command must not appear in generated code.
    code = stack.make_editlog().to_code()
    assert "set_linewidth" in code
    assert "set_alpha" not in code
