from fastapi import APIRouter

router = APIRouter(prefix="/timeline", tags=["timeline"])


@router.get("/{patient_id}")
async def get_timeline(patient_id: str):
    return {"patient_id": patient_id}
