from app.repositories.base import BaseRepository
from app.schemas.audit import AuditLogDocument


class AuditRepository(BaseRepository[AuditLogDocument]):
    def __init__(self):
        super().__init__(collection_name="audit_logs", model_cls=AuditLogDocument)
