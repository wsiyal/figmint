"""figmint — direct-manipulation figure editor for matplotlib.

Public API::

    import matplotlib.pyplot as plt
    from figmint import edit

    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [1, 4, 9])
    edit(fig)

M1 provides a working editor window (embedded figure, pan/zoom, dark/light theme, undo
stack, and export to PNG/PDF/SVG, Python script, and ``.figmint`` project). Interactive
selection/property editing and the flagship tools land in later milestones — see
``IMPLEMENTATION_SPEC.md``.

Importing :mod:`figmint` is lightweight: the Qt GUI is imported lazily inside
:func:`edit`, so ``import figmint`` does not pull in PySide6 until you open the editor.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from matplotlib.figure import Figure

__all__ = ["edit", "__version__"]
__version__ = "0.1.0"


def edit(fig: Figure, block: bool | None = None) -> Figure:
    """Open the figmint editor for ``fig`` and return it once the window closes.

    In a plain script this blocks (like ``plt.show()``) until the window is closed. In a
    Jupyter/IPython session with a Qt event loop it returns immediately. Pass
    ``block=True``/``False`` to override the auto-detection.

    Args:
        fig: The matplotlib figure to edit.
        block: Force blocking (``True``) or non-blocking (``False``); ``None`` auto-detects.

    Returns:
        The same (edited) figure.
    """
    from figmint.api import edit as _edit  # lazy: pulls in PySide6 only when opening

    return _edit(fig, block)
