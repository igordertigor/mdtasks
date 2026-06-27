from typing import Annotated

import re
import shutil
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path

import frontmatter as fm
import typer
from mdtasks import log, template
from mdtasks.blocking import get_blockers
from mdtasks.editor import get_editor
from mdtasks.schema import FrontMatter, TaskShort
from mdtasks.settings import settings
from mdtasks.task_id import find_by_id, get_new_id
from rich.table import Table

app = typer.Typer()


@app.command("ls")
def ls(
    context: Annotated[
        list[str],
        typer.Option(
            ...,
            "--context",
            "-c",
            help=(
                "Apply to selected contexts only. Can be used multiple times "
                "to select multiple contexts. Will read from MDTASKS_DEFAULT_CONTEXT "
                "environment variable if not specified."
            ),
        ),
    ] = [],
    min_prio: Annotated[
        int,
        typer.Option(
            ...,
            "--min-prio",
            "--prio",
            "--priority",
            "-p",
            help=("Only show tickets with the specified priority or higher."),
        ),
    ] = 0,
    show_project: Annotated[
        bool, typer.Option(..., help="Include 'project' in the output table")
    ] = False,
):
    """Show open tickets with filtering options."""
    if not context:
        context = [settings.default_context]

    context_lower = [c.lower() for c in context]
    is_all_context = "any" in context_lower or "all" in context_lower

    tasks = []
    all_open_tasks = []
    for fname in (settings.root / "open").glob("*.md"):
        frontmatter = fm.load(fname)
        m = re.search(r"# (.*)", frontmatter.content)
        if m:
            title = m.group(1)
        else:
            title = id

        task = TaskShort(**{"title": title, **frontmatter})
        all_open_tasks.append(task)
        if is_all_context or task.context.lower() in context_lower:
            if task.prio >= min_prio:
                tasks.append(task)

    tasks = sorted(tasks, key=lambda t: (-t.prio, t.id))
    table = Table()
    if show_project:
        table.add_column("Project")
    table.add_column("Context")
    table.add_column("Id")
    table.add_column("Prio")
    table.add_column("Title")
    table.add_column("Blockers")

    for task in tasks:
        content = [
            task.context,
            str(task.id),
            str(task.prio),
            task.title,
            ", ".join(str(i) for i in get_blockers(task, all_open_tasks)),
        ]
        if show_project:
            content.insert(0, task.project)
        table.add_row(*content)

    log.message(table)


@app.command("add")
@app.command("new")
def new(
    slug: Annotated[str, typer.Argument(help="Brief slug of the ticket")],
    context: Annotated[
        str,
        typer.Option(
            ...,
            "--context",
            "-c",
            help=(
                "Initialize the ticket as belonging to the given context. "
                "Will read from MDTASKS_DEFAULT_CONTEXT environment variable if not specified."
            ),
        ),
    ] = ":env:",
    use_full_spec: Annotated[
        bool,
        typer.Option(
            ...,
            help=(
                "Show the full frontmatter specification instead of "
                "only the fields that are actually used."
            ),
        ),
    ] = False,
):
    """Create a new ticket."""
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
        if not fh.name:
            log.error("Failed to create named temp file")
            raise typer.Exit(3)
        fh.write(base.encode())
        fh.flush()
        subprocess.run([get_editor(), fh.name])
        result = Path(fh.name).read_text()
        if result != base:
            shutil.copy(fh.name, dest)
        else:
            raise typer.Exit(1)
    log.message(f"{id = } {dest}")


@app.command("edit")
def edit(id: Annotated[int, typer.Argument(..., help="ticket id")]):
    """Edit an existing ticket"""
    path, _ = find_by_id(id)
    subprocess.run([get_editor(), str(path)])


@app.command("set")
def set_value(
    id: Annotated[int, typer.Argument(..., help="ticket id")],
    prio: Annotated[
        int | None,
        typer.Option(
            ..., "--prio", "--priority", "-p", help="Update priority to this value."
        ),
    ] = None,
    blocked: Annotated[
        int | None,
        typer.Option(
            ...,
            "--blocked",
            "--block",
            "-b",
            help="Add a ticket id that blocks this ticket.",
        ),
    ] = None,
):
    """Selectively set meta data of a ticket"""
    path, doc = find_by_id(id)
    frontmatter = FrontMatter(**doc.metadata)
    if prio:
        log.message(f"Setting prio {frontmatter.prio} -> {prio}")
        frontmatter.prio = prio
    elif blocked is not None:
        blockers = set(frontmatter.blocked_by)
        blockers.add(blocked)
        frontmatter.blocked_by = list(blockers)
    else:
        log.warning("Nothing to set")
        raise typer.Exit(3)

    path.write_text(template.render(frontmatter, doc.content))


@app.command("start")
def start(id: Annotated[int, typer.Argument(help="ticket id")]):
    """Record the start of a ticket"""
    path, doc = find_by_id(id)
    frontmatter = FrontMatter(**doc.metadata)
    frontmatter.started_at = datetime.now()

    path.write_text(template.render(frontmatter, doc.content))


@app.command("show")
def show(id: Annotated[int, typer.Argument(help="ticket id")]):
    """Show details for a ticket"""
    path, _ = find_by_id(id)
    log.message(path.read_text())


@app.command("done")
def done(id: Annotated[int, typer.Argument(help="ticket id")]):
    """Mark ticket as done.

    Note that there is a difference between done and closed:
        - done: Work has been done
        - closed: Work is no longer relevant
    """
    path, doc = find_by_id(id)
    frontmatter = FrontMatter(**doc.metadata)
    frontmatter.finished_at = datetime.now()

    new_path = settings.root / f"done/{path.name}"
    new_path.parent.mkdir(parents=True, exist_ok=True)
    new_path.write_text(template.render(frontmatter, doc.content))
    path.unlink()
    log.message(f"{path} -> {new_path}")


@app.command("close")
def close(
    id: Annotated[int, typer.Argument(help="ticket id")],
    reason: Annotated[
        list[str],
        typer.Argument(help="Brief explanation why the ticket is being closed."),
    ],
):
    """Mark ticket as closed.

    Note that there is a difference between done and closed:
        - done: Work has been done
        - closed: Work is no longer relevant
    """
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
