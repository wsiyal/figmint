# figmint — Implementation Spec (authoritative)

> **This document supersedes** `MASTER_PLAN.md`, `MASTER_PROMPT.md`, `QUICK_START.md`,
> and `README_START_HERE.md`. Those earlier drafts contain a **factual error**
> (that Pylustrator is "abandoned / 12+ months no updates"). It is not — see
> §1. Build from this file.

**Library name:** `figmint` · install `pip install figmint` · API `from figmint import edit`
Short, no underscore, "fig" + "mint condition" (publication-ready). Verified free on
PyPI (2026-07-16). Fallbacks if ever needed: `figly`, `figpad`, `plotpad`, `figdeck`.

---

## 1. Honest positioning (corrected)

The earlier plan was built on a false claim. The real landscape:

| Tool | Status (verified 2026-07-16) | What it already does | What it lacks |
|------|------------------------------|----------------------|---------------|
| **Pylustrator** 1.3.0 | Last **PyPI release Feb 2023** (~3 yrs, stale but not "dead"). Docs rebuilt 2025. | Drag/resize subplots, drag text/labels, add text & annotations, **generates plain matplotlib code**, saves back into your script. | No first-class inset-**zoom** tool; weak in-GUI editing of legend text / markers / colors; awkward in **Jupyter**; inserts code **into your source file** (messy diffs); no dark mode; performance on big figures. |
| **matplotlib built-in Qt editor** | Ships with matplotlib. | Toolbar "Customize → *Edit axis, curves and parameters*": titles, axis scales/limits, line color/style, marker. | No drag-to-move, no annotations, no inset zoom, no code export, no project save, single-artist only. |
| **matplotly / FigureForge / mpld3** | Varying maturity. | Notebook or web interactivity; some styling. | Not general-purpose desktop editors; limited artist coverage. |

**figmint's honest thesis:** *not* "replace a dead tool." It is: **the direct-manipulation
editor matplotlib's own Customize dialog should have been** — with the three things
researchers actually keep asking for and no existing tool does well together:

1. **A real inset-zoom tool** (drag a box on the data → get a magnified inset with connector lines).
2. **Subplot layout editing** (add/remove/rearrange panels, tune spacing) done visually.
3. **One-click "beautify"** publication presets — and **non-intrusive** output (never edits your source; exports a clean standalone script or a project file).

Everything else (drag, property panel, annotations, dark mode, notebook support) is table
stakes we must get *right*, not novel.

---

## 2. Scope: what is in v1 vs deferred

Keep v1 small enough to actually ship and be loved. **Resist the Haiku plan's kitchen sink.**

### v1 (MVP) — IN
- `edit(fig)` entry point; correct blocking (scripts) / non-blocking (notebook) behavior.
- Click-select any artist; drag to move (text, legend, annotations, whole subplots).
- Property panel for the artists researchers actually edit: **text/title/labels**, **line & marker**, **legend (incl. entry text & location)**, **axes (limits, scale, ticks, grid, spines)**.
- Annotations: text, arrow, rectangle, ellipse, line; LaTeX in text (`$...$`).
- **Inset-zoom tool** (§5.1) — the flagship.
- **Subplot layout editor** (§5.2) — add/remove panel, adjust margins/spacing/GridSpec.
- **Beautify presets** (§5.3) — 3–4 curated styles + tight-layout + font harmonize.
- Undo/redo (command stack).
- Export: PNG/PDF/SVG at chosen DPI; **generate standalone `.py`**; save/load **project** as JSON edit-log (§7).
- Dark/light theme; high-DPI aware.

### Deferred — explicitly OUT of v1 (say so; don't half-build)
- Multiple backends (Plotly/Bokeh). matplotlib only in v1. Keep a thin `Backend` seam but ship one.
- Full plugin marketplace / third-party plugin API. Ship internal extension points only.
- AI styling assistant.
- 3D (`mplot3d`) editing — allow the window to *open* on a 3D figure without crashing, but property editing of 3D artists is deferred.
- Data-analysis/statistics tools.

---

## 3. Architecture (lean, matplotlib-native)

**Do not reinvent matplotlib's artist tree.** The Haiku plan proposed a heavy
`FigureState`/`ArtistRegistry` mirror of the figure — avoid that; it drifts out of sync.
Instead keep a thin layer over the *live* figure.

```
figmint/
  __init__.py            # exports edit()
  api.py                 # edit(fig, block=None) -> Figure ; env detection
  app.py                 # QApplication bootstrap, high-DPI, theme install
  session.py             # ties one figure to one editor window; owns CommandStack

  model/
    selection.py         # current selection set; hit-testing over live artists
    commands.py          # Command base + concrete commands (see §6)
    history.py           # CommandStack (undo/redo, coalescing of drags)
    editlog.py           # ordered list of applied commands -> JSON (project + codegen)

  view/
    window.py            # QMainWindow: canvas + docks + menus + toolbar
    canvas.py            # FigureCanvasQTAgg subclass; event wiring; blit overlay
    overlay.py           # selection handles / rubber-band drawn via blit (§4)
    theme.py             # dark/light qss + matplotlib rcParams sync

  panels/
    properties.py        # context-sensitive property editor (dispatch by artist type)
    editors/             # one widget module per artist family (text, line, legend, axes, patch)
    layers.py            # tree view of figure -> axes -> artists (select from here too)

  tools/
    base.py              # Tool interface (activate, on_press/move/release)
    select.py            # default select+drag tool
    annotate.py          # text/arrow/rect/ellipse/line placement tools
    inset_zoom.py        # §5.1 flagship
    subplots.py          # §5.2 layout edits

  style/
    presets.py           # §5.3 beautify presets (rcParams bundles + layout ops)

  io/
    export_image.py      # savefig wrapper (PNG/PDF/SVG/DPI/transparent)
    codegen.py           # editlog -> standalone .py
    project.py           # editlog + figure-provenance <-> .figmint JSON

  util/
    env.py               # notebook/IPython detection, event-loop integration
    geometry.py, log.py, qtcompat.py
```

**Pattern:** every user edit becomes a `Command` that (a) mutates the live matplotlib
artist and (b) is recorded in `editlog`. Undo/redo replays inverse/forward. Codegen and
project-save both derive from the same editlog — one source of truth, so "what you see",
"the generated script", and "the saved project" can never disagree.

---

## 4. Performance — the honest version

The Haiku plan promised "differential rendering / blitting so 10k-point edits stay fluid."
That oversells it. **Correct approach:**

- A **property change to plotted data generally requires a full Agg redraw** — matplotlib
  has no partial-artist repaint for arbitrary property edits. Do a debounced
  `canvas.draw_idle()`; don't pretend it's incremental.
- Use **blitting only for the interaction overlay**: cache the rendered figure as a
  background bitmap (`copy_from_bbox`) at drag-start, then blit just the selection
  handles / rubber-band / ghost while the mouse moves; do one real `draw_idle()` on
  release. This is what keeps *dragging* smooth, and it's true.
- For genuinely heavy figures, offer **"fast drag" mode**: hide the dragged artist's full
  redraw and move only a lightweight bounding-box ghost until release.
- Coalesce rapid drag commands into a single undo entry (`history` coalescing window).

State this accurately in docs. Don't claim incremental rendering we don't have.

---

## 5. The three differentiating features (specify carefully)

### 5.1 Inset-zoom tool (flagship)
Goal: reproduce matplotlib's `zoom_inset_axes` gallery example, but by direct manipulation.

Interaction:
1. User picks the **Zoom Inset** tool, then drags a rectangle over the data region of a parent `Axes`.
2. figmint creates `axins = parent.inset_axes([x,y,w,h])` placed in a sensible empty corner (user can then drag/resize it).
3. Replays the parent's plotted lines/collections into `axins` (share data, not re-fetch).
4. Sets `axins` x/y-lim to the dragged region; calls `parent.indicate_inset_zoom(axins, edgecolor=...)` to draw the box + connector lines.
5. All of it recorded as an `AddInsetZoomCommand` so it round-trips through undo, codegen, and project save.

Property-panel controls for a selected inset: source region (xlim/ylim spinboxes), inset
position/size, connector line style/color, corner visibility, border, "sync styles with parent" toggle.

Codegen must emit the real matplotlib calls (`inset_axes`, `indicate_inset_zoom`) so the
exported script reproduces it without figmint.

### 5.2 Subplot / layout editor
- **Add panel**: convert current layout to a `GridSpec`, append a row/col, add an `Axes`.
- **Remove panel**: `ax.remove()` + reflow.
- **Rearrange / resize**: drag subplot edges (like Pylustrator) → adjust `GridSpec` ratios or `subplots_adjust`. Snap to a light grid.
- **Spacing controls** in a panel: `wspace`, `hspace`, per-side margins, `constrained_layout`/`tight_layout` toggle.
- Editing must survive round-trip: represent as commands that regenerate the layout deterministically (prefer `GridSpec` + explicit `set_position`) rather than opaque pixel nudges.

### 5.3 Beautify presets
A **Beautify** menu/dock applying a bundle of `rcParams` + layout ops in one undoable command:
- 3–4 curated presets, e.g. **"Publication (serif)"**, **"IEEE/compact"**, **"Slide (large fonts)"**, **"Minimal"**. Each sets font family/sizes, line widths, spine/tick style, grid, color cycle, dpi.
- Plus one-shot actions: **Tight layout**, **Harmonize fonts** (make all text one family/size scale), **Apply color palette** (choose a categorical palette, recolor series in order).
- Presets are plain data (dict of rcParams + list of layout ops) in `style/presets.py` so they're easy to add and appear verbatim in generated code.

---

## 6. Commands (undo/redo + codegen source)

`Command` interface: `do()`, `undo()`, and `to_code(ctx) -> list[str]` (the matplotlib
lines it emits). Concrete v1 commands:

`SetProp` (generic artist property) · `MoveArtist` · `AddAnnotation` (text/arrow/shape) ·
`DeleteArtist` · `EditLegend` (entries/loc/frame) · `SetAxesLimits` · `SetScale` ·
`AddInsetZoom` · `AddSubplot` · `RemoveSubplot` · `SetLayout` · `ApplyBeautify`.

Every command carries enough state to invert itself and to serialize. `editlog` = ordered
committed commands; `codegen` walks it; `project` saves it.

---

## 7. Persistence — JSON edit-log, not pickled figures

The Haiku plan suggested pickling the figure into `.feproj`. **Avoid**: pickled matplotlib
figures are fragile across versions. Instead:

- **Project file `.figmint`** = JSON: `{figmint_version, mpl_version, provenance, editlog:[...]}`.
  `provenance` records how the base figure was obtained (see below). Loading replays the editlog.
- **Base-figure provenance:** since `edit(fig)` receives a live figure the user built in
  code, v1 project-reopen requires the user to re-run their script to reconstruct the base
  figure, then figmint replays the editlog on top. Document this clearly. (A future version
  can snapshot artist data into the project for standalone reopen.)
- **Codegen** produces a fully standalone `.py` that does not import figmint.

---

## 8. Notebook / blocking behavior (be precise)

- `edit(fig, block=None)`: if `block is None`, **auto-detect**.
- **Script / plain Python:** run a real Qt event loop and block until the window closes
  (like `plt.show()`), then return the (mutated) `fig`.
- **IPython / Jupyter:** do **not** call a blocking `app.exec()` that freezes the kernel.
  Integrate with the existing Qt event loop (`%gui qt` / matplotlib's Qt backend loop);
  show the window non-blocking and return immediately; edits apply to the live `fig`.
  Detect via `IPython.get_ipython()` and whether a Qt loop is already running.
- Never create a second `QApplication` if one exists; reuse `QApplication.instance()`.
- Restore the user's matplotlib backend/rcParams on close.

---

## 9. Tech stack & quality bar
- Python 3.10+; **PySide6** (Qt6, high-DPI, LGPL); matplotlib ≥3.8 (`FigureCanvasQTAgg`); numpy.
- Type hints throughout; docstrings on public API; `ruff` + `black`; `mypy` on `model/` and `io/`.
- Tests: `pytest` + `pytest-qt`. Priority coverage: `commands`, `history`, `codegen`
  (assert generated script re-runs and reproduces key props), `editlog` round-trip,
  `inset_zoom`/`subplots` commands. GUI smoke tests via `pytest-qt`.
- CI: lint + type + tests on Linux/Windows/macOS.

---

## 10. Milestones (realistic — no fake "12-week" precision)

Ordered, each independently demoable. Times are relative effort, not calendar promises.

- **M1 – Skeleton & window:** `edit(fig)` opens a window embedding the figure; correct
  script-vs-notebook loop; dark/light theme; toolbar/dock shells. Return `fig` on close.
- **M2 – Select, drag, properties, undo:** hit-test + selection overlay (blit); move text/
  legend/annotations; property panel for text/line/legend/axes; `CommandStack` undo/redo.
- **M3 – Annotations + export:** text/arrow/rect/ellipse/line tools (LaTeX text); PNG/PDF/SVG
  export with DPI; **codegen** to standalone `.py`; **project** save/load (editlog JSON).
- **M4 – Flagship features:** inset-zoom tool (§5.1); subplot/layout editor (§5.2);
  beautify presets (§5.3). Ensure all three round-trip through undo + codegen + project.
- **M5 – Polish & release:** performance (blit drag / fast-drag mode), high-DPI/multi-monitor
  passes, docs + examples (script + notebook), PyPI packaging, CI green. Tag v0.1.0.

Ship M1–M3 first as a usable tool; M4 is what makes it *loved*; M5 makes it trustworthy.

---

## 11. Acceptance criteria (v0.1.0)
- `from figmint import edit; edit(fig)` works in a plain script (blocks, returns fig) **and**
  in Jupyter (non-blocking, kernel stays alive).
- Select + drag works for text, legend, and annotations; property panel edits at least:
  font family/size/color/weight, line color/width/style, marker style/size, legend entry
  text + location, axes limits/scale/grid.
- Add text, arrow, rectangle, ellipse; LaTeX renders in text.
- **Inset-zoom**: drag a region → magnified inset with connector lines appears and is editable.
- **Subplots**: add and remove a panel; adjust spacing; layout persists through export.
- **Beautify**: applying a preset visibly restyles and is a single undo.
- Undo/redo covers every above action.
- Export PNG/PDF/SVG at chosen DPI; **generated `.py` re-runs without figmint and reproduces
  the edited figure**; `.figmint` project reload replays edits on a re-run base figure.
- Dark mode works across window and canvas; crisp on a 4K/hiDPI display.
- Never modifies the user's source file. Never hard-crashes the host process on editor errors.
- CI green (ruff, mypy on model/io, pytest incl. codegen round-trip) on 3 OSes.

---

## 12. Build prompt for Fable (paste this)

```
You are implementing `figmint`, a matplotlib figure editor. The COMPLETE, AUTHORITATIVE
spec is IMPLEMENTATION_SPEC.md in this repo — read it fully and follow it. Ignore
MASTER_PLAN.md / MASTER_PROMPT.md / QUICK_START.md / README_START_HERE.md; they are
superseded and contain a factual error (Pylustrator is not abandoned).

Non-negotiables:
- Name is `figmint`; API `from figmint import edit; edit(fig)`.
- Python 3.10+, PySide6, matplotlib>=3.8. Type hints + docstrings; ruff/black/mypy clean.
- Do NOT mirror matplotlib's artist tree in a parallel state object — operate on the live
  figure via Commands (§3, §6). Every edit is a Command recorded in an editlog; undo/redo,
  code generation, and project save/load ALL derive from that one editlog (§6, §7).
- Correct notebook-vs-script event-loop handling (§8). Reuse QApplication.instance().
- Performance claims must match §4: blit ONLY the interaction overlay; property edits use
  debounced draw_idle(); no fake "incremental rendering".
- Persist projects as a JSON edit-log (`.figmint`), never as a pickled figure (§7).
- Never modify the user's source file. Never crash the host process on an editor error.

Deliver in milestone order M1→M5 (§10). For each milestone produce runnable code + tests,
and a short demo script. Start with M1 (skeleton, window, edit() loop, theme) and the
Command/CommandStack/editlog foundation, then M2.

The three features that define success (build in M4, make each round-trip through undo,
codegen, and project): inset-zoom tool (§5.1), subplot/layout editor (§5.2), beautify
presets (§5.3). Codegen for these must emit real matplotlib (inset_axes,
indicate_inset_zoom, GridSpec, rcParams) so exported scripts run without figmint.

Meet every item in the Acceptance Criteria (§11) before tagging v0.1.0.
```

---

---

# Part B — Development → Deployment (the complete pipeline)

Part A above is the design. Part B makes this a full dev-to-release plan and wires in
GitHub (`github.com/wsiyal/figmint`) and PyPI. Everything here is concrete enough to
copy-paste. **Actual repo creation and pushes are done by the owner (@wsiyal) / Fable —
not auto-executed by this planning step.**

## 13. Repository & GitHub setup

**Repo:** `https://github.com/wsiyal/figmint` (public). One-time bootstrap:

```bash
# in F:\python_plot_editor  (already your working dir)
git init -b main
# add the files from §13–§16 below, then:
git add .
git commit -m "chore: project scaffold, packaging, CI"
git remote add origin https://github.com/wsiyal/figmint.git
git push -u origin main
```

**Files that must live at repo root:**

- `LICENSE` — **MIT** recommended (permissive, researcher-friendly, max adoption).
  Note: PySide6 is **LGPL** and matplotlib is BSD-style. figmint only *imports* PySide6
  (dynamic linking), so figmint itself can be MIT with no conflict. Add a one-line
  "Third-party licenses" note in the README.
- `README.md` — hero example (the 3-line `edit(fig)`), a GIF of the inset-zoom tool,
  install, feature list, links to docs. Badges: PyPI version, CI status, Python versions, license.
- `.gitignore` — Python + Qt + build artifacts:
  ```
  __pycache__/ *.py[cod] .venv/ venv/ build/ dist/ *.egg-info/
  .pytest_cache/ .mypy_cache/ .ruff_cache/ htmlcov/ .coverage
  site/ .DS_Store *.figmint  # sample project files
  ```
- `CONTRIBUTING.md` — dev setup (`pip install -e ".[dev]"`), how to run tests/lint, PR rules.
- `CHANGELOG.md` — Keep a Changelog format; updated every release.
- `.github/ISSUE_TEMPLATE/` (bug_report.md, feature_request.md) + `pull_request_template.md`.
- `.github/workflows/` — see §14.
- `CODE_OF_CONDUCT.md` — Contributor Covenant (community goodwill; you asked for "loved by all").

**Branch & workflow:** trunk-based. Protect `main` (require CI green + 1 review even if
solo, via ruleset). Feature branches `feat/…`, `fix/…`. Conventional Commits so the
changelog and version bumps can be automated later.

## 14. CI/CD (GitHub Actions — concrete)

**`.github/workflows/ci.yml`** — lint, type, test on every push/PR across 3 OSes:

```yaml
name: CI
on: [push, pull_request]
jobs:
  test:
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python: ["3.10", "3.11", "3.12", "3.13"]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "${{ matrix.python }}" }
      - name: Install
        run: python -m pip install -e ".[dev]"
      - name: Lint & type
        run: |
          ruff check .
          ruff format --check .
          mypy figmint/model figmint/io
      - name: Test (headless Qt)
        uses: coactions/setup-xvfb@v1        # provides a virtual display on Linux
        with:
          run: pytest -q --cov=figmint --cov-report=xml
      # On Windows/macOS pytest-qt runs without xvfb; gate the xvfb step to Linux if needed.
```

> Qt GUI tests need a display. Use `xvfb` on Linux; set `QT_QPA_PLATFORM=offscreen` as a
> fallback for pure-logic Qt tests so headless runs never hang.

**`.github/workflows/release.yml`** — build + publish to PyPI on a version tag, using
**PyPI Trusted Publishing (OIDC)** — no API tokens stored:

```yaml
name: Release
on:
  push:
    tags: ["v*"]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: python -m pip install build
      - run: python -m build            # sdist + wheel into dist/
      - uses: actions/upload-artifact@v4
        with: { name: dist, path: dist/ }
  publish:
    needs: build
    runs-on: ubuntu-latest
    environment: pypi                    # add protection rules on this env in repo settings
    permissions:
      id-token: write                    # REQUIRED for trusted publishing
    steps:
      - uses: actions/download-artifact@v4
        with: { name: dist, path: dist/ }
      - uses: pypa/gh-action-pypi-publish@release/v1   # reads OIDC, no token needed
```

**One-time PyPI setup (owner action):** on PyPI, register the `figmint` project as a
*pending publisher* → repo `wsiyal/figmint`, workflow `release.yml`, environment `pypi`.
Do the same on **TestPyPI** first and dry-run with a `v0.0.x` tag before the real release.

## 15. Packaging — concrete `pyproject.toml`

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "figmint"
version = "0.1.0"                         # bump per release; or adopt hatch-vcs for git-tag versioning
description = "Direct-manipulation figure editor for matplotlib — edit, annotate, zoom-inset, beautify, export."
readme = "README.md"
requires-python = ">=3.10"
license = "MIT"
authors = [{ name = "wsiyal" }]
keywords = ["matplotlib", "figure", "editor", "gui", "plotting", "publication", "science"]
classifiers = [
  "Development Status :: 4 - Beta",
  "Intended Audience :: Science/Research",
  "Topic :: Scientific/Engineering :: Visualization",
  "License :: OSI Approved :: MIT License",
  "Programming Language :: Python :: 3.10",
  "Programming Language :: Python :: 3.11",
  "Programming Language :: Python :: 3.12",
  "Programming Language :: Python :: 3.13",
]
dependencies = [
  "matplotlib>=3.8",
  "PySide6>=6.6",
  "numpy>=1.24",
]

[project.optional-dependencies]
dev = ["pytest>=8", "pytest-qt>=4", "pytest-cov>=5", "ruff>=0.6", "mypy>=1.11", "build>=1.2"]
docs = ["mkdocs-material>=9.5", "mkdocstrings[python]>=0.25"]

[project.urls]
Homepage = "https://github.com/wsiyal/figmint"
Documentation = "https://wsiyal.github.io/figmint"
Issues = "https://github.com/wsiyal/figmint/issues"
Changelog = "https://github.com/wsiyal/figmint/blob/main/CHANGELOG.md"

[project.scripts]
figmint = "figmint.__main__:main"        # optional: `figmint demo` opens a sample figure

[tool.ruff]
line-length = 100
[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B"]
[tool.mypy]
python_version = "3.10"
warn_unused_ignores = true
```

Sanity gate before any tag: `python -m build` then `twine check dist/*` (or the publish
action's built-in check) so the PyPI long-description renders.

## 16. Documentation & hosting

- **mkdocs-material** + `mkdocstrings` for API docs; host on **GitHub Pages**.
- `.github/workflows/docs.yml`: on push to `main`, `pip install -e ".[docs]"`,
  `mkdocs gh-deploy --force`. Pages URL → `https://wsiyal.github.io/figmint`.
- Content: Quickstart (the 3-line example), a page per flagship feature (inset zoom,
  subplots, beautify) each with a screenshot/GIF, "Notebook vs script" guide, API reference,
  "How code export & project files work" (the editlog story), FAQ.
- Record 2–3 short GIFs (drag-edit, inset-zoom, beautify) — for a *visual* tool these do
  more for adoption than any prose. Put the inset-zoom GIF at the top of the README.

## 17. Versioning & release process

- **SemVer.** v0.x while API may shift; commit to stability at v1.0.0.
- Release steps (per version):
  1. Green CI on `main`.
  2. Update `CHANGELOG.md`; bump `version` in `pyproject.toml` (or rely on `hatch-vcs`).
  3. `git tag vX.Y.Z && git push origin vX.Y.Z` → `release.yml` builds + publishes.
  4. First ever release: tag `v0.0.1` against **TestPyPI** to validate the whole pipeline,
     then `v0.1.0` to real PyPI.
  5. Create a GitHub Release from the tag with the changelog notes.
- Announce v0.1.0 where researchers are: matplotlib Discourse, r/Python, r/datascience,
  relevant Discord/Zulip. Lead with the inset-zoom GIF and "no source-file edits, exports
  plain matplotlib."

## 18. Definition of Done (whole project, dev→deploy)

On top of §11 (feature acceptance):
- [ ] `pip install figmint` works from PyPI on Windows/macOS/Linux, Python 3.10–3.13.
- [ ] CI (lint + mypy + tests incl. codegen round-trip) green on all three OSes.
- [ ] Docs live at `wsiyal.github.io/figmint` with the three feature GIFs.
- [ ] README badges (PyPI, CI, license, Python) all green.
- [ ] `release.yml` has published at least once via trusted publishing (no stored tokens).
- [ ] LICENSE (MIT) + third-party-license note present; `twine check` passes.
- [ ] CHANGELOG started; v0.1.0 GitHub Release created from the tag.

## 19. End-to-end order of operations (single glance)

```
Scaffold repo (§13) ─► pyproject + tooling (§15) ─► CI green (§14)
   └─► Build library M1→M5 (§10, the actual editor code — Fable's main job)
          └─► Docs site (§16) ─► TestPyPI dry-run tag v0.0.1 (§17)
                 └─► Real release v0.1.0 via trusted publishing (§14/§17)
                        └─► GitHub Release + announce (§17) ─► Done (§18)
```

Add to the Fable build prompt (§12): "Also produce the repo-ops files in §13–§16 —
LICENSE (MIT), README, .gitignore, pyproject.toml, `.github/workflows/{ci,release,docs}.yml`,
mkdocs config, issue/PR templates — so the package is publishable to `wsiyal/figmint` and
PyPI via trusted publishing, meeting the §18 Definition of Done."

---

*Prepared 2026-07-16 (Opus review). Part A corrects the DeepSeek→Haiku drafts (verified:
Pylustrator last PyPI release Feb 2023; matplotlib ships a built-in Qt "Customize" editor;
inset zoom = `inset_axes` + `indicate_inset_zoom`; `figmint` free on PyPI). Part B adds the
full development→deployment pipeline wired to github.com/wsiyal/figmint + PyPI.*
