"""Print jobs endpoints."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.base import get_db
from app.models.print_job import PrintJob, PrintJobStatus
from app.schemas.printer_profile import PrintJobCreate, PrintJobResponse

router = APIRouter()


@router.post("/", response_model=PrintJobResponse, status_code=201)
async def create_print_job(
    job_data: PrintJobCreate,
    db: AsyncSession = Depends(get_db)
) -> PrintJob:
    """Create a new print job."""
    # TODO: Add authentication and get user_id from token
    print_job = PrintJob(
        design_id=job_data.design_id,
        printer_profile_id=job_data.printer_profile_id,
        user_id="default-user",  # Replace with actual user ID
        material=job_data.material,
        material_color=job_data.material_color,
        layer_height=job_data.layer_height,
        infill_density=job_data.infill_density,
        support_enabled=job_data.support_enabled,
        notes=job_data.notes,
        status=PrintJobStatus.QUEUED
    )
    db.add(print_job)
    await db.commit()
    await db.refresh(print_job)
    return print_job


@router.get("/", response_model=List[PrintJobResponse])
async def list_print_jobs(
    design_id: str = None,
    status: PrintJobStatus = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
) -> List[PrintJob]:
    """List all print jobs with optional filtering."""
    query = select(PrintJob)

    if design_id:
        query = query.where(PrintJob.design_id == design_id)
    if status:
        query = query.where(PrintJob.status == status)

    query = query.offset(skip).limit(limit).order_by(PrintJob.created_at.desc())
    result = await db.execute(query)
    return list(result.scalars().all())


@router.get("/{job_id}", response_model=PrintJobResponse)
async def get_print_job(
    job_id: str,
    db: AsyncSession = Depends(get_db)
) -> PrintJob:
    """Get a specific print job."""
    result = await db.execute(
        select(PrintJob).where(PrintJob.id == job_id)
    )
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Print job not found")
    return job


@router.patch("/{job_id}/status", response_model=PrintJobResponse)
async def update_print_job_status(
    job_id: str,
    status: PrintJobStatus,
    db: AsyncSession = Depends(get_db)
) -> PrintJob:
    """Update print job status."""
    result = await db.execute(
        select(PrintJob).where(PrintJob.id == job_id)
    )
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Print job not found")

    job.status = status
    await db.commit()
    await db.refresh(job)
    return job
