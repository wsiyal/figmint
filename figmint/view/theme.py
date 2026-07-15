"""Minimal dark/light theming for the editor window.

M1 provides two Qt stylesheets and a toggle. Fable can expand this (syncing matplotlib
rcParams, honoring the OS theme via ``QStyleHints.colorScheme``, etc.).
"""

from __future__ import annotations

from typing import Literal

Theme = Literal["light", "dark"]

_LIGHT_QSS = """
QMainWindow, QWidget { background: #f5f5f5; color: #1a1a1a; }
QMenuBar, QToolBar, QStatusBar { background: #ececec; color: #1a1a1a; }
QMenuBar::item:selected, QMenu::item:selected { background: #d0d0d0; }
QPushButton { background: #e0e0e0; border: 1px solid #b8b8b8; padding: 4px 8px; }
QPushButton:hover { background: #d5d5d5; }
"""

_DARK_QSS = """
QMainWindow, QWidget { background: #2b2b2b; color: #e6e6e6; }
QMenuBar, QToolBar, QStatusBar { background: #333333; color: #e6e6e6; }
QMenuBar::item:selected, QMenu::item:selected { background: #454545; }
QMenu { background: #333333; color: #e6e6e6; }
QPushButton { background: #3c3c3c; border: 1px solid #555; padding: 4px 8px; color: #e6e6e6; }
QPushButton:hover { background: #484848; }
"""


def stylesheet(theme: Theme) -> str:
    """Return the Qt stylesheet string for ``theme``."""
    return _DARK_QSS if theme == "dark" else _LIGHT_QSS
