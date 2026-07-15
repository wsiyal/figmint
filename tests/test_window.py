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


def test_select_updates_panel_and_enables_delete(qtbot) -> None:
    fig = _figure()
    win = EditorWindow(fig)
    qtbot.addWidget(win)
    line = fig.axes[0].lines[0]

    win.select(line)
    assert win.selection.current is line
    assert win._delete_act.isEnabled()
    assert win.panel._artist is line


def test_delete_selection_via_command(qtbot) -> None:
    fig = _figure()
    win = EditorWindow(fig)
    qtbot.addWidget(win)
    line = fig.axes[0].lines[0]

    win.select(line)
    win._on_delete()
    assert line.get_visible() is False
    assert not win.selection.has_selection
    assert win.stack.can_undo

    win.stack.undo()
    assert line.get_visible() is True


def test_hit_test_finds_line(qtbot) -> None:
    fig = _figure()
    win = EditorWindow(fig)
    qtbot.addWidget(win)
    win.canvas.draw()

    from matplotlib.backend_bases import MouseEvent

    ax = fig.axes[0]
    line = ax.lines[0]
    # A data point that lies on the plotted line ([0,1,2] -> [0,1,4]): (1, 1).
    px, py = ax.transData.transform((1, 1))
    event = MouseEvent("button_press_event", win.canvas, px, py, button=1)
    assert win.canvas.hit_test(event) is line
