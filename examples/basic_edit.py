"""Minimal figmint example: build a figure and open the editor.

Run with:  python examples/basic_edit.py
"""

import matplotlib.pyplot as plt

from figmint import edit


def main() -> None:
    fig, ax = plt.subplots()
    ax.plot([0, 1, 2, 3], [0, 1, 4, 9], marker="o", label="sample")
    ax.set_title("figmint basic example")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.legend()

    # Opens the editor window; blocks until you close it, then returns the figure.
    edit(fig)


if __name__ == "__main__":
    main()
