# figmint

**Direct-manipulation figure editor for matplotlib.**

Open any matplotlib figure in a GUI, drag things into place, edit legends / markers /
colors, add a zoom inset by dragging a box, rearrange subplots, and Beautify for
publication — then export an image or a clean standalone matplotlib script. figmint never
edits your source file.

```python
import matplotlib.pyplot as plt
from figmint import edit

fig, ax = plt.subplots()
ax.plot([1, 2, 3], [1, 4, 9], marker="o", label="data")
ax.legend()

edit(fig)
```

!!! note "Pre-release"
    figmint is in active development. See the full design and roadmap in
    `IMPLEMENTATION_SPEC.md` in the repository.

## Highlights

- Real inset-zoom tool (drag a region → magnified inset with connectors)
- Visual subplot / layout editing
- One-click Beautify presets for publication figures
- Non-intrusive: exports plain matplotlib code, never touches your script
- Works in scripts and Jupyter; dark/light theme; undo/redo everywhere
