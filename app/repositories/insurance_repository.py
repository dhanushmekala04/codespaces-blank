from app.repositories.base import BaseRepository
from app.schemas.insurance import InsuranceDocument, ClaimDocument


class InsuranceRepository(BaseRepository[InsuranceDocument]):
    def __init__(self):
        super().__init__(collection_name="insurance", model_cls=InsuranceDocument)

    async def get_by_patient(self, patient_id: str) -> InsuranceDocument | None:
        """Get insurance for a patient."""
        filters = {"patient_id": patient_id}
        results = await self.list(filters)
        return results[0] if results else None

    async def get_patient_claims(self, patient_id: str) -> list[ClaimDocument]:
        """Get all claims for a patient."""
        from app.db.mongo import get_database
        
        db = await get_database()
        claims_collection = db["claims"]
        
        cursor = claims_collection.find({"patient_id": patient_id, "is_deleted": False})
        docs = await cursor.to_list(length=None)
        
        return [ClaimDocument.model_validate(doc) for doc in docs]

    async def get_claim(self, claim_id: str) -> ClaimDocument | None:
        """Get a specific claim."""
        from app.db.mongo import get_database
        
        db = await get_database()
        claims_collection = db["claims"]
        
        doc = await claims_collection.find_one({"_id": claim_id, "is_deleted": False})
        return ClaimDocument.model_validate(doc) if doc else None
