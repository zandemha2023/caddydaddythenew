"""Print job model for tracking manufacturing jobs."""
from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey, Numeric, Integer, JSON, Index, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, Dict, Any, List
import uuid
import enum

from app.db.base import Base


class PrintJobStatus(str, enum.Enum):
    """Print job status enumeration."""
    QUEUED = "queued"
    PREPARING = "preparing"
    SLICING = "slicing"
    READY = "ready"
    PRINTING = "printing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PrintJob(Base):
    """Print job model for tracking manufacturing jobs."""

    __tablename__ = "print_jobs"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    design_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("designs.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    printer_profile_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("printer_profiles.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    status: Mapped[PrintJobStatus] = mapped_column(
        Enum(PrintJobStatus),
        default=PrintJobStatus.QUEUED,
        nullable=False,
        index=True
    )
    material: Mapped[str] = mapped_column(String(100), nullable=False)
    material_color: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    layer_height: Mapped[Numeric] = mapped_column(Numeric(5, 3), nullable=False)  # mm
    infill_density: Mapped[int] = mapped_column(Integer, nullable=False)  # percentage
    support_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    estimated_time: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # minutes
    estimated_material: Mapped[Optional[Numeric]] = mapped_column(
        Numeric(10, 2),
        nullable=True
    )  # grams
    estimated_cost: Mapped[Optional[Numeric]] = mapped_column(
        Numeric(10, 2),
        nullable=True
    )  # USD
    actual_time: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    gcode_file_path: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    slice_settings: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    print_settings: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
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
    design: Mapped["Design"] = relationship("Design", back_populates="print_jobs")
    printer_profile: Mapped["PrinterProfile"] = relationship(
        "PrinterProfile",
        back_populates="print_jobs"
    )
    user: Mapped["User"] = relationship("User", back_populates="print_jobs")
    cad_files: Mapped[List["CADFile"]] = relationship(
        "CADFile",
        back_populates="print_job"
    )

    # Indexes
    __table_args__ = (
        Index('idx_print_job_user_status', 'user_id', 'status'),
        Index('idx_print_job_created', 'created_at'),
    )

    def __repr__(self) -> str:
        return f"<PrintJob(id={self.id}, status={self.status}, printer={self.printer_profile_id})>"


# Import Boolean and Numeric
from sqlalchemy import Boolean, Numeric
