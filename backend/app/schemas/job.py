"""Job schemas."""
from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime
from app.models.job import JobStatus, JobType


class JobBase(BaseModel):
    """Base job schema."""
    job_type: JobType


class JobCreate(JobBase):
    """Schema for creating a job."""
    design_id: Optional[str] = None
    input_data: Optional[Dict[str, Any]] = None


class JobResponse(JobBase):
    """Schema for job responses."""
    id: str
    design_id: Optional[str] = None
    status: JobStatus
    celery_task_id: Optional[str] = None
    input_data: Optional[Dict[str, Any]] = None
    result_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    progress: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
