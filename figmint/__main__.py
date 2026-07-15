"""Command-line entry point: ``figmint demo`` opens a sample figure in the editor."""

from __future__ import annotations

import sys


def _demo() -> int:
    import matplotlib.pyplot as plt

    from figmint import edit

    fig, ax = plt.subplots()
    ax.plot([0, 1, 2, 3], [0, 1, 4, 9], marker="o", label="sample")
    ax.set_title("figmint demo")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.legend()
    edit(fig)
    return 0


def main(argv: list[str] | None = None) -> int:
    """Entry point for the ``figmint`` console script."""
    args = sys.argv[1:] if argv is None else argv
    if args and args[0] == "demo":
        return _demo()
    print("figmint — usage: figmint demo")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
