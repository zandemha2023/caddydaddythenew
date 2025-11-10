"""Job tracking endpoints."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.base import get_db
from app.models.job import Job
from app.schemas.job import JobResponse

router = APIRouter()


@router.get("/", response_model=List[JobResponse])
async def list_jobs(
    design_id: str = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
) -> List[Job]:
    """List all jobs, optionally filtered by design."""
    query = select(Job)

    if design_id:
        query = query.where(Job.design_id == design_id)

    query = query.offset(skip).limit(limit).order_by(Job.created_at.desc())
    result = await db.execute(query)
    return list(result.scalars().all())


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: str,
    db: AsyncSession = Depends(get_db)
) -> Job:
    """Get a specific job status."""
    result = await db.execute(
        select(Job).where(Job.id == job_id)
    )
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.delete("/{job_id}", status_code=204)
async def cancel_job(
    job_id: str,
    db: AsyncSession = Depends(get_db)
) -> None:
    """Cancel a job."""
    from app.models.job import JobStatus

    result = await db.execute(
        select(Job).where(Job.id == job_id)
    )
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
        raise HTTPException(status_code=400, detail="Job cannot be cancelled")

    job.status = JobStatus.CANCELLED
    await db.commit()
