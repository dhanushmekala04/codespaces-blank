from app.services.event_service import EventService

event_service = EventService()


async def get_patient_timeline(patient_id: str):
    events = await event_service.list_events(patient_id)
    return {"patient_id": patient_id, "events": [event.model_dump() for event in events]}


async def get_root_cause(patient_id: str):
    return {"patient_id": patient_id, "root_cause": "Analysis pending"}
