# Contributing to batch-background-remover

Thanks for wanting to peel some pixels. This repo is a plugin host: the
core does batch I/O, scheduling, and pipeline orchestration; every
matting algorithm lives in an **extension** under `src/bbr/extensions/`.

## Dev Setup

```powershell
git clone https://github.com/<you>/batch-background-remover
cd batch-background-remover
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
pytest -q
bbr plugins list
```

## Writing an Extension

1. Create `src/bbr/extensions/my_matting.py`.
2. Subclass `BaseExtension` from `bbr.contracts.extension`.
3. Declare `name`, `api_version = "1"`, and `capabilities`.
4. Implement `process(frame: Frame) -> Frame`.
5. Register it in `pyproject.toml` under `[project.entry-points."bbr.plugins"]`.

Extensions must be pure with respect to the `Frame` they receive — do
not mutate the input. Return a new `Frame` with the alpha channel filled.

## Style

- `ruff` and `black` are authoritative. `mypy --strict` on `src/bbr/core`.
- No global mutable state in the host. The registry is read-only after
  discovery.
- Log through `bbr.utils.logging.get_logger(__name__)`, never `print`.

## PR Checklist

- [ ] `pytest -q` passes.
- [ ] `ruff check src tests` clean.
- [ ] New extension has a fixture image in `tests/fixtures/`.
- [ ] Descriptor schema unchanged, or `api_version` bumped.
- [ ] No model weights committed.

## Commit Messages

Conventional Commits. Scope is the subsystem: `loader`, `registry`,
`pipeline`, `ext:grabcut`, `cli`.

```
feat(loader): enforce api_version range on discovery
fix(registry): dedupe extensions by canonical name
```