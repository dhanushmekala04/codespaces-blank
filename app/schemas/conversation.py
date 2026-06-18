from datetime import datetime

from app.schemas.base import BaseDocument


class ConversationHistoryDocument(BaseDocument):
    patient_id: str
    session_id: str
    messages: list[dict] = []
    summary: str | None = None


class ConversationHistoryCreate(ConversationHistoryDocument):
    pass
