"""Resolve a live matplotlib artist to a stable code reference and a human label.

The code reference (e.g. ``"ax.lines[0]"``, ``"ax.title"``) is what the code generator
emits so exported scripts can reproduce edits. The label (e.g. ``"Line 1"``) is shown in
the UI. Both assume a single primary Axes bound to the name ``ax`` in generated code; the
first Axes of the figure is used. Fable can generalize to multiple axes later.
"""

from __future__ import annotations

from typing import Any


def _axes_of(artist: Any) -> Any | None:
    return getattr(artist, "axes", None)


def artist_ref(artist: Any) -> str:
    """Return a best-effort code expression referring to ``artist`` (rooted at ``ax``).

    Falls back to ``"artist"`` for shapes we don't have a stable path for.
    """
    ax = _axes_of(artist)
    if ax is not None:
        if artist is getattr(ax, "title", None):
            return "ax.title"
        if artist is getattr(ax, "xaxis", None) and hasattr(ax, "xaxis"):
            return "ax.xaxis"
        if artist is ax.get_xaxis().get_label():
            return "ax.xaxis.label"
        if artist is ax.get_yaxis().get_label():
            return "ax.yaxis.label"
        legend = ax.get_legend()
        if legend is not None and artist is legend:
            return "ax.get_legend()"
        for i, line in enumerate(ax.lines):
            if artist is line:
                return f"ax.lines[{i}]"
        for i, text in enumerate(ax.texts):
            if artist is text:
                return f"ax.texts[{i}]"
        for i, patch in enumerate(ax.patches):
            if artist is patch:
                return f"ax.patches[{i}]"
    return "artist"


def describe_artist(artist: Any) -> str:
    """Return a short human label for the selection/status bar."""
    ax = _axes_of(artist)
    cls = type(artist).__name__
    if ax is not None:
        if artist is getattr(ax, "title", None):
            return "Title"
        if artist is ax.get_xaxis().get_label():
            return "X label"
        if artist is ax.get_yaxis().get_label():
            return "Y label"
        legend = ax.get_legend()
        if legend is not None and artist is legend:
            return "Legend"
        for i, line in enumerate(ax.lines):
            if artist is line:
                label = line.get_label()
                if label and not label.startswith("_"):
                    return f"Line: {label}"
                return f"Line {i + 1}"
        for i, text in enumerate(ax.texts):
            if artist is text:
                return f"Text {i + 1}"
    return cls
