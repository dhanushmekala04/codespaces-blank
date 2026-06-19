from datetime import datetime

from pydantic import Field

from app.schemas.base import BaseDocument
from app.schemas.enums import ClaimStatus, InsuranceStatus


class InsuranceDocument(BaseDocument):
    patient_id: str
    plan_id: str
    payer_name: str
    member_id: str
    status: InsuranceStatus = InsuranceStatus.ACTIVE
    coverage_start: str | None = None
    coverage_end: str | None = None
    provider_name: str | None = None
    plan_name: str | None = None


class ClaimDocument(BaseDocument):
    """Insurance claim document."""
    patient_id: str
    insurance_id: str
    claim_number: str | None = None
    claim_amount: float = 0.0
    approved_amount: float | None = None
    status: ClaimStatus = ClaimStatus.SUBMITTED
    denial_reason: str | None = None
    submitted_at: datetime | None = None
    processed_at: datetime | None = None


class InsuranceCreate(InsuranceDocument):
    pass


class InsuranceUpdate(InsuranceDocument):
    patient_id: str | None = None
    plan_id: str | None = None
    payer_name: str | None = None
    member_id: str | None = None
    status: InsuranceStatus | None = None
