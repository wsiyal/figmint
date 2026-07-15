# Changelog

All notable changes to figmint are documented here.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning: [SemVer](https://semver.org).

## [Unreleased]
### Added
- Project scaffold: packaging (`pyproject.toml`), CI/release/docs workflows, license,
  docs skeleton, and smoke tests.
- Full design + development→deployment plan in `IMPLEMENTATION_SPEC.md`.
- **M1 editor foundation:**
  - `edit(fig, block=None)` opens a PySide6 window embedding the figure, with correct
    script (blocking) vs notebook (non-blocking) behavior; lazy Qt import so
    `import figmint` stays lightweight.
  - Command / CommandStack (undo-redo) / EditLog core — one edit log drives both code
    generation and project save.
  - Matplotlib canvas with pan/zoom toolbar; dark/light theme toggle.
  - Export: PNG/PDF/SVG (with DPI), standalone Python script, and `.figmint` project file.
  - `figmint demo` CLI opens a sample figure.
  - 26 tests (logic + headless Qt window smoke tests).

- **M2 interactive editing:**
  - Click-to-select any artist (line, text, title, labels, legend, patches) with a
    Qt-overlay selection highlight (never appears in exports).
  - Context-sensitive property panel (dock): edit text (string, font size, color) and
    line (width, style, marker, marker size, color) — every change is undoable.
  - Drag-to-move free text annotations; delete selected artist; all through the command
    stack so undo/redo and code export stay consistent.
  - Artist→code-reference resolver so generated scripts use real matplotlib paths
    (`ax.lines[0]`, `ax.title`, …).

<!-- Fable: next milestones — M3 annotations (text/arrow/shapes/LaTeX);
     M4 inset zoom / subplots / beautify. -->
