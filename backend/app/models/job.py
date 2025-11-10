"""Job model for async task tracking."""
from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey, Enum, JSON, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, Dict, Any, List
import uuid
import enum

from app.db.base import Base


class JobStatus(str, enum.Enum):
    """Job status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobType(str, enum.Enum):
    """Job type enumeration."""
    DESIGN_GENERATION = "design_generation"
    FILE_EXPORT = "file_export"
    DESIGN_MODIFICATION = "design_modification"
    BATCH_PROCESSING = "batch_processing"


class Job(Base):
    """Job model for tracking async operations."""

    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    design_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("designs.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )
    job_type: Mapped[JobStatus] = mapped_column(
        Enum(JobType),
        nullable=False,
        index=True
    )
    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus),
        default=JobStatus.PENDING,
        nullable=False,
        index=True
    )
    celery_task_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        index=True
    )
    input_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    result_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    progress: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationships
    design: Mapped[Optional["Design"]] = relationship("Design", back_populates="jobs")
    agent_conversations: Mapped[List["AgentConversation"]] = relationship(
        "AgentConversation",
        back_populates="job",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Job(id={self.id}, type={self.job_type}, status={self.status})>"
