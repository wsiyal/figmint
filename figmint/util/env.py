"""Environment detection: are we in a Jupyter notebook, and should ``edit`` block?"""

from __future__ import annotations


def in_notebook() -> bool:
    """Return ``True`` when running inside a Jupyter/IPython kernel with a GUI loop.

    Detects the ZMQ-based interactive shell used by Jupyter (notebook/lab/qtconsole).
    A plain ``python`` script or a terminal IPython session returns ``False``.
    """
    try:
        from IPython import get_ipython
    except ModuleNotFoundError:
        return False

    shell = get_ipython()
    if shell is None:
        return False
    # ZMQInteractiveShell => Jupyter kernel; TerminalInteractiveShell => plain REPL.
    return type(shell).__name__ == "ZMQInteractiveShell"


def should_block(block: bool | None) -> bool:
    """Resolve the ``block`` argument of :func:`figmint.edit`.

    ``None`` means auto-detect: block in scripts, do not block in notebooks.
    """
    if block is not None:
        return block
    return not in_notebook()
