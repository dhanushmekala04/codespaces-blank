from datetime import datetime
from typing import Any

from pydantic import Field

from app.schemas.base import BaseDocument


class ConversationHistoryDocument(BaseDocument):
    patient_id: str
    session_id: str
    messages: list[dict[str, Any]] = Field(default_factory=list)
    summary: str | None = None


class ConversationHistoryCreate(ConversationHistoryDocument):
    pass
