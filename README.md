# figmint

**Direct-manipulation figure editor for matplotlib.** Open any matplotlib figure in a real
GUI, drag things where you want them, edit legends / markers / colors, drop in a
**zoom inset** by dragging a box, rearrange **subplots**, hit **Beautify** for a
publication look — then export a PNG/PDF/SVG *or* a clean standalone matplotlib script.
figmint never edits your source file.

```python
import matplotlib.pyplot as plt
from figmint import edit

fig, ax = plt.subplots()
ax.plot([1, 2, 3], [1, 4, 9], marker="o", label="data")
ax.legend()

edit(fig)   # opens the editor — blocks in scripts, non-blocking in Jupyter
```

> **Status: in active development (pre-release).** The design and full
> development→deployment plan live in [`IMPLEMENTATION_SPEC.md`](IMPLEMENTATION_SPEC.md).
> Not yet on PyPI.

## Why figmint

- **A real inset-zoom tool** — drag a region, get a magnified inset with connector lines.
- **Visual subplot/layout editing** — add, remove, rearrange panels; tune spacing.
- **One-click Beautify** — curated publication presets, tight layout, font harmonizing.
- **Non-intrusive** — your script is never modified; export plain matplotlib code instead.
- **Works in notebooks and scripts** — correct event-loop handling for both.
- **Modern UX** — dark/light theme, high-DPI aware, undo/redo everywhere.

## Install

```bash
# once released:
pip install figmint

# for now, from source:
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
