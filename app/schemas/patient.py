from pydantic import Field

from app.schemas.base import BaseDocument
from app.schemas.enums import ConsentStatus, PatientStatus


class PatientDocument(BaseDocument):
    patient_id: str
    tenant_id: str
    first_name: str
    last_name: str
    email: str | None = None
    phone: str | None = None
    status: PatientStatus = PatientStatus.ACTIVE
    consent_status: ConsentStatus = ConsentStatus.PENDING
    date_of_birth: str | None = None
    preferred_language: str = "en"


class PatientCreate(PatientDocument):
    pass


class PatientUpdate(PatientDocument):
    patient_id: str | None = None
    first_name: str | None = None
    last_name: str | None = None
