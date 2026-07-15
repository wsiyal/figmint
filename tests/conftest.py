"""Test configuration: run Qt headless and matplotlib non-interactively."""

from __future__ import annotations

import os

# Must be set before PySide6 / Qt is imported anywhere.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import matplotlib  # noqa: E402  (after env setup, intentionally)

matplotlib.use("Agg")
