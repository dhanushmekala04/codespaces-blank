"""Insurance tools — callable by agents for insurance and claims data."""

from app.services.insurance_service import InsuranceService

insurance_service = InsuranceService()


async def get_insurance_details(patient_id: str) -> dict:
    """Get insurance coverage details for a patient."""
    record = await insurance_service.get_patient_insurance(patient_id)
    return {
        "patient_id": patient_id,
        "insurance": record.model_dump() if record else None,
        "found": record is not None,
    }


async def get_patient_claims(patient_id: str) -> dict:
    """Get all insurance claims for a patient."""
    claims = await insurance_service.get_patient_claims(patient_id)
    return {
        "patient_id": patient_id,
        "count": len(claims) if claims else 0,
        "claims": claims or [],
    }


async def get_claim_status(claim_id: str) -> dict:
    """Get the current status of a specific claim."""
    status = await insurance_service.get_claim_status(claim_id)
    return {
        "claim_id": claim_id,
        "status": status if status else "not_found",
        "found": status is not None,
    }


async def get_claim_details(claim_id: str) -> dict:
    """Get full details for a specific claim."""
    claim = await insurance_service.get_claim(claim_id)
    return {
        "claim_id": claim_id,
        "claim": claim.model_dump() if claim else None,
        "found": claim is not None,
    }
