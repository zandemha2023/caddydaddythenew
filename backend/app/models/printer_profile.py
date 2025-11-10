"""Printer profile model for printer specifications."""
from datetime import datetime
from sqlalchemy import String, Text, DateTime, Numeric, Integer, JSON, Boolean, Index, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, Dict, Any, List
import uuid
import enum

from app.db.base import Base


class PrinterTechnology(str, enum.Enum):
    """Printer technology enumeration."""
    FDM = "fdm"  # Fused Deposition Modeling
    SLA = "sla"  # Stereolithography
    SLS = "sls"  # Selective Laser Sintering
    MJF = "mjf"  # Multi Jet Fusion
    BINDER_JET = "binder_jet"
    DMLS = "dmls"  # Direct Metal Laser Sintering
    POLYJET = "polyjet"


class PrinterManufacturer(str, enum.Enum):
    """Printer manufacturer enumeration."""
    # FDM
    PRUSA = "prusa"
    BAMBU_LAB = "bambu_lab"
    CREALITY = "creality"
    ULTIMAKER = "ultimaker"
    MAKERBOT = "makerbot"
    # SLA
    FORMLABS = "formlabs"
    ELEGOO = "elegoo"
    ANYCUBIC = "anycubic"
    PHROZEN = "phrozen"
    # Industrial
    STRATASYS = "stratasys"
    EOS = "eos"
    HP = "hp"
    MARKFORGED = "markforged"
    CUSTOM = "custom"


class PrinterProfile(Base):
    """Printer profile model with specifications and capabilities."""

    __tablename__ = "printer_profiles"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    manufacturer: Mapped[PrinterManufacturer] = mapped_column(
        Enum(PrinterManufacturer),
        nullable=False,
        index=True
    )
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    technology: Mapped[PrinterTechnology] = mapped_column(
        Enum(PrinterTechnology),
        nullable=False,
        index=True
    )

    # Build volume (mm)
    build_volume_x: Mapped[Numeric] = mapped_column(Numeric(10, 2), nullable=False)
    build_volume_y: Mapped[Numeric] = mapped_column(Numeric(10, 2), nullable=False)
    build_volume_z: Mapped[Numeric] = mapped_column(Numeric(10, 2), nullable=False)

    # Resolution and tolerances
    min_layer_height: Mapped[Numeric] = mapped_column(Numeric(5, 3), nullable=False)  # mm
    max_layer_height: Mapped[Numeric] = mapped_column(Numeric(5, 3), nullable=False)  # mm
    xy_resolution: Mapped[Numeric] = mapped_column(Numeric(5, 3), nullable=False)  # mm
    dimensional_accuracy: Mapped[Numeric] = mapped_column(
        Numeric(5, 3),
        nullable=False
    )  # ± mm

    # Supported materials
    supported_materials: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        nullable=False
    )  # {material_name: {properties}}

    # Temperature capabilities (for FDM)
    max_nozzle_temp: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # °C
    max_bed_temp: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # °C
    heated_chamber: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Print speeds
    max_print_speed: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # mm/s
    recommended_print_speed: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )  # mm/s

    # Features
    auto_bed_leveling: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    filament_runout_detection: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    power_loss_recovery: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    multi_material: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Manufacturing parameters
    manufacturing_parameters: Mapped["ManufacturingParameters"] = relationship(
        "ManufacturingParameters",
        back_populates="printer_profile",
        uselist=False,
        cascade="all, delete-orphan"
    )

    # Post-processing requirements
    post_processing: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        nullable=True
    )  # {washing, curing, support_removal, etc.}

    # Slicing software compatibility
    compatible_slicers: Mapped[List[str]] = mapped_column(
        JSON,
        nullable=False
    )  # PrusaSlicer, Cura, etc.

    # Custom settings
    default_profile_settings: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True
    )

    # Metadata
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_industrial: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

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
    print_jobs: Mapped[List["PrintJob"]] = relationship(
        "PrintJob",
        back_populates="printer_profile"
    )

    # Indexes
    __table_args__ = (
        Index('idx_printer_profile_tech_mfr', 'technology', 'manufacturer'),
        Index('idx_printer_profile_active', 'is_active'),
    )

    def __repr__(self) -> str:
        return f"<PrinterProfile(name={self.name}, tech={self.technology}, mfr={self.manufacturer})>"
