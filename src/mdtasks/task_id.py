from typing import Iterator

from pathlib import Path

import frontmatter as fm
import typer
from mdtasks.log import error
from mdtasks.schema import FrontMatter
from mdtasks.settings import settings

IGNORE = {".git", "__pycache__", "node_modules"}


def get_new_id() -> int:
    new_id = 1
    for doc in iter_all_tasks():
        frontmatter = FrontMatter(**doc.metadata)
        new_id = max(new_id, frontmatter.id + 1)
    return new_id


def find_by_id(id: int) -> tuple[Path, fm.Post]:
    for path in iter_all_task_files():
        doc = fm.load(path)
        frontmatter = FrontMatter(**doc.metadata)
        if frontmatter.id == id:
            return path, doc
    error(f"Could not find task with id {id}")
    raise typer.Exit(2)


def iter_all_task_files() -> Iterator[Path]:
    for path, dirs, files in settings.root.walk():
        dirs[:] = [d for d in dirs if d not in IGNORE]
        for fname in files:
            yield path / fname


def iter_all_tasks() -> Iterator[fm.Post]:
    for fname in iter_all_task_files():
        yield fm.load(fname)
