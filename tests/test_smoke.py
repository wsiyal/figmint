"""Smoke tests so CI/build are green from day one. Fable expands the suite per §9."""

from __future__ import annotations

import pytest

import figmint


def test_version_is_exposed() -> None:
    assert isinstance(figmint.__version__, str)
    assert figmint.__version__


def test_edit_is_public() -> None:
    assert callable(figmint.edit)


def test_edit_placeholder_raises() -> None:
    # Remove/replace this once figmint.edit is implemented.
    with pytest.raises(NotImplementedError):
        figmint.edit(object())  # type: ignore[arg-type]
