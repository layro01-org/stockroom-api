import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import String, Text, DateTime, Numeric, Integer, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    sku: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    category_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"), nullable=True
    )
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)
    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, default=Decimal("0")
    )
    quantity_in_stock: Mapped[int] = mapped_column(
        Integer(), nullable=False, default=0
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
