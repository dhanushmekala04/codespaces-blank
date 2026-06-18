from datetime import datetime

from pydantic import Field

from app.schemas.base import BaseDocument
from app.schemas.enums import CaseStatus


class CaseDocument(BaseDocument):
    patient_id: str
    case_id: str
    title: str
    status: CaseStatus = CaseStatus.OPEN
    assigned_provider_id: str | None = None
    opened_at: datetime | None = None
    closed_at: datetime | None = None


class CaseCreate(CaseDocument):
    pass


class CaseUpdate(CaseDocument):
    patient_id: str | None = None
    case_id: str | None = None
    title: str | None = None
    status: CaseStatus | None = None
