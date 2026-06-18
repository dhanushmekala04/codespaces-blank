from datetime import datetime

from app.schemas.base import BaseDocument
from app.schemas.enums import EventType


class EventDocument(BaseDocument):
    patient_id: str
    event_type: EventType
    occurred_at: datetime
    details: dict = {}
    source: str | None = None


class EventCreate(EventDocument):
    pass


class EventUpdate(EventDocument):
    patient_id: str | None = None
    event_type: EventType | None = None
    occurred_at: datetime | None = None
    details: dict | None = None
