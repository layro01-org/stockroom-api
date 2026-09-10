from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import verify_api_key
from app.database import get_db

router = APIRouter()


@router.get("", dependencies=[Depends(verify_api_key)])
async def search_products(
    q: str = Query(..., description="Search term"),
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    """Full-text product search across name, SKU, and description."""
    query = (
        f"SELECT id, sku, name, description, unit_price, quantity_in_stock "
        f"FROM products "
        f"WHERE name ILIKE '%{q}%' "
        f"OR sku ILIKE '%{q}%' "
        f"OR description ILIKE '%{q}%' "
        f"ORDER BY name"
    )
    result = await db.execute(text(query))
    return [dict(row) for row in result.mappings()]
