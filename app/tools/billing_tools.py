from app.services.billing_service import BillingService

billing_service = BillingService()


async def get_current_balance(patient_id: str):
    record = await billing_service.get_billing(patient_id)
    return {"patient_id": patient_id, "balance": str(record.amount_due) if record else "0"}


async def get_billing_history(patient_id: str):
    return {"patient_id": patient_id, "history": []}


async def explain_balance_change(patient_id: str):
    return {"patient_id": patient_id, "explanation": "Balance change review pending."}
