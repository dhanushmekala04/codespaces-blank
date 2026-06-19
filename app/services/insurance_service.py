"""Insurance Service for managing claims and coverage."""

from app.repositories.insurance_repository import InsuranceRepository
from app.schemas.insurance import InsuranceDocument, ClaimDocument
from app.services.cache_service import cache_service


class InsuranceService:
    """Service for insurance and claims operations."""

    def __init__(self, insurance_repository: InsuranceRepository | None = None):
        self.insurance_repository = insurance_repository or InsuranceRepository()

    async def get_patient_insurance(self, patient_id: str) -> InsuranceDocument | None:
        """Get insurance information for a patient."""
        return await self.insurance_repository.get_by_patient(patient_id)

    async def get_patient_claims(self, patient_id: str) -> list[dict] | None:
        """
        Get all claims for a patient.
        Redis cache: claim:{patient_id}:all  TTL 2 min
        """
        cache_key = f"{patient_id}:all"
        cached = await cache_service.get_claim(cache_key)
        if cached is not None:
            return cached

        claims = await self.insurance_repository.get_patient_claims(patient_id)

        if not claims:
            return None

        result = [
            {
                "_id": str(claim.id),
                "patient_id": claim.patient_id,
                "insurance_id": claim.insurance_id,
                "claim_amount": claim.claim_amount,
                "status": claim.status,
                "denial_reason": getattr(claim, "denial_reason", None),
                "submitted_at": claim.submitted_at.isoformat() if claim.submitted_at else None,
            }
            for claim in claims
        ]

        await cache_service.set_claim(cache_key, result)
        return result

    async def get_claim(self, claim_id: str) -> ClaimDocument | None:
        """Get specific claim details. Redis cache: claim:{claim_id} TTL 2 min"""
        cached = await cache_service.get_claim(claim_id)
        if cached is not None:
            # Re-hydrate as a simple dict check; return as-is for dict consumers
            return cached  # type: ignore[return-value]

        claim = await self.insurance_repository.get_claim(claim_id)
        if claim:
            await cache_service.set_claim(claim_id, {
                "_id": str(claim.id),
                "status": claim.status,
                "claim_amount": claim.claim_amount,
                "denial_reason": getattr(claim, "denial_reason", None),
            })
        return claim

    async def get_claim_status(self, claim_id: str) -> str | None:
        """Get claim status."""
        claim = await self.get_claim(claim_id)
        if isinstance(claim, dict):
            return claim.get("status")
        return claim.status if claim else None
