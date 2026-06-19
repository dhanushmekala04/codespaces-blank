from app.repositories.patient_repository import PatientRepository
from app.schemas.patient import PatientDocument
from app.schemas.enums import ConsentStatus, PatientStatus


class PatientService:
    def __init__(self, patient_repository: PatientRepository | None = None):
        self.patient_repository = patient_repository or PatientRepository()

    async def get_patient(self, patient_id: str) -> PatientDocument | None:
        """Get patient by their patient_id field."""
        return await self.patient_repository.get_by_patient_id(patient_id)

    async def get_patient_by_db_id(self, db_id: str) -> PatientDocument | None:
        """Get patient by MongoDB _id."""
        return await self.patient_repository.get_by_id(db_id)

    async def list_patients(self, tenant_id: str | None = None) -> list[PatientDocument]:
        """List all patients, optionally scoped to a tenant."""
        if tenant_id:
            return await self.patient_repository.get_by_tenant(tenant_id)
        return await self.patient_repository.list()

    async def validate_patient(self, patient_id: str) -> bool:
        """Return True if the patient exists and is active."""
        patient = await self.get_patient(patient_id)
        if patient is None:
            return False
        return patient.status == PatientStatus.ACTIVE

    async def has_consent(self, patient_id: str) -> bool:
        """Return True if the patient has granted consent."""
        return await self.patient_repository.has_consent(patient_id)

    async def get_patient_profile(self, patient_id: str) -> dict | None:
        """Return a serializable patient profile dict."""
        patient = await self.get_patient(patient_id)
        if patient is None:
            return None
        return {
            "patient_id": patient.patient_id,
            "tenant_id": patient.tenant_id,
            "full_name": f"{patient.first_name} {patient.last_name}",
            "email": patient.email,
            "phone": patient.phone,
            "date_of_birth": patient.date_of_birth,
            "status": patient.status,
            "consent_status": patient.consent_status,
            "preferred_language": patient.preferred_language,
        }
