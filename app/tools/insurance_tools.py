from app.services.insurance_service import InsuranceService

insurance_service = InsuranceService()


async def get_insurance_details(patient_id: str):
    record = await insurance_service.get_insurance(patient_id)
    return {"patient_id": patient_id, "insurance": record.model_dump() if record else None}


async def get_claim_status(claim_id: str):
    return {"claim_id": claim_id, "status": "pending"}
