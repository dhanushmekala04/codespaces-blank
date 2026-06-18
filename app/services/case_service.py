from app.repositories.case_repository import CaseRepository
from app.schemas.case import CaseDocument


class CaseService:
    def __init__(self, case_repository: CaseRepository | None = None):
        self.case_repository = case_repository or CaseRepository()

    async def get_case(self, case_id: str) -> CaseDocument | None:
        return await self.case_repository.get_by_id(case_id)

    async def list_cases(self, patient_id: str | None = None):
        filters = {"patient_id": patient_id} if patient_id else None
        return await self.case_repository.list(filters)
