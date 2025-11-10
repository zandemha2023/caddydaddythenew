"""Design and DesignVersion models."""
from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional, Dict, Any
import uuid

from app.db.base import Base


class Design(Base):
    """Design model for CAD projects."""

    __tablename__ = "designs"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    project_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    original_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    current_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
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
    project: Mapped["Project"] = relationship("Project", back_populates="designs")
    versions: Mapped[List["DesignVersion"]] = relationship(
        "DesignVersion",
        back_populates="design",
        cascade="all, delete-orphan",
        order_by="DesignVersion.version_number.desc()"
    )
    jobs: Mapped[List["Job"]] = relationship(
        "Job",
        back_populates="design",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Design(id={self.id}, name={self.name}, version={self.current_version})>"


class DesignVersion(Base):
    """Design version model for tracking design history."""

    __tablename__ = "design_versions"

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
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    parameters: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    cad_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    file_paths: Mapped[Optional[Dict[str, str]]] = mapped_column(JSON, nullable=True)
    agent_trace: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # Relationships
    design: Mapped["Design"] = relationship("Design", back_populates="versions")

    def __repr__(self) -> str:
        return f"<DesignVersion(id={self.id}, design_id={self.design_id}, version={self.version_number})>"
