"""Printer profile schemas."""
from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any, List
from decimal import Decimal

from app.models.printer_profile import PrinterTechnology, PrinterManufacturer


class PrinterProfileBase(BaseModel):
    """Base printer profile schema."""
    name: str
    manufacturer: PrinterManufacturer
    model: str
    technology: PrinterTechnology
    description: Optional[str] = None


class PrinterProfileCreate(PrinterProfileBase):
    """Schema for creating a printer profile."""
    build_volume_x: Decimal
    build_volume_y: Decimal
    build_volume_z: Decimal
    min_layer_height: Decimal
    max_layer_height: Decimal
    xy_resolution: Decimal
    dimensional_accuracy: Decimal
    supported_materials: Dict[str, Any]
    max_nozzle_temp: Optional[int] = None
    max_bed_temp: Optional[int] = None
    heated_chamber: bool = False
    max_print_speed: Optional[int] = None
    recommended_print_speed: Optional[int] = None
    auto_bed_leveling: bool = False
    filament_runout_detection: bool = False
    power_loss_recovery: bool = False
    multi_material: bool = False
    post_processing: Optional[Dict[str, Any]] = None
    compatible_slicers: List[str]
    is_industrial: bool = False


class ManufacturingParametersResponse(BaseModel):
    """Manufacturing parameters response schema."""
    wall_thickness: Decimal
    wall_line_count: int
    top_layers: int
    bottom_layers: int
    default_infill_density: int
    infill_pattern: str
    support_type: str
    print_speed: int
    default_nozzle_temp: Optional[int]
    default_bed_temp: Optional[int]

    model_config = ConfigDict(from_attributes=True)


class PrinterProfileResponse(PrinterProfileBase):
    """Printer profile response schema."""
    id: str
    build_volume_x: Decimal
    build_volume_y: Decimal
    build_volume_z: Decimal
    min_layer_height: Decimal
    max_layer_height: Decimal
    xy_resolution: Decimal
    dimensional_accuracy: Decimal
    supported_materials: Dict[str, Any]
    max_nozzle_temp: Optional[int]
    max_bed_temp: Optional[int]
    heated_chamber: bool
    max_print_speed: Optional[int]
    recommended_print_speed: Optional[int]
    auto_bed_leveling: bool
    filament_runout_detection: bool
    power_loss_recovery: bool
    multi_material: bool
    post_processing: Optional[Dict[str, Any]]
    compatible_slicers: List[str]
    is_active: bool
    is_industrial: bool
    manufacturing_parameters: Optional[ManufacturingParametersResponse] = None

    model_config = ConfigDict(from_attributes=True)


class PrintJobCreate(BaseModel):
    """Schema for creating a print job."""
    design_id: str
    printer_profile_id: str
    material: str
    material_color: Optional[str] = None
    layer_height: Decimal
    infill_density: int = 20
    support_enabled: bool = True
    notes: Optional[str] = None


class PrintJobResponse(BaseModel):
    """Print job response schema."""
    id: str
    design_id: str
    printer_profile_id: str
    status: str
    material: str
    material_color: Optional[str]
    layer_height: Decimal
    infill_density: int
    support_enabled: bool
    estimated_time: Optional[int]
    estimated_material: Optional[Decimal]
    estimated_cost: Optional[Decimal]
    notes: Optional[str]
    created_at: str
    updated_at: str

    model_config = ConfigDict(from_attributes=True)
