from app.repositories.patient_repository import PatientRepository
from app.schemas.patient import PatientDocument


class PatientService:
    def __init__(self, patient_repository: PatientRepository | None = None):
        self.patient_repository = patient_repository or PatientRepository()

    async def get_patient(self, patient_id: str) -> PatientDocument | None:
        return await self.patient_repository.get_by_id(patient_id)

    async def list_patients(self) -> list[PatientDocument]:
        return await self.patient_repository.list()

    async def validate_patient(self, patient_id: str) -> bool:
        patient = await self.get_patient(patient_id)
        return patient is not None
