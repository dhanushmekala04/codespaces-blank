from datetime import datetime, timezone

from app.repositories.base import BaseRepository
from app.schemas.audit import AuditLogDocument


class AuditRepository(BaseRepository[AuditLogDocument]):
    def __init__(self):
        super().__init__(collection_name="audit_logs", model_cls=AuditLogDocument)

    async def get_by_request(self, request_id: str) -> list[AuditLogDocument]:
        """Get all audit log entries for a given request."""
        collection = await self._collection()
        cursor = collection.find(
            {"request_id": request_id, "is_deleted": False}
        ).sort("created_at", 1)
        docs = await cursor.to_list(length=None)
        return [self.model_cls.model_validate(doc) for doc in docs]

    async def get_by_actor(self, actor_id: str, limit: int = 100) -> list[AuditLogDocument]:
        """Get recent audit entries for a specific actor."""
        collection = await self._collection()
        cursor = (
            collection.find({"actor_id": actor_id, "is_deleted": False})
            .sort("created_at", -1)
            .limit(limit)
        )
        docs = await cursor.to_list(length=limit)
        return [self.model_cls.model_validate(doc) for doc in docs]

    async def get_by_action(self, action: str, limit: int = 100) -> list[AuditLogDocument]:
        """Get recent audit entries for a specific action type."""
        collection = await self._collection()
        cursor = (
            collection.find({"action": action, "is_deleted": False})
            .sort("created_at", -1)
            .limit(limit)
        )
        docs = await cursor.to_list(length=limit)
        return [self.model_cls.model_validate(doc) for doc in docs]

    async def get_failed_events(self, limit: int = 100) -> list[AuditLogDocument]:
        """Get recent failed audit events for monitoring."""
        collection = await self._collection()
        cursor = (
            collection.find({"outcome": "failure", "is_deleted": False})
            .sort("created_at", -1)
            .limit(limit)
        )
        docs = await cursor.to_list(length=limit)
        return [self.model_cls.model_validate(doc) for doc in docs]
