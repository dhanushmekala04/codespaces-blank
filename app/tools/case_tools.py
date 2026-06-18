from app.services.case_service import CaseService

case_service = CaseService()


async def get_case_summary(case_id: str):
    case = await case_service.get_case(case_id)
    return {"case_id": case_id, "summary": case.title if case else "No case found"}


async def get_lab_results(patient_id: str):
    return {"patient_id": patient_id, "results": []}
