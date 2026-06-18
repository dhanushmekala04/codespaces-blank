from typing import Any, Generic, TypeVar

from motor.motor_asyncio import AsyncIOMotorCollection

from app.db.mongo import get_database
from app.schemas.base import BaseDocument

T = TypeVar("T", bound=BaseDocument)


class BaseRepository(Generic[T]):
    def __init__(self, collection_name: str, model_cls: type[T]):
        self.collection_name = collection_name
        self.model_cls = model_cls

    async def _collection(self) -> AsyncIOMotorCollection:
        db = await get_database()
        return db[self.collection_name]

    async def create(self, document: T) -> T:
        collection = await self._collection()
        doc = document.model_dump(by_alias=True, exclude_none=True)
        result = await collection.insert_one(doc)
        document.id = str(result.inserted_id)
        return document

    async def get_by_id(self, id: str) -> T | None:
        collection = await self._collection()
        doc = await collection.find_one({"_id": id, "is_deleted": False})
        if not doc:
            return None
        return self.model_cls.model_validate(doc)

    async def update(self, id: str, updates: dict[str, Any]) -> T | None:
        collection = await self._collection()
        await collection.update_one(
            {"_id": id, "is_deleted": False},
            {"$set": updates},
        )
        return await self.get_by_id(id)

    async def delete(self, id: str) -> bool:
        collection = await self._collection()
        result = await collection.update_one(
            {"_id": id, "is_deleted": False},
            {"$set": {"is_deleted": True}},
        )
        return result.modified_count > 0

    async def list(self, filters: dict[str, Any] | None = None) -> list[T]:
        filters = filters or {}
        filters["is_deleted"] = False
        collection = await self._collection()
        docs = await collection.find(filters).to_list(length=None)
        return [self.model_cls.model_validate(doc) for doc in docs]
