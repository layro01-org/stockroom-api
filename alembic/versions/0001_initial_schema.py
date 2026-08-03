"""initial schema

Revision ID: 0001
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "categories",
        sa.Column(
            "id",
            sa.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("name", sa.String(256), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "products",
        sa.Column(
            "id",
            sa.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("sku", sa.String(128), nullable=False),
        sa.Column("name", sa.String(256), nullable=False),
        sa.Column("category_id", sa.UUID(as_uuid=True), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "unit_price",
            sa.Numeric(10, 2),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "quantity_in_stock",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["category_id"],
            ["categories.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("sku"),
    )

    op.create_table(
        "stock_movements",
        sa.Column(
            "id",
            sa.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("product_id", sa.UUID(as_uuid=True), nullable=False),
        sa.Column("movement_type", sa.String(16), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("reason", sa.String(512), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.CheckConstraint("movement_type IN ('in', 'out')", name="ck_movement_type"),
        sa.CheckConstraint("quantity > 0", name="ck_quantity_positive"),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("stock_movements")
    op.drop_table("products")
    op.drop_table("categories")
