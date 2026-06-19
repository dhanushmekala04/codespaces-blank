"""Billing tools — callable by agents for billing data retrieval."""

from app.services.billing_service import BillingService

billing_service = BillingService()


async def get_current_balance(patient_id: str) -> dict:
    """Get the current outstanding balance for a patient."""
    balance = await billing_service.get_patient_balance(patient_id)
    return {
        "patient_id": patient_id,
        "balance": balance,
        "currency": "USD",
    }


async def get_billing_history(patient_id: str) -> dict:
    """Get full billing history (charges and payments) for a patient."""
    history = await billing_service.get_billing_history(patient_id)
    return {
        "patient_id": patient_id,
        "count": len(history),
        "history": history,
    }


async def get_billing_summary(patient_id: str) -> dict:
    """Get an aggregated billing summary including charges and payments."""
    summary = await billing_service.get_billing_summary(patient_id)
    if summary is None:
        return {
            "patient_id": patient_id,
            "total_balance": 0.0,
            "total_due": 0.0,
            "total_paid": 0.0,
            "charges": [],
            "payments": [],
        }
    return summary


async def explain_balance_change(patient_id: str) -> dict:
    """
    Provide a narrative explanation of recent balance changes.

    This is a placeholder — extend to compare billing records across
    time ranges and generate a human-readable explanation.
    """
    summary = await billing_service.get_billing_summary(patient_id)
    if not summary:
        return {"patient_id": patient_id, "explanation": "No billing records found."}

    balance = summary.get("total_balance", 0.0)
    charge_count = len(summary.get("charges", []))
    payment_count = len(summary.get("payments", []))

    return {
        "patient_id": patient_id,
        "current_balance": balance,
        "explanation": (
            f"Your current balance is ${balance:.2f}. "
            f"There are {charge_count} charge(s) and {payment_count} payment(s) on record."
        ),
    }
