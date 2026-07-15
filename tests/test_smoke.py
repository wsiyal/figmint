"""Smoke tests for the public surface."""

from __future__ import annotations

import inspect

import figmint


def test_version_is_exposed() -> None:
    assert isinstance(figmint.__version__, str)
    assert figmint.__version__


def test_edit_is_public_with_block_param() -> None:
    assert callable(figmint.edit)
    params = inspect.signature(figmint.edit).parameters
    assert "fig" in params
    assert "block" in params
