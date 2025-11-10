"""Design management endpoints."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.base import get_db
from app.models.design import Design
from app.schemas.design import DesignCreate, DesignUpdate, DesignResponse

router = APIRouter()


@router.post("/", response_model=DesignResponse, status_code=201)
async def create_design(
    design_data: DesignCreate,
    db: AsyncSession = Depends(get_db)
) -> Design:
    """Create a new design."""
    design = Design(
        project_id=design_data.project_id,
        name=design_data.name,
        description=design_data.description,
        original_prompt=design_data.original_prompt
    )
    db.add(design)
    await db.commit()
    await db.refresh(design)
    return design


@router.get("/", response_model=List[DesignResponse])
async def list_designs(
    project_id: str = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
) -> List[Design]:
    """List all designs, optionally filtered by project."""
    query = select(Design).options(selectinload(Design.versions))

    if project_id:
        query = query.where(Design.project_id == project_id)

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all())


@router.get("/{design_id}", response_model=DesignResponse)
async def get_design(
    design_id: str,
    db: AsyncSession = Depends(get_db)
) -> Design:
    """Get a specific design with all versions."""
    result = await db.execute(
        select(Design)
        .options(selectinload(Design.versions))
        .where(Design.id == design_id)
    )
    design = result.scalar_one_or_none()
    if not design:
        raise HTTPException(status_code=404, detail="Design not found")
    return design


@router.patch("/{design_id}", response_model=DesignResponse)
async def update_design(
    design_id: str,
    design_data: DesignUpdate,
    db: AsyncSession = Depends(get_db)
) -> Design:
    """Update a design."""
    result = await db.execute(
        select(Design).where(Design.id == design_id)
    )
    design = result.scalar_one_or_none()
    if not design:
        raise HTTPException(status_code=404, detail="Design not found")

    if design_data.name is not None:
        design.name = design_data.name
    if design_data.description is not None:
        design.description = design_data.description

    await db.commit()
    await db.refresh(design)
    return design
