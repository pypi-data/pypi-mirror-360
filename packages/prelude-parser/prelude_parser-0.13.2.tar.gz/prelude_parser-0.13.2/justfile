@_default:
  just --list

@develop:
  uv run maturin develop --uv -E all

@install: && develop
  uv sync --frozen --all-extras

@lock:
  uv lock

@lint:
  echo cargo check
  just --justfile {{justfile()}} check
  echo cargo clippy
  just --justfile {{justfile()}} clippy
  echo cargo fmt
  just --justfile {{justfile()}} fmt
  echo ruff-check
  just --justfile {{justfile()}} ruff-check
  echo ruff-format
  just --justfile {{justfile()}} ruff-format
  echo mypy
  just --justfile {{justfile()}} mypy

@check:
  cargo check

@clippy:
  cargo clippy

@fmt:
  cargo fmt

@mypy:
  uv run mypy prelude_parser tests

@ruff-check:
  uv run ruff check prelude_parser tests

@ruff-format:
  uv run ruff format prelude_parser tests

@test *args="":
  uv run pytest {{args}}
