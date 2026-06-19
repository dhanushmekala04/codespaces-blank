"""Patients API routes."""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.services.patient_service import PatientService

router = APIRouter(prefix="/patients", tags=["patients"])
_patient_service = PatientService()


class PatientResponse(BaseModel):
    patient_id: str
    tenant_id: str
    full_name: str
    email: str | None
    phone: str | None
    date_of_birth: str | None
    status: str
    consent_status: str
    preferred_language: str


@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(patient_id: str) -> PatientResponse:
    """Get patient profile by patient_id."""
    profile = await _patient_service.get_patient_profile(patient_id)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient '{patient_id}' not found.",
        )
    return PatientResponse(**profile)


@router.get("/{patient_id}/exists", response_model=dict)
async def patient_exists(patient_id: str) -> dict:
    """Check whether a patient exists and is active."""
    valid = await _patient_service.validate_patient(patient_id)
    return {"patient_id": patient_id, "exists": valid}
