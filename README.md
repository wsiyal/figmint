# figmint

[![CI](https://github.com/wsiyal/figmint/actions/workflows/ci.yml/badge.svg)](https://github.com/wsiyal/figmint/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue)

**Direct-manipulation figure editor for matplotlib.** Open any matplotlib figure in a real
GUI, click to select elements, edit their properties, drag text around, and export a
PNG/PDF/SVG *or* a clean standalone matplotlib script. figmint never edits your source file.

```python
import matplotlib.pyplot as plt
from figmint import edit

fig, ax = plt.subplots()
ax.plot([1, 2, 3], [1, 4, 9], marker="o", label="data")
ax.legend()

edit(fig)   # opens the editor — blocks in scripts, non-blocking in Jupyter
```

> **Status: early release (v0.1.0).** The core editor works today (see "Available now").
> The flagship tools — inset-zoom, subplot layout, and one-click Beautify — are on the
> near-term roadmap. Full design lives in [`IMPLEMENTATION_SPEC.md`](IMPLEMENTATION_SPEC.md).

## Available now (v0.1.0)

- **Click-to-select** any element (lines, text, title, labels, legend) with a highlight.
- **Property panel** — edit text (content, font size, color) and lines (width, style,
  marker, marker size, color); every change is **undoable**.
- **Drag** text annotations; **delete** elements; full **undo/redo**.
- **Export** — PNG/PDF/SVG at any DPI, a standalone matplotlib **`.py` script**, and a
  reloadable **`.figmint` project** file.
- **Non-intrusive** — your source file is never modified.
- **Works in scripts and Jupyter**; **dark/light** theme; high-DPI aware.

## On the roadmap

- **Inset-zoom tool** — drag a region, get a magnified inset with connector lines.
- **Visual subplot/layout editing** — add, remove, rearrange panels; tune spacing.
- **One-click Beautify** — curated publication presets, tight layout, font harmonizing.
- Annotation tools (arrows, shapes, LaTeX), richer legend/axes editing.

## Install

```bash
pip install figmint

# or from source:
git clone https://github.com/wsiyal/figmint
cd figmint
pip install -e ".[dev]"
```

## Documentation

Full docs: https://wsiyal.github.io/figmint (built from `docs/`).

## Development

```bash
pip install -e ".[dev]"
ruff check .        # lint
ruff format .       # format
mypy figmint        # type-check
pytest              # tests
```

See [`CONTRIBUTING.md`](CONTRIBUTING.md).

## License

[MIT](LICENSE). figmint dynamically imports **PySide6** (LGPL) and **matplotlib**
(BSD-style); those remain under their own licenses.
