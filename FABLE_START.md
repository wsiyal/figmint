# START HERE (for Fable)

You are implementing **figmint**, a direct-manipulation figure editor for matplotlib.
This file is your entry point. Everything you need is in this repo.

## 1. Read first (in order)
1. **`IMPLEMENTATION_SPEC.md`** — the authoritative spec. Part A = design/features/milestones;
   Part B = development→deployment. Read it fully.
2. This file — your working checklist.

Ignore any `MASTER_*.md` / `QUICK_START.md` / `README_START_HERE.md` if you ever see them
(they were superseded and contain a factual error). The spec is the source of truth.

## 2. Ground rules (non-negotiable — from the spec)
- Name is **figmint**; public API is exactly `from figmint import edit` / `edit(fig, block=None)`.
- Python 3.10+, **PySide6**, **matplotlib≥3.8**. Type hints + docstrings; `ruff`/`mypy` clean.
- **Operate on the live matplotlib figure via Commands** — do NOT build a parallel state mirror.
- **One editlog** drives undo/redo, code export, AND project save/load. Keep them consistent.
- **Never modify the user's source file.** Never crash the host process on an editor error.
- Correct **notebook-vs-script** event-loop handling (spec §8). Reuse `QApplication.instance()`.
- Persistence = **JSON editlog** (`.figmint`), never a pickled figure.
- Performance claims must match spec §4 (blit only the interaction overlay; debounced `draw_idle`).

## 3. What already exists (the scaffold)
- Packaging: `pyproject.toml` (hatchling, deps, ruff/mypy/pytest config).
- CI/CD: `.github/workflows/{ci,release,docs}.yml` (tests on 3 OS × Py 3.10–3.13; PyPI trusted
  publishing on tags; mkdocs → Pages).
- Docs: `mkdocs.yml` + `docs/index.md`. License (MIT), CHANGELOG, CONTRIBUTING, CoC, templates.
- **Placeholder package** `figmint/` (`__init__.py` with a stub `edit()`, `__main__.py`, `py.typed`)
  and `tests/test_smoke.py`. **Replace the placeholder `edit()` and expand tests as you build.**
  Keep `__version__` and the `edit` signature stable.

Verify locally before you start:
```bash
pip install -e ".[dev]"
ruff check . && mypy figmint && pytest
```

## 4. Build order — milestones (spec §10). Tick as you go.
- [ ] **M1 Skeleton:** `edit(fig)` opens a PySide6 window embedding the figure; correct
      script-vs-notebook loop; dark/light theme; Command / CommandStack / editlog foundation.
      Returns `fig` on close.
- [ ] **M2 Select + edit:** hit-test + selection overlay (blit); drag-move text/legend/annotations;
      property panel for text/line/legend/axes; undo/redo.
- [ ] **M3 Annotations + export:** text/arrow/rect/ellipse/line tools (LaTeX text); PNG/PDF/SVG
      export with DPI; **codegen** to standalone `.py`; **project** save/load (`.figmint` JSON).
- [ ] **M4 Flagship (this is what makes figmint loved):**
      - [ ] Inset-zoom tool (spec §5.1) — drag region → `inset_axes` + `indicate_inset_zoom`.
      - [ ] Subplot/layout editor (spec §5.2).
      - [ ] Beautify presets (spec §5.3).
      Each must round-trip through undo + codegen + project.
- [ ] **M5 Polish & release:** perf pass, high-DPI/multi-monitor, docs + GIFs, PyPI + CI green,
      tag `v0.1.0` (TestPyPI dry-run first, spec §17).

Ship M1–M3 as a usable tool; M4 is the differentiator; M5 makes it trustworthy.

## 5. Definition of Done
Meet **spec §11** (feature acceptance) and **spec §18** (dev→deploy: pip-installable,
CI green on 3 OS, docs live, published via trusted publishing, `twine check` passes).

## 6. Workflow
- Branch per milestone (`feat/m1-skeleton`, …); open a PR; keep CI green.
- Conventional Commits; update `CHANGELOG.md` for user-facing changes.
- One-time owner setup still pending (not your job, but don't block on it):
  register `figmint` as a PyPI/TestPyPI trusted publisher (repo `wsiyal/figmint`,
  workflow `release.yml`, environment `pypi`); fill the `<your-contact-email>` in
  `CODE_OF_CONDUCT.md`.
