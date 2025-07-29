# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from datetime import datetime

from .entry import Entry
from .._models import BaseModel

__all__ = ["History", "Relation"]


class Relation(BaseModel):
    head: str

    relation: str

    tail: str


class History(BaseModel):
    created_at: datetime

    entries: List[Entry]

    relations: List[Relation]

    session_id: str
