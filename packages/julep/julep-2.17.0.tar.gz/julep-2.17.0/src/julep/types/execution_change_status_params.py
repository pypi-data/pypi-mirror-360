# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Optional
from typing_extensions import Literal, TypeAlias, TypedDict

__all__ = ["ExecutionChangeStatusParams", "ResumeExecutionRequest", "StopExecutionRequest"]


class ResumeExecutionRequest(TypedDict, total=False):
    input: Optional[object]

    status: Literal["running"]


class StopExecutionRequest(TypedDict, total=False):
    reason: Optional[str]

    status: Literal["cancelled"]


ExecutionChangeStatusParams: TypeAlias = Union[ResumeExecutionRequest, StopExecutionRequest]
