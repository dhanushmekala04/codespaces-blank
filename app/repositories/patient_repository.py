from app.repositories.base import BaseRepository
from app.schemas.patient import PatientDocument
from app.schemas.enums import ConsentStatus, PatientStatus


class PatientRepository(BaseRepository[PatientDocument]):
    def __init__(self):
        super().__init__(collection_name="patients", model_cls=PatientDocument)

    async def get_by_patient_id(self, patient_id: str) -> PatientDocument | None:
        """Get patient by their patient_id field (not MongoDB _id)."""
        collection = await self._collection()
        doc = await collection.find_one({"patient_id": patient_id, "is_deleted": False})
        return self.model_cls.model_validate(doc) if doc else None

    async def get_by_tenant(self, tenant_id: str) -> list[PatientDocument]:
        """Get all patients for a tenant."""
        collection = await self._collection()
        cursor = collection.find({"tenant_id": tenant_id, "is_deleted": False})
        docs = await cursor.to_list(length=None)
        return [self.model_cls.model_validate(doc) for doc in docs]

    async def get_by_email(self, email: str) -> PatientDocument | None:
        """Find patient by email address."""
        collection = await self._collection()
        doc = await collection.find_one({"email": email, "is_deleted": False})
        return self.model_cls.model_validate(doc) if doc else None

    async def get_active_patients(self, tenant_id: str) -> list[PatientDocument]:
        """Get all active patients for a tenant."""
        collection = await self._collection()
        cursor = collection.find(
            {
                "tenant_id": tenant_id,
                "is_deleted": False,
                "status": PatientStatus.ACTIVE.value,
            }
        )
        docs = await cursor.to_list(length=None)
        return [self.model_cls.model_validate(doc) for doc in docs]

    async def has_consent(self, patient_id: str) -> bool:
        """Check whether a patient has granted consent."""
        patient = await self.get_by_patient_id(patient_id)
        if patient is None:
            return False
        return patient.consent_status == ConsentStatus.GRANTED
