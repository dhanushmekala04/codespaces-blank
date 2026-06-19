"""Billing API routes."""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.services.billing_service import BillingService

router = APIRouter(prefix="/billing", tags=["billing"])
_billing_service = BillingService()


class BillingChargeItem(BaseModel):
    charge_id: str
    account_id: str
    description: str
    amount: float
    status: str
    due_date: str | None
    date: str


class BillingPaymentItem(BaseModel):
    payment_id: str
    amount: float
    date: str


class BillingSummaryResponse(BaseModel):
    patient_id: str
    total_due: float
    total_paid: float
    total_balance: float
    currency: str
    charges: list[BillingChargeItem]
    payments: list[BillingPaymentItem]


class BalanceResponse(BaseModel):
    patient_id: str
    balance: float
    currency: str = "USD"


@router.get("/{patient_id}/summary", response_model=BillingSummaryResponse)
async def get_billing_summary(patient_id: str) -> BillingSummaryResponse:
    """Get full billing summary for a patient."""
    summary = await _billing_service.get_billing_summary(patient_id)
    if summary is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No billing records found for patient '{patient_id}'.",
        )

    charges = [
        BillingChargeItem(
            charge_id=c["charge_id"],
            account_id=c.get("account_id", ""),
            description=c.get("description", ""),
            amount=c["amount"],
            status=c.get("status", ""),
            due_date=c.get("due_date") or None,
            date=c.get("date", ""),
        )
        for c in summary.get("charges", [])
    ]

    payments = [
        BillingPaymentItem(
            payment_id=p["payment_id"],
            amount=p["amount"],
            date=p.get("date", ""),
        )
        for p in summary.get("payments", [])
    ]

    return BillingSummaryResponse(
        patient_id=patient_id,
        total_due=summary.get("total_due", 0.0),
        total_paid=summary.get("total_paid", 0.0),
        total_balance=summary.get("total_balance", 0.0),
        currency=summary.get("currency", "USD"),
        charges=charges,
        payments=payments,
    )


@router.get("/{patient_id}/balance", response_model=BalanceResponse)
async def get_balance(patient_id: str) -> BalanceResponse:
    """Get current outstanding balance for a patient."""
    balance = await _billing_service.get_patient_balance(patient_id)
    return BalanceResponse(patient_id=patient_id, balance=balance)
