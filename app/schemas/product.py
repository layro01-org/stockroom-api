import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class ProductCreate(BaseModel):
    sku: str
    name: str
    category_id: uuid.UUID | None = None
    description: str | None = None
    unit_price: Decimal
    quantity_in_stock: int = 0


class ProductUpdate(BaseModel):
    sku: str | None = None
    name: str | None = None
    category_id: uuid.UUID | None = None
    description: str | None = None
    unit_price: Decimal | None = None
    quantity_in_stock: int | None = None


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    sku: str
    name: str
    category_id: uuid.UUID | None
    description: str | None
    unit_price: Decimal
    quantity_in_stock: int
    created_at: datetime
    updated_at: datetime
