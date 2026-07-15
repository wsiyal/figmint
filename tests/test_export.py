"""Tests for image export."""

from __future__ import annotations

import pytest
from matplotlib.figure import Figure

from figmint.io.export_image import export_figure


def _figure() -> Figure:
    fig = Figure()
    ax = fig.add_subplot(111)
    ax.plot([0, 1, 2], [0, 1, 4])
    return fig


@pytest.mark.parametrize("ext", [".png", ".pdf", ".svg"])
def test_export_writes_file(tmp_path, ext) -> None:
    out = tmp_path / f"figure{ext}"
    result = export_figure(_figure(), out, dpi=150)
    assert result == out
    assert out.exists()
    assert out.stat().st_size > 0


def test_export_rejects_unknown_extension(tmp_path) -> None:
    with pytest.raises(ValueError, match="Unsupported export format"):
        export_figure(_figure(), tmp_path / "figure.gif")
