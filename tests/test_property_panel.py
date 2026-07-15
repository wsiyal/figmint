"""Tests for the property panel (headless Qt)."""

from __future__ import annotations

from matplotlib.figure import Figure

from figmint.core.history import CommandStack
from figmint.panels.properties import PropertyPanel


def _line():
    fig = Figure()
    ax = fig.add_subplot(111)
    (line,) = ax.plot([0, 1, 2], [0, 1, 4], label="d")
    return line


def test_panel_empty_state(qtbot) -> None:
    panel = PropertyPanel(CommandStack())
    qtbot.addWidget(panel)
    panel.set_target(None)  # should not raise


def test_panel_edit_pushes_undoable_command(qtbot) -> None:
    line = _line()
    stack = CommandStack()
    panel = PropertyPanel(stack)
    qtbot.addWidget(panel)

    panel.set_target(line)
    panel.edit_property("linewidth", 7.0)

    assert line.get_linewidth() == 7.0
    assert stack.can_undo

    stack.undo()
    assert line.get_linewidth() != 7.0


def test_panel_edit_without_target_is_noop(qtbot) -> None:
    stack = CommandStack()
    panel = PropertyPanel(stack)
    qtbot.addWidget(panel)
    panel.set_target(None)
    panel.edit_property("linewidth", 3.0)
    assert not stack.can_undo
