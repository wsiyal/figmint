"""Public entry point: :func:`edit`."""

from __future__ import annotations

from typing import TYPE_CHECKING

from figmint.app import get_app
from figmint.util.env import should_block
from figmint.view.window import EditorWindow

if TYPE_CHECKING:
    from matplotlib.figure import Figure


def edit(fig: Figure, block: bool | None = None) -> Figure:
    """Open the figmint editor for ``fig`` and return it once the window closes.

    In a plain script this blocks (like ``plt.show()``) until the window is closed. In a
    Jupyter/IPython session with a Qt event loop it returns immediately and edits apply to
    the live figure. Pass ``block=True``/``False`` to override the auto-detection.

    Args:
        fig: The matplotlib figure to edit.
        block: Force blocking (``True``) or non-blocking (``False``); ``None`` auto-detects.

    Returns:
        The same (edited) figure.
    """
    app = get_app()
    window = EditorWindow(fig)
    window.show()
    if should_block(block):
        app.exec()
    return fig
