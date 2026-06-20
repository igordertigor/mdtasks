from datetime import datetime
import os
from pathlib import Path
from typing import Annotated
from rich.table import Table
import typer
import shutil
import frontmatter as fm
import re
import tempfile
import subprocess

from mdtasks import template
from mdtasks.schema import FrontMatter, TaskShort
from mdtasks.settings import settings
from mdtasks.task_id import find_by_id, get_new_id
from mdtasks import log

app = typer.Typer()


@app.command("ls")
def ls(context: Annotated[str, typer.Option(..., "--context", "-c")] = ":env:"):
    if context == ":env:":
        context = settings.default_context

    tasks = []
    for fname in (settings.root / "open").glob("*.md"):
        frontmatter = fm.load(fname)
        m = re.search(r"# (.*)", frontmatter.content)
        if m:
            title = m.group(1)
        else:
            title = id

        task = TaskShort(**{"title": title, **frontmatter})
        if context.lower() in {"any", "all"} or task.context.lower() == context.lower():
            tasks.append(task)

    tasks = sorted(tasks, key=lambda t: (-t.prio, t.id))
    table = Table()
    table.add_column("Project")
    table.add_column("Context")
    table.add_column("Id")
    table.add_column("Title")
    table.add_column("Prio")

    for task in tasks:
        table.add_row(
            task.project, task.context, str(task.id), task.title, str(task.prio)
        )

    log.message(table)


@app.command("add")
@app.command("new")
def new(
    slug: str,
    context: Annotated[str, typer.Option(..., "--context", "-c")] = ":env:",
    use_full_spec: bool = False,
):
    id = get_new_id()
    if context == ":env:":
        context = settings.default_context
    frontmatter = FrontMatter(
        project=settings.project, context=context, id=id, created_at=datetime.now()
    )
    base = template.render(frontmatter, use_full_spec=use_full_spec)
    dest = settings.root / f"open/{slug}.md"
    dest.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(suffix=".md") as fh:
        fh.write(base.encode())
        fh.flush()
        subprocess.run([os.getenv("EDITOR"), fh.name])
        result = Path(fh.name).read_text()
        if result != base:
            shutil.copy(fh.name, dest)
        else:
            raise typer.Exit(1)
    log.message(f"{id = } {dest}")


@app.command("edit")
def edit(id: int):
    path, _ = find_by_id(id)
    subprocess.run([os.getenv("EDITOR"), str(path)])


@app.command("set")
def set_value(
    id: int,
    prio: Annotated[int | None, typer.Option(..., "--prio", "--priority", "-p")] = None,
    blocked: Annotated[int | None, typer.Option(..., "--blocked", "--block", "-b")] = None,
):
    path, doc = find_by_id(id)
    frontmatter = FrontMatter(**doc.metadata)
    if prio:
        log.message(f"Setting prio {frontmatter.prio} -> {prio}")
        frontmatter.prio = prio
    elif blocked is not None:
        blockers = set(formatter.blocked_by)
        blockers.add(blocked)
        frontmatter.blocked_by = list(blockers)
    else:
        log.warning("Nothing to set")
        raise typer.Exit(3)

    path.write_text(template.render(frontmatter, doc.content))


@app.command("start")
def start(id: int):
    path, doc = find_by_id(id)
    frontmatter = FrontMatter(**doc.metadata)
    frontmatter.started_at = datetime.now()

    path.write_text(template.render(frontmatter, doc.content))


@app.command("show")
def show(id: int):
    path, _ = find_by_id(id)
    log.message(path.read_text())


@app.command("done")
def done(id: int):
    path, doc = find_by_id(id)
    frontmatter = FrontMatter(**doc.metadata)
    frontmatter.finished_at = datetime.now()

    new_path = settings.root / f"done/{path.name}"
    new_path.parent.mkdir(parents=True, exist_ok=True)
    new_path.write_text(template.render(frontmatter, doc.content))
    path.unlink()
    log.message(f"{path} -> {new_path}")


@app.command("close")
def close(id: int, reason: list[str]):
    path, doc = find_by_id(id)
    frontmatter = FrontMatter(**doc.metadata)
    frontmatter.finished_at = datetime.now()

    new_path = settings.root / f"closed/{path.name}"
    new_path.parent.mkdir(parents=True, exist_ok=True)
    new_path.write_text(
        template.render(frontmatter, "\n\n".join([doc.content, " ".join(reason)]))
    )
    path.unlink()
    log.message(f"{path} -> {new_path}")
