from datetime import datetime
from typing import Any

from pydantic import Field

from app.schemas.base import BaseDocument


class AuditLogDocument(BaseDocument):
    request_id: str
    actor_id: str | None = None
    action: str
    outcome: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    latency_ms: int | None = None


class AuditLogCreate(AuditLogDocument):
    pass
