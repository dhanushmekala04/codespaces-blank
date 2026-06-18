from fastapi import APIRouter

router = APIRouter(prefix="/appointments", tags=["appointments"])


@router.get("/{appointment_id}")
async def get_appointment(appointment_id: str):
    return {"appointment_id": appointment_id}
