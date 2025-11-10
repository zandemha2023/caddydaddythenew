"""Printer profiles endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.base import get_db
from app.models.printer_profile import PrinterProfile, PrinterTechnology, PrinterManufacturer
from app.schemas.printer_profile import PrinterProfileResponse
from app.services.printer_profiles import PrinterProfilesService

router = APIRouter()


@router.get("/", response_model=List[PrinterProfileResponse])
async def list_printer_profiles(
    technology: Optional[PrinterTechnology] = Query(None, description="Filter by technology"),
    manufacturer: Optional[PrinterManufacturer] = Query(None, description="Filter by manufacturer"),
    active_only: bool = Query(True, description="Only return active profiles"),
    db: AsyncSession = Depends(get_db)
) -> List[PrinterProfile]:
    """List all printer profiles with optional filtering."""
    service = PrinterProfilesService(db)
    return await service.list_profiles(
        technology=technology,
        manufacturer=manufacturer,
        active_only=active_only
    )


@router.get("/{profile_id}", response_model=PrinterProfileResponse)
async def get_printer_profile(
    profile_id: str,
    db: AsyncSession = Depends(get_db)
) -> PrinterProfile:
    """Get a specific printer profile."""
    result = await db.execute(
        select(PrinterProfile)
        .options(selectinload(PrinterProfile.manufacturing_parameters))
        .where(PrinterProfile.id == profile_id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Printer profile not found")
    return profile


@router.get("/by-name/{name}", response_model=PrinterProfileResponse)
async def get_printer_profile_by_name(
    name: str,
    db: AsyncSession = Depends(get_db)
) -> PrinterProfile:
    """Get a printer profile by name."""
    service = PrinterProfilesService(db)
    profile = await service.get_profile_by_name(name)
    if not profile:
        raise HTTPException(status_code=404, detail="Printer profile not found")

    # Load manufacturing parameters
    await db.refresh(profile, ["manufacturing_parameters"])
    return profile


@router.get("/technologies/", response_model=List[str])
async def list_technologies() -> List[str]:
    """List all available printer technologies."""
    return [tech.value for tech in PrinterTechnology]


@router.get("/manufacturers/", response_model=List[str])
async def list_manufacturers() -> List[str]:
    """List all available printer manufacturers."""
    return [mfr.value for mfr in PrinterManufacturer]


@router.post("/seed", status_code=201)
async def seed_printer_profiles(
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Seed database with default printer profiles."""
    service = PrinterProfilesService(db)
    await service.seed_default_profiles()
    return {"message": "Printer profiles seeded successfully"}
