from datetime import datetime

from pydantic import Field

from app.schemas.base import BaseDocument
from app.schemas.enums import AppointmentStatus


class AppointmentDocument(BaseDocument):
    patient_id: str
    provider_id: str | None = None
    appointment_id: str
    scheduled_at: datetime
    status: AppointmentStatus = AppointmentStatus.SCHEDULED
    reason: str | None = None
    notes: str | None = None


class AppointmentCreate(AppointmentDocument):
    pass


class AppointmentUpdate(AppointmentDocument):
    patient_id: str | None = None
    appointment_id: str | None = None
    scheduled_at: datetime | None = None
    status: AppointmentStatus | None = None
