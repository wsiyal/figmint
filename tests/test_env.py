"""Tests for environment detection."""

from __future__ import annotations

from figmint.util.env import in_notebook, should_block


def test_in_notebook_false_under_pytest() -> None:
    # The test runner is a plain Python process, not a Jupyter kernel.
    assert in_notebook() is False


def test_should_block_explicit_overrides() -> None:
    assert should_block(True) is True
    assert should_block(False) is False


def test_should_block_auto_blocks_in_script() -> None:
    # Auto-detect: not a notebook here, so it should block.
    assert should_block(None) is True
