"""Appointments API routes."""

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel

from app.services.appointment_service import AppointmentService

router = APIRouter(prefix="/appointments", tags=["appointments"])
_appointment_service = AppointmentService()


class AppointmentItem(BaseModel):
    id: str
    appointment_id: str
    scheduled_at: str
    status: str
    reason: str | None
    provider_id: str | None
    notes: str | None


class AppointmentsResponse(BaseModel):
    patient_id: str
    count: int
    appointments: list[AppointmentItem]


@router.get("/patient/{patient_id}", response_model=AppointmentsResponse)
async def get_patient_appointments(
    patient_id: str,
    upcoming_only: bool = Query(False, description="Return only scheduled appointments"),
) -> AppointmentsResponse:
    """Get all appointments (or only upcoming) for a patient."""
    if upcoming_only:
        appointments = await _appointment_service.get_upcoming_appointments(patient_id)
    else:
        appointments = await _appointment_service.get_patient_appointments(patient_id)

    items = [
        AppointmentItem(
            id=str(apt.id),
            appointment_id=getattr(apt, "appointment_id", str(apt.id)),
            scheduled_at=apt.scheduled_at.isoformat() if apt.scheduled_at else "",
            status=apt.status,
            reason=apt.reason,
            provider_id=apt.provider_id,
            notes=apt.notes,
        )
        for apt in appointments
    ]

    return AppointmentsResponse(
        patient_id=patient_id,
        count=len(items),
        appointments=items,
    )


@router.get("/{appointment_id}", response_model=AppointmentItem)
async def get_appointment(appointment_id: str) -> AppointmentItem:
    """Get a single appointment by its ID."""
    apt = await _appointment_service.get_appointment(appointment_id)
    if apt is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Appointment '{appointment_id}' not found.",
        )
    return AppointmentItem(
        id=str(apt.id),
        appointment_id=getattr(apt, "appointment_id", str(apt.id)),
        scheduled_at=apt.scheduled_at.isoformat() if apt.scheduled_at else "",
        status=apt.status,
        reason=apt.reason,
        provider_id=apt.provider_id,
        notes=apt.notes,
    )
