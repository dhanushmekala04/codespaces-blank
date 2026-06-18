from decimal import Decimal
from datetime import datetime

from pydantic import Field

from app.schemas.base import BaseDocument
from app.schemas.enums import BillingStatus


class BillingDocument(BaseDocument):
    patient_id: str
    account_id: str
    amount_due: Decimal
    amount_paid: Decimal = Decimal("0.00")
    currency: str = "USD"
    status: BillingStatus = BillingStatus.OPEN
    due_date: datetime | None = None


class BillingCreate(BillingDocument):
    pass


class BillingUpdate(BillingDocument):
    patient_id: str | None = None
    account_id: str | None = None
    amount_due: Decimal | None = None
    amount_paid: Decimal | None = None
    status: BillingStatus | None = None
