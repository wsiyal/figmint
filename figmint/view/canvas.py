"""The matplotlib canvas embedded in the editor window.

Thin wrapper over ``FigureCanvasQTAgg`` so we have one place to add event wiring and,
later, the blit-based selection overlay (spec §4). M1 keeps it minimal.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg

if TYPE_CHECKING:
    from matplotlib.figure import Figure


class FigmintCanvas(FigureCanvasQTAgg):
    """Canvas that renders the user's figure inside Qt."""

    def __init__(self, figure: Figure) -> None:
        super().__init__(figure)
        self.figure = figure

    def refresh(self) -> None:
        """Request a non-blocking redraw after the figure changed."""
        self.draw_idle()
