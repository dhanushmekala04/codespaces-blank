"""Case tools — callable by agents for case and lab result data."""

from app.services.case_service import CaseService

case_service = CaseService()


async def get_case_summary(patient_id: str) -> dict:
    """Get a summary of all cases for a patient."""
    summary = await case_service.get_cases_summary(patient_id)
    return {"patient_id": patient_id, **summary}


async def get_case_by_id(case_id: str) -> dict:
    """Get details for a specific case."""
    case = await case_service.get_case(case_id)
    return {
        "case_id": case_id,
        "case": {
            "_id": str(case.id),
            "case_id": case.case_id,
            "title": case.title,
            "status": case.status,
            "opened_at": case.opened_at.isoformat() if case.opened_at else "",
            "closed_at": case.closed_at.isoformat() if case.closed_at else None,
            "assigned_provider_id": case.assigned_provider_id,
        } if case else None,
        "found": case is not None,
    }


async def get_open_cases(patient_id: str) -> dict:
    """Get all open cases for a patient."""
    cases = await case_service.get_open_cases(patient_id)
    return {
        "patient_id": patient_id,
        "count": len(cases),
        "cases": [
            {
                "_id": str(c.id),
                "case_id": c.case_id,
                "title": c.title,
                "status": c.status,
                "opened_at": c.opened_at.isoformat() if c.opened_at else "",
            }
            for c in cases
        ],
    }


async def get_lab_results(patient_id: str) -> dict:
    """
    Get lab results for a patient.

    This is a placeholder — wire up a lab results collection
    once the labs data source is available.
    """
    return {
        "patient_id": patient_id,
        "results": [],
        "message": "Lab results retrieval requires integration with the lab results collection.",
    }
