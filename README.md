# mdtasks

Simple commandline tasks and tickets via markdown files

## Installation

```
uv tool install mdtasks
```

The tool installs an executable `mdtasks` and an alias `t` that refers to the same executable.

## Usage

Use `t --help` for detailed up to date help.

Tasks are stored in a central folder by can be grouped by project and context. Typically, you will have one or two projects but separate contexts (e.g. "messaging", "backend", "ux", "website", ...). You can set both via environment variables. Use [direnv](https://direnv.net/) to automatically switch based on the current directory. The following env vars are read:

| Env Var | description | default |
|---------|-------------|---------|
| `MDTASKS_ROOT` | root directory for task files | `~/.mdtasks` |
| `MDTASKS_PROJECT` | project specifier | `"any"` |
| `MDTASKS_DEFAULT_CONTEXT` | default context specifier | `"any"` |


To create your first task, run

```
t new my-first-task --use-full-spec
```

This will scaffold a task, open your preferred editor (`$EDITOR`) to let you edit the task and will then move the tasks to `$MDTASKS_ROOT/open/` directory.
The flag `--use-full-spec` is useful while you're not yet really familiar with mdtasks metadata schema: when called with `--use-full-spec`, mdtasks will add the full metadata schema to the task file, including optional arguments.

To see an overview of existing tasks, run
```
t ls
```

For other kinds of usage, use `t --help`.

## Projects vs Contexts

Projects and contexts may appear quite similar, but they aren't really: Typically, projects refer to an overarching concept. You work on that project for a longer time. That's why mdtasks isn't really able to filter by project from the command line. The idea is that you might have projects "private" and "work". You can filter by project only via environment variables (e.g. by setting `MDTASKS_PROJECT` for a particular directory via direnv). On the other hand, contexts are less tightly coupled to a particular directory and the cli typically allows for ad-hoc switches between different contexts (although you can also set the default context via environment variable).
