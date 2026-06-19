"""Billing Service for managing patient billing operations."""

from app.repositories.billing_repository import BillingRepository
from app.schemas.billing import BillingDocument
from app.schemas.enums import BillingStatus
from app.services.cache_service import cache_service


class BillingService:
    """Service for billing operations."""

    def __init__(self, billing_repository: BillingRepository | None = None):
        self.billing_repository = billing_repository or BillingRepository()

    async def get_billing_records(self, patient_id: str) -> list[BillingDocument]:
        """Get all billing records for a patient."""
        return await self.billing_repository.get_by_patient(patient_id)

    async def get_billing_summary(self, patient_id: str) -> dict | None:
        """
        Get billing summary for a patient.
        Redis cache: billing_summary:{patient_id}  TTL 2 min
        Never cache write operations — read-only summary only.
        """
        # Try cache first
        cached = await cache_service.get_billing_summary(patient_id)
        if cached is not None:
            return cached

        billings = await self.billing_repository.get_by_patient(patient_id)

        if not billings:
            return None

        total_due = sum(float(b.amount_due) for b in billings)
        total_paid = sum(float(b.amount_paid) for b in billings)
        total_balance = total_due - total_paid

        charges = [
            {
                "charge_id": str(b.id),
                "account_id": b.account_id,
                "description": f"Account {b.account_id}",
                "amount": float(b.amount_due),
                "status": b.status,
                "due_date": b.due_date.isoformat() if b.due_date else "",
                "date": b.created_at.isoformat() if b.created_at else "",
            }
            for b in billings
        ]

        payments = [
            {
                "payment_id": str(b.id),
                "amount": float(b.amount_paid),
                "date": b.updated_at.isoformat() if b.updated_at else "",
            }
            for b in billings
            if b.amount_paid > 0
        ]

        summary = {
            "_id": str(billings[0].id),
            "patient_id": patient_id,
            "total_due": total_due,
            "total_paid": total_paid,
            "total_balance": total_balance,
            "charges": charges,
            "payments": payments,
            "currency": billings[0].currency,
        }

        # Cache the result
        await cache_service.set_billing_summary(patient_id, summary)
        return summary

    async def get_patient_balance(self, patient_id: str) -> float:
        """Get current outstanding balance for a patient."""
        summary = await self.get_billing_summary(patient_id)
        return summary["total_balance"] if summary else 0.0

    async def get_open_balances(self, patient_id: str) -> list[BillingDocument]:
        """Get all unpaid / overdue billing records."""
        return await self.billing_repository.get_open_balances(patient_id)

    async def get_billing_history(self, patient_id: str) -> list[dict]:
        """Return serializable billing history for display."""
        billings = await self.billing_repository.get_by_patient(patient_id)
        return [
            {
                "charge_id": str(b.id),
                "account_id": b.account_id,
                "amount_due": float(b.amount_due),
                "amount_paid": float(b.amount_paid),
                "balance": float(b.amount_due - b.amount_paid),
                "status": b.status,
                "currency": b.currency,
                "due_date": b.due_date.isoformat() if b.due_date else "",
                "created_at": b.created_at.isoformat() if b.created_at else "",
            }
            for b in billings
        ]
