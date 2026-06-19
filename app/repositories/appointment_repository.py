from app.repositories.base import BaseRepository
from app.schemas.appointment import AppointmentDocument
from app.schemas.enums import AppointmentStatus


class AppointmentRepository(BaseRepository[AppointmentDocument]):
    def __init__(self):
        super().__init__(collection_name="appointments", model_cls=AppointmentDocument)

    async def get_by_patient(self, patient_id: str) -> list[AppointmentDocument]:
        """Get all appointments for a patient, newest first."""
        collection = await self._collection()
        cursor = collection.find(
            {"patient_id": patient_id, "is_deleted": False}
        ).sort("scheduled_at", -1)
        docs = await cursor.to_list(length=None)
        return [self.model_cls.model_validate(doc) for doc in docs]

    async def get_upcoming(self, patient_id: str) -> list[AppointmentDocument]:
        """Get scheduled (upcoming) appointments for a patient."""
        collection = await self._collection()
        cursor = collection.find(
            {
                "patient_id": patient_id,
                "is_deleted": False,
                "status": AppointmentStatus.SCHEDULED.value,
            }
        ).sort("scheduled_at", 1)
        docs = await cursor.to_list(length=None)
        return [self.model_cls.model_validate(doc) for doc in docs]

    async def get_by_status(
        self,
        patient_id: str,
        status: AppointmentStatus,
    ) -> list[AppointmentDocument]:
        """Get appointments by status."""
        collection = await self._collection()
        cursor = collection.find(
            {
                "patient_id": patient_id,
                "is_deleted": False,
                "status": status.value,
            }
        ).sort("scheduled_at", -1)
        docs = await cursor.to_list(length=None)
        return [self.model_cls.model_validate(doc) for doc in docs]

    async def get_by_provider(self, provider_id: str) -> list[AppointmentDocument]:
        """Get all appointments for a provider."""
        collection = await self._collection()
        cursor = collection.find(
            {"provider_id": provider_id, "is_deleted": False}
        ).sort("scheduled_at", 1)
        docs = await cursor.to_list(length=None)
        return [self.model_cls.model_validate(doc) for doc in docs]
