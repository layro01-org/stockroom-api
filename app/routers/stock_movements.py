import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import verify_api_key
from app.database import get_db
from app.models.product import Product
from app.models.stock_movement import StockMovement
from app.schemas.stock_movement import StockMovementCreate, StockMovementResponse

router = APIRouter()


@router.get("", response_model=List[StockMovementResponse], dependencies=[Depends(verify_api_key)])
async def list_stock_movements(
    product_id: Optional[uuid.UUID] = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(StockMovement).order_by(StockMovement.created_at.desc())
    if product_id is not None:
        stmt = stmt.where(StockMovement.product_id == product_id)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("", response_model=StockMovementResponse, status_code=201, dependencies=[Depends(verify_api_key)])
async def create_stock_movement(
    payload: StockMovementCreate,
    db: AsyncSession = Depends(get_db),
):
    # Load the product
    result = await db.execute(select(Product).where(Product.id == payload.product_id))
    product = result.scalar_one_or_none()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    # Adjust quantity
    if payload.movement_type == "in":
        product.quantity_in_stock += payload.quantity
    else:  # "out"
        if product.quantity_in_stock < payload.quantity:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Insufficient stock: requested {payload.quantity}, "
                    f"available {product.quantity_in_stock}"
                ),
            )
        product.quantity_in_stock -= payload.quantity

    # Record the movement
    movement = StockMovement(
        product_id=payload.product_id,
        movement_type=payload.movement_type,
        quantity=payload.quantity,
        reason=payload.reason,
    )
    db.add(movement)
    await db.commit()
    await db.refresh(movement)
    return movement
