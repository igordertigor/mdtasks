default:
  just --list

format:
  uv run ruff check --diff src/mdtasks
  uv run ruff check --select I --diff src/mdtasks
  uv run ruff format --target-version p311 --check --diff src/mdtasks

format-write:
  uv run ruff check --fix src/mdtasks
  uv run ruff check --select I --fix src/mdtasks
  uv run ruff format --target-version=py313 src/mdtasks

type:
  uv run mypy --explicit-package-bases src/mdtasks
