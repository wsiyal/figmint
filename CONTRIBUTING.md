# Contributing to figmint

Thanks for helping make figure editing pleasant for researchers!

## Dev setup

```bash
git clone https://github.com/wsiyal/figmint
cd figmint
python -m venv .venv && . .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

## Before you push

```bash
ruff check .        # lint
ruff format .       # auto-format
mypy figmint        # type-check
pytest              # tests
```

CI runs the same on Windows, macOS, and Linux across Python 3.10–3.13. PRs must be green.

## Conventions

- **Conventional Commits** (`feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, `test:`).
- Branch names: `feat/…`, `fix/…`, `docs/…`.
- Type hints and docstrings (Google style) on public APIs.
- New behavior needs tests. Code generation changes must keep the "generated script
  re-runs and reproduces the figure" round-trip test passing.
- Architecture and scope decisions live in [`IMPLEMENTATION_SPEC.md`](IMPLEMENTATION_SPEC.md) —
  read it before large changes. Notably: operate on the live matplotlib figure via
  Commands; one editlog drives undo, code export, and project save.

## Reporting bugs / requesting features

Use the issue templates. For bugs, include OS, Python version, matplotlib & PySide6
versions, and a minimal reproducer.
