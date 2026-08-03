import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import verify_api_key
from app.database import get_db
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse

router = APIRouter()


@router.get("", response_model=List[ProductResponse], dependencies=[Depends(verify_api_key)])
async def list_products(
    category_id: Optional[uuid.UUID] = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Product)
    if category_id is not None:
        stmt = stmt.where(Product.category_id == category_id)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("", response_model=ProductResponse, status_code=201, dependencies=[Depends(verify_api_key)])
async def create_product(payload: ProductCreate, db: AsyncSession = Depends(get_db)):
    product = Product(
        sku=payload.sku,
        name=payload.name,
        category_id=payload.category_id,
        description=payload.description,
        unit_price=payload.unit_price,
        quantity_in_stock=payload.quantity_in_stock,
    )
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product


@router.get("/{product_id}", response_model=ProductResponse, dependencies=[Depends(verify_api_key)])
async def get_product(product_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.put("/{product_id}", response_model=ProductResponse, dependencies=[Depends(verify_api_key)])
async def update_product(
    product_id: uuid.UUID,
    payload: ProductUpdate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)

    await db.commit()
    await db.refresh(product)
    return product


@router.delete("/{product_id}", status_code=204, dependencies=[Depends(verify_api_key)])
async def delete_product(product_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    await db.delete(product)
    await db.commit()
