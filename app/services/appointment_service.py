from app.repositories.appointment_repository import AppointmentRepository
from app.schemas.appointment import AppointmentDocument


class AppointmentService:
    def __init__(self, appointment_repository: AppointmentRepository | None = None):
        self.appointment_repository = appointment_repository or AppointmentRepository()

    async def get_appointment(self, appointment_id: str) -> AppointmentDocument | None:
        return await self.appointment_repository.get_by_id(appointment_id)

    async def list_appointments(self, patient_id: str | None = None):
        filters = {"patient_id": patient_id} if patient_id else None
        return await self.appointment_repository.list(filters)
