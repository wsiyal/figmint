"""QApplication bootstrap: reuse an existing app (notebook/host) or create one."""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication


def get_app() -> QApplication:
    """Return the running ``QApplication`` or create one.

    Never creates a second application (which would break a host app or a Jupyter
    ``%gui qt`` loop). High-DPI scaling is automatic on Qt6, so no extra attributes are
    needed here.
    """
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv[:1])
    return app
