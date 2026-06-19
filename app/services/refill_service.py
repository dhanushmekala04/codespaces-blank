"""RefillService — prescription refill tracking and status management."""

from datetime import datetime, timezone
from typing import Any

from app.repositories.base import BaseRepository


class RefillService:
    """
    Service for tracking prescription refill requests.

    Note: This service tracks refill *status* only.
    It does not provide medication advice, dosage recommendations,
    or clinical guidance — those require a licensed healthcare provider.
    """

    async def get_refill_status(self, patient_id: str) -> dict[str, Any]:
        """
        Get current refill status for a patient.

        Returns a status summary. Extend this method once a
        RefillRepository / prescriptions collection is in place.
        """
        return {
            "patient_id": patient_id,
            "checked_at": datetime.now(timezone.utc).isoformat(),
            "status": "no_pending_refills",
            "pending_refills": [],
            "message": (
                "No pending refill requests found. "
                "Contact your healthcare provider to request a refill."
            ),
        }

    async def get_active_medications(self, patient_id: str) -> list[dict[str, Any]]:
        """
        Get list of active medications for a patient.

        Returns an empty list until a prescriptions collection is wired up.
        """
        return []

    async def request_refill(
        self,
        patient_id: str,
        medication_name: str,
        notes: str | None = None,
    ) -> dict[str, Any]:
        """
        Record a refill request for a patient.

        Returns a confirmation dict. Extend once a repository is available.
        """
        return {
            "patient_id": patient_id,
            "medication": medication_name,
            "status": "requested",
            "requested_at": datetime.now(timezone.utc).isoformat(),
            "notes": notes,
            "message": (
                f"Refill request for '{medication_name}' has been received. "
                "Your care team will review and respond within 1-2 business days."
            ),
        }

    async def get_refill_history(self, patient_id: str) -> list[dict[str, Any]]:
        """
        Get refill request history for a patient.

        Returns an empty list until a prescriptions collection is wired up.
        """
        return []
