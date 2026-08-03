import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, field_validator


class StockMovementCreate(BaseModel):
    product_id: uuid.UUID
    movement_type: Literal["in", "out"]
    quantity: int
    reason: str | None = None

    @field_validator("quantity")
    @classmethod
    def quantity_must_be_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("quantity must be greater than 0")
        return v


class StockMovementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    product_id: uuid.UUID
    movement_type: str
    quantity: int
    reason: str | None
    created_at: datetime
