from fastapi import APIRouter

router = APIRouter(prefix="/billing", tags=["billing"])


@router.get("/{patient_id}")
async def get_billing(patient_id: str):
    return {"patient_id": patient_id}
