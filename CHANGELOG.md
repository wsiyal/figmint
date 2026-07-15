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

<!-- Fable: next milestones — M2 select/drag + property panel; M3 annotations;
     M4 inset zoom / subplots / beautify. -->
