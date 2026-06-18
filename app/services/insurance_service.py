from app.repositories.insurance_repository import InsuranceRepository
from app.schemas.insurance import InsuranceDocument


class InsuranceService:
    def __init__(self, insurance_repository: InsuranceRepository | None = None):
        self.insurance_repository = insurance_repository or InsuranceRepository()

    async def get_insurance(self, patient_id: str) -> InsuranceDocument | None:
        records = await self.insurance_repository.list({"patient_id": patient_id})
        return records[0] if records else None
