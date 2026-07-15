"""figmint — direct-manipulation figure editor for matplotlib.

PLACEHOLDER package. The real implementation is built by Fable per the repository's
``IMPLEMENTATION_SPEC.md`` (Part A design + Part B ops). Keep the public surface below
(``edit`` and ``__version__``) stable; replace the body.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from matplotlib.figure import Figure

__all__ = ["edit", "__version__"]
__version__ = "0.1.0"


def edit(fig: "Figure", block: Optional[bool] = None) -> "Figure":
    """Open the figure editor for ``fig`` and return it once the window closes.

    Args:
        fig: The matplotlib figure to edit.
        block: Force blocking (``True``) or non-blocking (``False``). When ``None``,
            auto-detect: block in scripts, non-blocking in Jupyter/IPython.

    Returns:
        The same (edited) figure.

    Note:
        Placeholder — not yet implemented. See ``IMPLEMENTATION_SPEC.md`` (§8, §10).
    """
    raise NotImplementedError(
        "figmint.edit is not implemented yet — see IMPLEMENTATION_SPEC.md (Fable builds this)."
    )
