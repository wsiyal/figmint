"""Command-line entry point for figmint (``figmint`` console script).

PLACEHOLDER. Fable implements per IMPLEMENTATION_SPEC.md — e.g. ``figmint demo`` should
open a sample figure in the editor.
"""

from __future__ import annotations

import sys


def main(argv: list[str] | None = None) -> int:
    """Entry point for the ``figmint`` console script."""
    args = sys.argv[1:] if argv is None else argv
    print("figmint CLI is not implemented yet. See IMPLEMENTATION_SPEC.md.")
    print(f"(received args: {args})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
