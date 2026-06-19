from app.repositories.appointment_repository import AppointmentRepository
from app.schemas.appointment import AppointmentDocument
from app.schemas.enums import AppointmentStatus
from app.services.cache_service import cache_service

_APT_SUMMARY_TTL = 60 * 5   # 5 min — same tier as timeline


class AppointmentService:
    def __init__(self, appointment_repository: AppointmentRepository | None = None):
        self.appointment_repository = appointment_repository or AppointmentRepository()

    async def get_appointment(self, appointment_id: str) -> AppointmentDocument | None:
        """Get appointment by MongoDB _id."""
        return await self.appointment_repository.get_by_id(appointment_id)

    async def get_patient_appointments(self, patient_id: str) -> list[AppointmentDocument]:
        """Get all appointments for a patient, newest first."""
        return await self.appointment_repository.get_by_patient(patient_id)

    async def get_upcoming_appointments(self, patient_id: str) -> list[AppointmentDocument]:
        """Get only scheduled (upcoming) appointments."""
        return await self.appointment_repository.get_upcoming(patient_id)

    async def list_appointments(
        self,
        patient_id: str | None = None,
        status: AppointmentStatus | None = None,
    ) -> list[AppointmentDocument]:
        """List appointments with optional patient and status filters."""
        if patient_id and status:
            return await self.appointment_repository.get_by_status(patient_id, status)
        if patient_id:
            return await self.appointment_repository.get_by_patient(patient_id)
        return await self.appointment_repository.list()

    async def get_appointments_summary(self, patient_id: str) -> dict:
        """Return a serializable summary of a patient's appointments.
        Redis cache: appointment_summary:{patient_id}  TTL 5 min
        """
        cache_key = f"appointment_summary:{patient_id}"
        cached = await cache_service._getjson(cache_key)
        if cached is not None:
            return cached

        appointments = await self.get_patient_appointments(patient_id)
        result = [
            {
                "_id": str(apt.id),
                "appointment_id": getattr(apt, "appointment_id", str(apt.id)),
                "scheduled_at": apt.scheduled_at.isoformat() if apt.scheduled_at else "",
                "status": apt.status,
                "reason": apt.reason or "",
                "provider_id": apt.provider_id or "",
                "notes": apt.notes or "",
            }
            for apt in appointments
        ]

        await cache_service._setex(cache_key, _APT_SUMMARY_TTL, result)
        return result

    async def invalidate_appointments(self, patient_id: str) -> None:
        """Invalidate cached appointment summary after any write."""
        await cache_service._delete(f"appointment_summary:{patient_id}")
