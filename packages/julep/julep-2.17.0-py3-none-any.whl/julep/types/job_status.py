# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["JobStatus"]


class JobStatus(BaseModel):
    id: str

    created_at: datetime

    updated_at: datetime

    has_progress: Optional[bool] = None

    name: Optional[str] = None

    progress: Optional[float] = None

    reason: Optional[str] = None

    state: Optional[Literal["pending", "in_progress", "retrying", "succeeded", "aborted", "failed", "unknown"]] = None
