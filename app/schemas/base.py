from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class TimestampedModel(BaseModel):
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class BaseDocument(TimestampedModel):
    id: str | None = Field(default=None, alias="_id")
    is_deleted: bool = Field(default=False)
    deleted_at: datetime | None = None

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
    }

    def mark_deleted(self) -> None:
        self.is_deleted = True
        self.deleted_at = datetime.now(timezone.utc)
