"""Tests for the editor window (headless via pytest-qt / offscreen)."""

from __future__ import annotations

from matplotlib.figure import Figure

from figmint.core.commands import SetArtistPropCommand
from figmint.view.window import EditorWindow


def _figure() -> Figure:
    fig = Figure()
    ax = fig.add_subplot(111)
    ax.plot([0, 1, 2], [0, 1, 4], label="d")
    ax.set_title("t")
    ax.legend()
    return fig


def test_window_builds_and_embeds_canvas(qtbot) -> None:
    win = EditorWindow(_figure())
    qtbot.addWidget(win)
    assert win.canvas is not None
    assert win.canvas.figure is win._figure
    assert not win.stack.can_undo
    assert not win._undo_act.isEnabled()


def test_push_enables_undo_action(qtbot) -> None:
    fig = _figure()
    win = EditorWindow(fig)
    qtbot.addWidget(win)
    line = fig.axes[0].lines[0]
    win.stack.push(SetArtistPropCommand(line, "linewidth", 4.0, "ax.lines[0]"))
    assert win.stack.can_undo
    assert win._undo_act.isEnabled()


def test_theme_toggle(qtbot) -> None:
    win = EditorWindow(_figure())
    qtbot.addWidget(win)
    assert win.theme == "light"
    win.toggle_theme()
    assert win.theme == "dark"
    assert win.styleSheet()  # a stylesheet is applied


def test_export_image(qtbot, tmp_path) -> None:
    win = EditorWindow(_figure())
    qtbot.addWidget(win)
    out = win.export_image_to(tmp_path / "out.png", dpi=120)
    assert out.exists()


def test_export_code_and_project(qtbot, tmp_path) -> None:
    fig = _figure()
    win = EditorWindow(fig)
    qtbot.addWidget(win)
    line = fig.axes[0].lines[0]
    win.stack.push(SetArtistPropCommand(line, "linewidth", 4.0, "ax.lines[0]"))

    code = win.export_code_to(tmp_path / "out.py")
    assert "set_linewidth" in code.read_text(encoding="utf-8")

    proj = win.save_project_to(tmp_path / "out.figmint")
    assert '"schema": 1' in proj.read_text(encoding="utf-8")
