"""Tests for artist reference / label resolution."""

from __future__ import annotations

from matplotlib.figure import Figure


def _ax():
    fig = Figure()
    return fig.add_subplot(111)


def test_line_ref_and_label() -> None:
    from figmint.model.artref import artist_ref, describe_artist

    ax = _ax()
    (line,) = ax.plot([0, 1], [0, 1], label="signal")
    assert artist_ref(line) == "ax.lines[0]"
    assert "signal" in describe_artist(line)


def test_title_ref() -> None:
    from figmint.model.artref import artist_ref, describe_artist

    ax = _ax()
    ax.set_title("Result")
    assert artist_ref(ax.title) == "ax.title"
    assert describe_artist(ax.title) == "Title"


def test_text_ref() -> None:
    from figmint.model.artref import artist_ref

    ax = _ax()
    txt = ax.text(0.5, 0.5, "note")
    assert artist_ref(txt) == "ax.texts[0]"


def test_unknown_artist_falls_back() -> None:
    from figmint.model.artref import artist_ref

    assert artist_ref(object()) == "artist"
