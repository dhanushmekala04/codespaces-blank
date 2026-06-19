"""Appointment tools — callable by agents for appointment data retrieval."""

from app.services.appointment_service import AppointmentService

appointment_service = AppointmentService()


async def get_upcoming_appointments(patient_id: str) -> dict:
    """Get upcoming (scheduled) appointments for a patient."""
    appointments = await appointment_service.get_upcoming_appointments(patient_id)
    return {
        "patient_id": patient_id,
        "count": len(appointments),
        "appointments": [
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
        ],
    }


async def get_all_appointments(patient_id: str) -> dict:
    """Get full appointment history for a patient."""
    appointments = await appointment_service.get_patient_appointments(patient_id)
    return {
        "patient_id": patient_id,
        "count": len(appointments),
        "appointments": [
            {
                "_id": str(apt.id),
                "appointment_id": getattr(apt, "appointment_id", str(apt.id)),
                "scheduled_at": apt.scheduled_at.isoformat() if apt.scheduled_at else "",
                "status": apt.status,
                "reason": apt.reason or "",
                "provider_id": apt.provider_id or "",
            }
            for apt in appointments
        ],
    }


async def find_available_slots(provider_id: str | None = None) -> dict:
    """
    Find available appointment slots.

    This is a placeholder — integrate with a scheduling system
    (e.g., a provider availability collection) to return real slots.
    """
    return {
        "provider_id": provider_id,
        "slots": [],
        "message": "Slot availability lookup requires integration with the scheduling system.",
    }


async def reschedule_appointment(appointment_id: str, new_time: str) -> dict:
    """
    Reschedule an existing appointment.

    This is a placeholder — wire up AppointmentRepository.update()
    with the new scheduled_at value once the rescheduling workflow is defined.
    """
    return {
        "appointment_id": appointment_id,
        "requested_time": new_time,
        "status": "pending_confirmation",
        "message": "Reschedule request received. A staff member will confirm shortly.",
    }
