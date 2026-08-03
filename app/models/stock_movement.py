import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, Integer, ForeignKey, CheckConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class StockMovement(Base):
    __tablename__ = "stock_movements"
    __table_args__ = (
        CheckConstraint("movement_type IN ('in', 'out')", name="ck_movement_type"),
        CheckConstraint("quantity > 0", name="ck_quantity_positive"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    movement_type: Mapped[str] = mapped_column(String(16), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer(), nullable=False)
    reason: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
