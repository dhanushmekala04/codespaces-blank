from app.repositories.base import BaseRepository
from app.schemas.billing import BillingDocument


class BillingRepository(BaseRepository[BillingDocument]):
    def __init__(self):
        super().__init__(collection_name="billing", model_cls=BillingDocument)
