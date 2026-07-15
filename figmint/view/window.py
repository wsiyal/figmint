"""The figmint editor main window (M1).

Embeds the figure, provides a menu/toolbar, undo-redo wiring, theme switching, and
export (image / Python script / project). Interactive selection, property editing, and
the flagship tools (inset zoom, subplots, beautify) are added by later milestones on top
of this scaffold.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT
from matplotlib.figure import Figure
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QFileDialog, QMainWindow, QMessageBox

from figmint.core.history import CommandStack
from figmint.io.export_image import SUPPORTED_FORMATS, export_figure
from figmint.view.canvas import FigmintCanvas
from figmint.view.theme import Theme, stylesheet


class EditorWindow(QMainWindow):
    """Main editor window for a single matplotlib figure."""

    def __init__(self, figure: Figure, *, theme: Theme = "light") -> None:
        super().__init__()
        self._figure = figure
        self._theme: Theme = theme
        self.stack = CommandStack(on_change=self._on_stack_change)

        self.setWindowTitle("figmint")
        self.resize(900, 640)

        self.canvas = FigmintCanvas(figure)
        self.setCentralWidget(self.canvas)
        self.addToolBar(NavigationToolbar2QT(self.canvas, self))

        self._build_menus()
        self.statusBar().showMessage("Ready")
        self.apply_theme(theme)
        self._update_edit_actions()

    # ---- menu construction -------------------------------------------------
    def _build_menus(self) -> None:
        menubar = self.menuBar()

        file_menu = menubar.addMenu("&File")
        for label, ext in (("PNG", ".png"), ("PDF", ".pdf"), ("SVG", ".svg")):
            act = QAction(f"Export as {label}…", self)
            act.triggered.connect(lambda _=False, e=ext: self._export_image_dialog(e))
            file_menu.addAction(act)
        file_menu.addSeparator()
        code_act = QAction("Export Python script…", self)
        code_act.triggered.connect(self._export_code_dialog)
        file_menu.addAction(code_act)
        proj_act = QAction("Save project…", self)
        proj_act.triggered.connect(self._save_project_dialog)
        file_menu.addAction(proj_act)
        file_menu.addSeparator()
        quit_act = QAction("E&xit", self)
        quit_act.setShortcut(QKeySequence.StandardKey.Quit)
        quit_act.triggered.connect(self.close)
        file_menu.addAction(quit_act)

        edit_menu = menubar.addMenu("&Edit")
        self._undo_act = QAction("&Undo", self)
        self._undo_act.setShortcut(QKeySequence.StandardKey.Undo)
        self._undo_act.triggered.connect(self._on_undo)
        edit_menu.addAction(self._undo_act)
        self._redo_act = QAction("&Redo", self)
        self._redo_act.setShortcut(QKeySequence.StandardKey.Redo)
        self._redo_act.triggered.connect(self._on_redo)
        edit_menu.addAction(self._redo_act)

        view_menu = menubar.addMenu("&View")
        theme_act = QAction("Toggle dark/light theme", self)
        theme_act.triggered.connect(self.toggle_theme)
        view_menu.addAction(theme_act)

    # ---- theme -------------------------------------------------------------
    @property
    def theme(self) -> Theme:
        return self._theme

    def apply_theme(self, theme: Theme) -> None:
        """Apply ``theme`` to this window."""
        self._theme = theme
        self.setStyleSheet(stylesheet(theme))

    def toggle_theme(self) -> None:
        """Switch between dark and light."""
        self.apply_theme("dark" if self._theme == "light" else "light")

    # ---- undo/redo ---------------------------------------------------------
    def _on_undo(self) -> None:
        self.stack.undo()

    def _on_redo(self) -> None:
        self.stack.redo()

    def _on_stack_change(self) -> None:
        self.canvas.refresh()
        self._update_edit_actions()

    def _update_edit_actions(self) -> None:
        self._undo_act.setEnabled(self.stack.can_undo)
        self._redo_act.setEnabled(self.stack.can_redo)

    # ---- export (direct, dialog-free: used by tests and the dialogs) -------
    def export_image_to(self, path: str | Path, *, dpi: int = 300) -> Path:
        """Export the figure to an image file (format inferred from extension)."""
        return export_figure(self._figure, path, dpi=dpi)

    def export_code_to(self, path: str | Path) -> Path:
        """Write a standalone matplotlib script reproducing the current edits."""
        dest = Path(path)
        dest.write_text(self.stack.make_editlog().to_code(), encoding="utf-8")
        return dest

    def save_project_to(self, path: str | Path) -> Path:
        """Write the current edit log to a ``.figmint`` project file."""
        import figmint

        dest = Path(path)
        text = self.stack.make_editlog().to_project(
            mpl_version=matplotlib.__version__,
            figmint_version=figmint.__version__,
        )
        dest.write_text(text, encoding="utf-8")
        return dest

    # ---- export dialogs ----------------------------------------------------
    def _export_image_dialog(self, ext: str) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Export figure", f"figure{ext}", f"*{ext}")
        if not path:
            return
        try:
            self.export_image_to(path)
            self.statusBar().showMessage(f"Exported {path}")
        except (OSError, ValueError) as exc:  # pragma: no cover - UI error path
            QMessageBox.warning(self, "Export failed", str(exc))

    def _export_code_dialog(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Export script", "figure.py", "*.py")
        if not path:
            return
        self.export_code_to(path)
        self.statusBar().showMessage(f"Wrote {path}")

    def _save_project_dialog(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Save project", "figure.figmint", "*.figmint")
        if not path:
            return
        self.save_project_to(path)
        self.statusBar().showMessage(f"Saved {path}")


__all__ = ["EditorWindow", "SUPPORTED_FORMATS"]
