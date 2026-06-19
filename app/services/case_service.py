from datetime import datetime, timezone

from app.repositories.case_repository import CaseRepository
from app.schemas.case import CaseDocument
from app.schemas.enums import CaseStatus


class CaseService:
    def __init__(self, case_repository: CaseRepository | None = None):
        self.case_repository = case_repository or CaseRepository()

    async def get_case(self, case_id: str) -> CaseDocument | None:
        """Get case by MongoDB _id."""
        return await self.case_repository.get_by_id(case_id)

    async def get_patient_cases(self, patient_id: str) -> list[CaseDocument]:
        """Get all cases for a patient, newest first."""
        return await self.case_repository.get_by_patient(patient_id)

    async def get_open_cases(self, patient_id: str) -> list[CaseDocument]:
        """Get all open cases for a patient."""
        return await self.case_repository.get_open_cases(patient_id)

    async def list_cases(self, patient_id: str | None = None) -> list[CaseDocument]:
        """List cases with optional patient filter."""
        if patient_id:
            return await self.case_repository.get_by_patient(patient_id)
        return await self.case_repository.list()

    async def create_case(
        self,
        patient_id: str,
        title: str,
        assigned_provider_id: str | None = None,
    ) -> CaseDocument:
        """Create a new case for a patient."""
        case = CaseDocument(
            patient_id=patient_id,
            case_id=f"CASE-{patient_id}-{int(datetime.now(timezone.utc).timestamp())}",
            title=title,
            status=CaseStatus.OPEN,
            assigned_provider_id=assigned_provider_id,
            opened_at=datetime.now(timezone.utc),
        )
        return await self.case_repository.create(case)

    async def update_case_status(self, case_id: str, status: CaseStatus) -> CaseDocument | None:
        """Update the status of a case."""
        updates: dict = {"status": status.value}
        if status == CaseStatus.CLOSED:
            updates["closed_at"] = datetime.now(timezone.utc).isoformat()
        return await self.case_repository.update(case_id, updates)

    async def get_cases_summary(self, patient_id: str) -> dict:
        """Return a serializable summary of all patient cases."""
        cases = await self.get_patient_cases(patient_id)
        open_cases = [c for c in cases if c.status == CaseStatus.OPEN]
        return {
            "total": len(cases),
            "open": len(open_cases),
            "cases": [
                {
                    "_id": str(c.id),
                    "case_id": c.case_id,
                    "title": c.title,
                    "status": c.status,
                    "opened_at": c.opened_at.isoformat() if c.opened_at else "",
                    "closed_at": c.closed_at.isoformat() if c.closed_at else None,
                    "assigned_provider_id": c.assigned_provider_id,
                }
                for c in cases
            ],
        }
