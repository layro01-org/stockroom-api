import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import verify_api_key
from app.database import get_db
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse

router = APIRouter()


@router.get("", response_model=List[CategoryResponse], dependencies=[Depends(verify_api_key)])
async def list_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Category))
    return result.scalars().all()


@router.post("", response_model=CategoryResponse, status_code=201, dependencies=[Depends(verify_api_key)])
async def create_category(payload: CategoryCreate, db: AsyncSession = Depends(get_db)):
    category = Category(name=payload.name, description=payload.description)
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category


@router.get("/{category_id}", response_model=CategoryResponse, dependencies=[Depends(verify_api_key)])
async def get_category(category_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.put("/{category_id}", response_model=CategoryResponse, dependencies=[Depends(verify_api_key)])
async def update_category(
    category_id: uuid.UUID,
    payload: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)

    await db.commit()
    await db.refresh(category)
    return category


@router.delete("/{category_id}", status_code=204, dependencies=[Depends(verify_api_key)])
async def delete_category(category_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")

    await db.delete(category)
    await db.commit()
