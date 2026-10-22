from datetime import datetime
from enum import Enum
from pathlib import Path

from pydantic import BaseModel, Field


class FrontMatter(BaseModel):
    project: str
    context: str
    id: int
    created_at: datetime
    started_at: datetime | None = None
    finished_at: datetime | None = None
    prio: int = 0
    blocked_by: list[int] = Field(default_factory=list)


class TaskShort(FrontMatter):
    title: str
    filename: Path | None = None


class TicketStatus(str, Enum):
    open = "open"
    closed = "closed"
    done = "done"


class Output(str, Enum):
    standard = "standard"
    json = "json"
    markdown = "markdown"
