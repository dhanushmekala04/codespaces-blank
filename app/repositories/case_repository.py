from app.repositories.base import BaseRepository
from app.schemas.case import CaseDocument
from app.schemas.enums import CaseStatus


class CaseRepository(BaseRepository[CaseDocument]):
    def __init__(self):
        super().__init__(collection_name="cases", model_cls=CaseDocument)

    async def get_by_patient(self, patient_id: str) -> list[CaseDocument]:
        """Get all cases for a patient, newest first."""
        collection = await self._collection()
        cursor = collection.find(
            {"patient_id": patient_id, "is_deleted": False}
        ).sort("opened_at", -1)
        docs = await cursor.to_list(length=None)
        return [self.model_cls.model_validate(doc) for doc in docs]

    async def get_open_cases(self, patient_id: str) -> list[CaseDocument]:
        """Get all open cases for a patient."""
        collection = await self._collection()
        cursor = collection.find(
            {
                "patient_id": patient_id,
                "is_deleted": False,
                "status": CaseStatus.OPEN.value,
            }
        ).sort("opened_at", -1)
        docs = await cursor.to_list(length=None)
        return [self.model_cls.model_validate(doc) for doc in docs]

    async def get_by_status(
        self,
        patient_id: str,
        status: CaseStatus,
    ) -> list[CaseDocument]:
        """Get cases by status."""
        collection = await self._collection()
        cursor = collection.find(
            {
                "patient_id": patient_id,
                "is_deleted": False,
                "status": status.value,
            }
        ).sort("opened_at", -1)
        docs = await cursor.to_list(length=None)
        return [self.model_cls.model_validate(doc) for doc in docs]

    async def get_by_provider(self, provider_id: str) -> list[CaseDocument]:
        """Get all cases assigned to a provider."""
        collection = await self._collection()
        cursor = collection.find(
            {"assigned_provider_id": provider_id, "is_deleted": False}
        ).sort("opened_at", -1)
        docs = await cursor.to_list(length=None)
        return [self.model_cls.model_validate(doc) for doc in docs]
