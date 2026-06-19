from app.repositories.base import BaseRepository
from app.schemas.billing import BillingDocument
from app.schemas.enums import BillingStatus


class BillingRepository(BaseRepository[BillingDocument]):
    def __init__(self):
        super().__init__(collection_name="billing", model_cls=BillingDocument)

    async def get_by_patient(self, patient_id: str) -> list[BillingDocument]:
        """Get all billing records for a patient."""
        collection = await self._collection()
        cursor = collection.find(
            {"patient_id": patient_id, "is_deleted": False}
        ).sort("created_at", -1)
        docs = await cursor.to_list(length=None)
        return [self.model_cls.model_validate(doc) for doc in docs]

    async def get_open_balances(self, patient_id: str) -> list[BillingDocument]:
        """Get unpaid billing records for a patient."""
        collection = await self._collection()
        cursor = collection.find(
            {
                "patient_id": patient_id,
                "is_deleted": False,
                "status": {"$in": [BillingStatus.OPEN.value, BillingStatus.PARTIAL.value, BillingStatus.OVERDUE.value]},
            }
        ).sort("due_date", 1)
        docs = await cursor.to_list(length=None)
        return [self.model_cls.model_validate(doc) for doc in docs]

    async def get_by_account(self, account_id: str) -> BillingDocument | None:
        """Get billing record by account ID."""
        collection = await self._collection()
        doc = await collection.find_one({"account_id": account_id, "is_deleted": False})
        return self.model_cls.model_validate(doc) if doc else None

    async def get_by_status(
        self,
        patient_id: str,
        status: BillingStatus,
    ) -> list[BillingDocument]:
        """Get billing records by status."""
        collection = await self._collection()
        cursor = collection.find(
            {
                "patient_id": patient_id,
                "is_deleted": False,
                "status": status.value,
            }
        ).sort("due_date", 1)
        docs = await cursor.to_list(length=None)
        return [self.model_cls.model_validate(doc) for doc in docs]
