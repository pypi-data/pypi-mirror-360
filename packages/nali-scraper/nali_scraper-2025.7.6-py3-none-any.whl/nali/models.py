from dataclasses import dataclass
from datetime import datetime


@dataclass
class Notice:
    id: int
    title: str | None
    content: str | None
    author: str | None
    url: str | None
    date: datetime | None
