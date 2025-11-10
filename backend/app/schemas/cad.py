"""CAD-specific schemas."""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum


class ExportFormat(str, Enum):
    """Supported export formats."""
    STL = "stl"
    STEP = "step"
    OBJ = "obj"
    DXF = "dxf"
    GCODE = "gcode"
    SVG = "svg"


class PrinterType(str, Enum):
    """Supported printer types."""
    FDM = "fdm"
    SLA = "sla"
    SLS = "sls"
    CNC = "cnc"
    LASER = "laser"


class CADGenerationRequest(BaseModel):
    """Request schema for CAD generation."""
    prompt: str = Field(..., description="Natural language description of the 3D model")
    project_id: Optional[str] = Field(None, description="Project ID to associate with")
    design_id: Optional[str] = Field(None, description="Design ID for versioning")
    export_formats: List[ExportFormat] = Field(
        default=[ExportFormat.STL],
        description="Desired output formats"
    )
    printer_type: Optional[PrinterType] = Field(
        None,
        description="Target printer type for optimization"
    )
    parameters: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional parameters (dimensions, material, etc.)"
    )


class CADGenerationResponse(BaseModel):
    """Response schema for CAD generation."""
    job_id: str
    design_id: str
    status: str
    message: str
    estimated_time: Optional[int] = Field(None, description="Estimated time in seconds")


class AgentMessage(BaseModel):
    """WebSocket message from agent."""
    type: str = Field(..., description="Message type: status, progress, error, complete")
    job_id: str
    data: Dict[str, Any]
    timestamp: str
