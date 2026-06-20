from typing import Sequence
from mdtasks.schema import FrontMatter


def is_blocked(task: FrontMatter, open_tasks: Sequence[FrontMatter]) -> bool:
    for t in open_tasks:
        if t.id in task.blocked_by:
            return True
    return False


def get_blockers(task: FrontMatter, open_tasks: Sequence[FrontMatter]) -> set[int]:
    return set([t.id for t in open_tasks if t.id in task.blocked_by])
