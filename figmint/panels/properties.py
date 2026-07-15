"""Context-sensitive property editor for the selected artist.

Given a selected artist, the panel builds the relevant editors and turns every change into
an undoable :class:`SetArtistPropCommand` pushed onto the shared command stack. The
building is driven by small, declarative field specs so Fable can extend coverage (legend,
axes, patches, 3D) by adding specs rather than new widgets.
"""

from __future__ import annotations

from typing import Any

from matplotlib.lines import Line2D
from matplotlib.text import Text
from PySide6.QtWidgets import (
    QColorDialog,
    QComboBox,
    QDockWidget,
    QDoubleSpinBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QWidget,
)

from figmint.core.commands import SetArtistPropCommand
from figmint.core.history import CommandStack
from figmint.model.artref import artist_ref, describe_artist

_LINESTYLES = ["-", "--", "-.", ":", "None"]
_MARKERS = ["None", ".", "o", "v", "^", "s", "*", "+", "x", "D"]


class PropertyPanel(QDockWidget):
    """Dock widget that edits properties of the selected artist."""

    def __init__(self, stack: CommandStack) -> None:
        super().__init__("Properties")
        self._stack = stack
        self._artist: Any | None = None
        self._body = QWidget()
        self._form = QFormLayout(self._body)
        self.setWidget(self._body)
        self.set_target(None)

    # ---- public API --------------------------------------------------------
    def set_target(self, artist: Any | None) -> None:
        """Rebuild the panel to edit ``artist`` (or show an empty state)."""
        self._artist = artist
        self._clear()
        if artist is None:
            self._form.addRow(QLabel("No selection"))
            return
        self._form.addRow(QLabel(f"<b>{describe_artist(artist)}</b>"))
        if isinstance(artist, Text):
            self._build_text(artist)
        elif isinstance(artist, Line2D):
            self._build_line(artist)
        else:
            self._form.addRow(QLabel(type(artist).__name__))

    def edit_property(self, prop: str, value: Any) -> None:
        """Apply a property edit programmatically (also used by tests)."""
        if self._artist is None:
            return
        ref = artist_ref(self._artist)
        self._stack.push(SetArtistPropCommand(self._artist, prop, value, ref))

    # ---- builders ----------------------------------------------------------
    def _build_text(self, artist: Text) -> None:
        text_edit = QLineEdit(artist.get_text())
        text_edit.editingFinished.connect(lambda: self.edit_property("text", text_edit.text()))
        self._form.addRow("Text", text_edit)

        size = QDoubleSpinBox()
        size.setRange(1, 200)
        size.setValue(float(artist.get_fontsize()))
        size.valueChanged.connect(lambda v: self.edit_property("fontsize", v))
        self._form.addRow("Font size", size)

        self._add_color_row("Color", artist.get_color(), "color")

    def _build_line(self, artist: Line2D) -> None:
        width = QDoubleSpinBox()
        width.setRange(0, 50)
        width.setSingleStep(0.5)
        width.setValue(float(artist.get_linewidth()))
        width.valueChanged.connect(lambda v: self.edit_property("linewidth", v))
        self._form.addRow("Line width", width)

        style = QComboBox()
        style.addItems(_LINESTYLES)
        current = str(artist.get_linestyle())
        style.setCurrentText(current if current in _LINESTYLES else "-")
        style.currentTextChanged.connect(lambda v: self.edit_property("linestyle", v))
        self._form.addRow("Line style", style)

        marker = QComboBox()
        marker.addItems(_MARKERS)
        cur_marker = str(artist.get_marker())
        marker.setCurrentText(cur_marker if cur_marker in _MARKERS else "None")
        marker.currentTextChanged.connect(lambda v: self.edit_property("marker", v))
        self._form.addRow("Marker", marker)

        msize = QDoubleSpinBox()
        msize.setRange(0, 100)
        msize.setValue(float(artist.get_markersize()))
        msize.valueChanged.connect(lambda v: self.edit_property("markersize", v))
        self._form.addRow("Marker size", msize)

        self._add_color_row("Color", artist.get_color(), "color")

    def _add_color_row(self, label: str, current: Any, prop: str) -> None:
        button = QPushButton(str(current))

        def pick() -> None:
            color = QColorDialog.getColor()
            if color.isValid():
                hex_value = color.name()
                button.setText(hex_value)
                self.edit_property(prop, hex_value)

        button.clicked.connect(pick)
        self._form.addRow(label, button)

    # ---- internals ---------------------------------------------------------
    def _clear(self) -> None:
        while self._form.count():
            item = self._form.takeAt(0)
            if item is None:
                continue
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
