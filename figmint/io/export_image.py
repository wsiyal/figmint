"""Export a figure to PNG / PDF / SVG at a chosen DPI."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from matplotlib.figure import Figure

#: Extensions figmint offers in the export dialog.
SUPPORTED_FORMATS = (".png", ".pdf", ".svg")


def export_figure(
    fig: Figure,
    path: str | Path,
    *,
    dpi: int = 300,
    transparent: bool = False,
    tight: bool = True,
) -> Path:
    """Save ``fig`` to ``path``; the format is inferred from the file extension.

    Args:
        fig: The matplotlib figure to save.
        path: Destination path ending in ``.png``, ``.pdf``, or ``.svg``.
        dpi: Output resolution (raster formats). Common: 150, 300, 600, 1200.
        transparent: Transparent background (useful for PNG over slides/posters).
        tight: Trim surrounding whitespace with ``bbox_inches="tight"``.

    Returns:
        The path written.

    Raises:
        ValueError: If the extension is not one of :data:`SUPPORTED_FORMATS`.
    """
    dest = Path(path)
    suffix = dest.suffix.lower()
    if suffix not in SUPPORTED_FORMATS:
        raise ValueError(
            f"Unsupported export format {suffix!r}; expected one of {SUPPORTED_FORMATS}."
        )
    fig.savefig(
        dest,
        dpi=dpi,
        transparent=transparent,
        bbox_inches="tight" if tight else None,
    )
    return dest
