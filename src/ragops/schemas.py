"""Shared service schemas."""

from typing import Literal

from pydantic import BaseModel, ConfigDict

ReadinessStatus = Literal["ok", "unavailable", "pending", "timeout"]


class HealthResponse(BaseModel):
    """Liveness response returned by the API."""

    model_config = ConfigDict(frozen=True)

    status: Literal["ok"]


class ReadinessResponse(BaseModel):
    """Dependency status without connection details or credentials."""

    model_config = ConfigDict(frozen=True)

    status: Literal["ok", "not_ready"]
    checks: dict[str, ReadinessStatus]
