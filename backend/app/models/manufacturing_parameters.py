"""Manufacturing parameters model for printer-specific settings."""
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Numeric, Integer, JSON, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, Dict, Any
import uuid

from app.db.base import Base


class ManufacturingParameters(Base):
    """Manufacturing parameters for specific printer profiles."""

    __tablename__ = "manufacturing_parameters"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    printer_profile_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("printer_profiles.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True
    )

    # Wall and shell settings
    wall_thickness: Mapped[Numeric] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        default=1.2
    )  # mm
    wall_line_count: Mapped[int] = mapped_column(Integer, nullable=False, default=2)
    top_layers: Mapped[int] = mapped_column(Integer, nullable=False, default=4)
    bottom_layers: Mapped[int] = mapped_column(Integer, nullable=False, default=4)

    # Infill settings
    default_infill_density: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=20
    )  # percentage
    infill_pattern: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="grid"
    )  # grid, gyroid, cubic, etc.

    # Support settings
    support_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="normal"
    )  # normal, tree, organic
    support_density: Mapped[int] = mapped_column(Integer, nullable=False, default=15)  # percentage
    support_z_distance: Mapped[Numeric] = mapped_column(
        Numeric(5, 3),
        nullable=False,
        default=0.2
    )  # mm
    support_interface_layers: Mapped[int] = mapped_column(Integer, nullable=False, default=3)

    # Adhesion settings
    build_plate_adhesion: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="skirt"
    )  # skirt, brim, raft
    brim_width: Mapped[Numeric] = mapped_column(Numeric(5, 2), nullable=True)  # mm

    # Temperature settings (FDM specific)
    default_nozzle_temp: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # °C
    default_bed_temp: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # °C
    initial_layer_temp_offset: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        default=0
    )  # °C

    # Speed settings
    print_speed: Mapped[int] = mapped_column(Integer, nullable=False, default=50)  # mm/s
    travel_speed: Mapped[int] = mapped_column(Integer, nullable=False, default=150)  # mm/s
    initial_layer_speed: Mapped[int] = mapped_column(Integer, nullable=False, default=20)  # mm/s
    infill_speed: Mapped[int] = mapped_column(Integer, nullable=False, default=80)  # mm/s

    # Retraction settings
    retraction_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    retraction_distance: Mapped[Numeric] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        default=5.0
    )  # mm
    retraction_speed: Mapped[int] = mapped_column(Integer, nullable=False, default=45)  # mm/s

    # Cooling settings
    cooling_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    min_fan_speed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)  # percentage
    max_fan_speed: Mapped[int] = mapped_column(Integer, nullable=False, default=100)  # percentage

    # Quality settings
    adaptive_layer_height: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    smooth_spiralized_contours: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )  # vase mode

    # Tolerances
    horizontal_expansion: Mapped[Numeric] = mapped_column(
        Numeric(5, 3),
        nullable=False,
        default=0.0
    )  # mm
    hole_horizontal_expansion: Mapped[Numeric] = mapped_column(
        Numeric(5, 3),
        nullable=False,
        default=0.0
    )  # mm

    # Material-specific overrides
    material_overrides: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True
    )  # {material_name: {settings}}

    # Advanced settings
    advanced_settings: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True
    )  # ironing, z_seam, combing, etc.

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
    printer_profile: Mapped["PrinterProfile"] = relationship(
        "PrinterProfile",
        back_populates="manufacturing_parameters"
    )

    def __repr__(self) -> str:
        return f"<ManufacturingParameters(printer_profile_id={self.printer_profile_id})>"
