"""The matplotlib canvas embedded in the editor window.

Adds click-to-select (hit-testing over common artists), drag-to-move for free ``Text``
artists, and a selection highlight painted as a Qt overlay so it never appears in exports.
The blit-based fast-drag optimization (spec §4) is a later refinement; M2 uses
``draw_idle`` during drag, which is correct if not yet optimal.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.text import Text
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPen

if TYPE_CHECKING:
    from matplotlib.backend_bases import MouseEvent
    from matplotlib.figure import Figure


class FigmintCanvas(FigureCanvasQTAgg):
    """Canvas that renders the figure and handles selection + drag."""

    def __init__(self, figure: Figure) -> None:
        super().__init__(figure)
        self.figure = figure
        self._selected: Any | None = None
        #: Called with the hit artist (or ``None``) on a click.
        self.on_select: Callable[[Any | None], None] | None = None
        #: Called with (artist, old_pos, new_pos) when a drag finishes.
        self.on_move: Callable[[Any, tuple[float, float], tuple[float, float]], None] | None = None

        self._drag_artist: Any | None = None
        self._drag_start_pos: tuple[float, float] | None = None
        self._drag_offset: tuple[float, float] = (0.0, 0.0)

        self.mpl_connect("button_press_event", self._on_press)
        self.mpl_connect("motion_notify_event", self._on_motion)
        self.mpl_connect("button_release_event", self._on_release)

    # ---- selection ---------------------------------------------------------
    def set_selected(self, artist: Any | None) -> None:
        """Set the highlighted artist and repaint the overlay."""
        self._selected = artist
        self.update()

    def refresh(self) -> None:
        """Request a non-blocking redraw after the figure changed."""
        self.draw_idle()
        self.update()

    def hit_test(self, event: MouseEvent) -> Any | None:
        """Return the topmost interactive artist under ``event``, or ``None``."""
        ax = self.figure.axes[0] if self.figure.axes else None
        if ax is None:
            return None
        candidates: list[Any] = []
        legend = ax.get_legend()
        if legend is not None:
            candidates.append(legend)
        candidates += list(ax.texts)
        candidates += [ax.title, ax.xaxis.label, ax.yaxis.label]
        candidates += list(ax.lines)
        candidates += list(ax.patches)
        for artist in candidates:
            if artist is None or not artist.get_visible():
                continue
            try:
                hit, _ = artist.contains(event)
            except (TypeError, ValueError):
                continue
            if hit:
                return artist
        return None

    # ---- mouse handlers ----------------------------------------------------
    def _on_press(self, event: MouseEvent) -> None:
        if event.inaxes is None and event.xdata is None:
            artist = None
        else:
            artist = self.hit_test(event)
        if self.on_select is not None:
            self.on_select(artist)

        # Begin drag for a free text artist (in ax.texts) with left button.
        if (
            artist is not None
            and event.button == 1
            and isinstance(artist, Text)
            and self._is_free_text(artist)
            and event.xdata is not None
            and event.ydata is not None
        ):
            pos = artist.get_position()
            self._drag_artist = artist
            self._drag_start_pos = (float(pos[0]), float(pos[1]))
            self._drag_offset = (float(pos[0]) - event.xdata, float(pos[1]) - event.ydata)

    def _on_motion(self, event: MouseEvent) -> None:
        if self._drag_artist is None or event.xdata is None or event.ydata is None:
            return
        ox, oy = self._drag_offset
        self._drag_artist.set_position((event.xdata + ox, event.ydata + oy))
        self.draw_idle()
        self.update()

    def _on_release(self, event: MouseEvent) -> None:
        if self._drag_artist is None or self._drag_start_pos is None:
            return
        artist = self._drag_artist
        start = self._drag_start_pos
        fp = artist.get_position()
        final = (float(fp[0]), float(fp[1]))
        self._drag_artist = None
        self._drag_start_pos = None
        if final != start and self.on_move is not None:
            self.on_move(artist, start, final)

    def _is_free_text(self, artist: Text) -> bool:
        ax = getattr(artist, "axes", None)
        return ax is not None and artist in ax.texts

    # ---- selection overlay (Qt layer, never exported) ----------------------
    def paintEvent(self, event: Any) -> None:  # noqa: N802 (Qt override name)
        super().paintEvent(event)
        artist = self._selected
        if artist is None or not getattr(artist, "get_visible", lambda: True)():
            return
        try:
            bbox = artist.get_window_extent()
        except (RuntimeError, ValueError, TypeError):
            return
        ratio = self.device_pixel_ratio_or_one()
        # matplotlib bbox origin is bottom-left; Qt is top-left -> flip y.
        height = self.height()
        x0 = bbox.x0 / ratio
        x1 = bbox.x1 / ratio
        y_top = height - bbox.y1 / ratio
        painter = QPainter(self)
        pen = QPen(QColor("#2d7ff9"))
        pen.setWidth(2)
        pen.setStyle(Qt.PenStyle.DashLine)
        painter.setPen(pen)
        painter.drawRect(
            int(x0) - 3, int(y_top) - 3, int(x1 - x0) + 6, int(bbox.height / ratio) + 6
        )
        painter.end()

    def device_pixel_ratio_or_one(self) -> float:
        try:
            return float(self.devicePixelRatioF())
        except (AttributeError, TypeError):
            return 1.0
