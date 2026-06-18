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


class InsuranceCreate(InsuranceDocument):
    pass


class InsuranceUpdate(InsuranceDocument):
    patient_id: str | None = None
    plan_id: str | None = None
    payer_name: str | None = None
    member_id: str | None = None
    status: InsuranceStatus | None = None
