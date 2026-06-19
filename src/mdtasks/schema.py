from pydantic import BaseModel
from datetime import datetime


class FrontMatter(BaseModel):
    project: str
    context: str
    id: int
    created_at: datetime
    started_at: datetime | None = None
    finished_at: datetime | None = None
    prio: int = 0


class TaskShort(FrontMatter):
    title: str
