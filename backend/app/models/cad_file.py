"""CAD file model for managing generated 3D files."""
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Integer, Boolean, Index, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, Dict, Any
import uuid
import enum

from app.db.base import Base


class FileFormat(str, enum.Enum):
    """CAD file format enumeration."""
    STL = "stl"
    STEP = "step"
    OBJ = "obj"
    DXF = "dxf"
    GCODE = "gcode"
    SVG = "svg"
    SCAD = "scad"
    CADQUERY = "cq"
    THREE_MF = "3mf"
    AMF = "amf"


class CADFile(Base):
    """CAD file model for managing generated 3D files."""

    __tablename__ = "cad_files"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    design_version_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("design_versions.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    print_job_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("print_jobs.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_format: Mapped[FileFormat] = mapped_column(
        Enum(FileFormat),
        nullable=False,
        index=True
    )
    file_path: Mapped[str] = mapped_column(String(512), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)  # bytes
    checksum: Mapped[str] = mapped_column(String(64), nullable=False)  # SHA-256
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        sqlalchemy.JSON,
        nullable=True
    )  # bounds, vertex_count, face_count, etc.
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # Relationships
    design_version: Mapped["DesignVersion"] = relationship(
        "DesignVersion",
        back_populates="cad_files"
    )
    print_job: Mapped[Optional["PrintJob"]] = relationship(
        "PrintJob",
        back_populates="cad_files"
    )

    # Indexes
    __table_args__ = (
        Index('idx_cad_file_version_format', 'design_version_id', 'file_format'),
        Index('idx_cad_file_checksum', 'checksum'),
    )

    def __repr__(self) -> str:
        return f"<CADFile(filename={self.filename}, format={self.file_format})>"


# Import sqlalchemy for JSON type
import sqlalchemy
