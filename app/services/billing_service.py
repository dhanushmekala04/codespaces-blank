from app.repositories.billing_repository import BillingRepository
from app.schemas.billing import BillingDocument


class BillingService:
    def __init__(self, billing_repository: BillingRepository | None = None):
        self.billing_repository = billing_repository or BillingRepository()

    async def get_billing(self, patient_id: str) -> BillingDocument | None:
        records = await self.billing_repository.list({"patient_id": patient_id})
        return records[0] if records else None
