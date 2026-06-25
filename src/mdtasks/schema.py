from datetime import datetime

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
