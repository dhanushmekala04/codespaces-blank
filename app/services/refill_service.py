from app.repositories.base import BaseRepository
from typing import Any


class RefillService:
    async def get_refill_status(self, patient_id: str) -> dict[str, Any]:
        return {"patient_id": patient_id, "status": "pending"}
