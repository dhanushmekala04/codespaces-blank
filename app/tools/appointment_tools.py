from app.services.appointment_service import AppointmentService

appointment_service = AppointmentService()


async def get_upcoming_appointments(patient_id: str):
    return await appointment_service.list_appointments(patient_id)


async def find_available_slots(provider_id: str | None = None):
    return {"provider_id": provider_id, "slots": []}


async def reschedule_appointment(appointment_id: str, new_time: str):
    return {"appointment_id": appointment_id, "new_time": new_time}
