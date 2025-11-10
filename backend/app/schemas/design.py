"""Design schemas."""
from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime


class DesignBase(BaseModel):
    """Base design schema."""
    name: str
    description: Optional[str] = None


class DesignCreate(DesignBase):
    """Schema for creating a design."""
    project_id: str
    original_prompt: str


class DesignUpdate(BaseModel):
    """Schema for updating a design."""
    name: Optional[str] = None
    description: Optional[str] = None


class DesignVersionResponse(BaseModel):
    """Schema for design version responses."""
    id: str
    design_id: str
    version_number: int
    prompt: str
    parameters: Optional[Dict[str, Any]] = None
    cad_data: Optional[Dict[str, Any]] = None
    file_paths: Optional[Dict[str, str]] = None
    agent_trace: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DesignResponse(DesignBase):
    """Schema for design responses."""
    id: str
    project_id: str
    original_prompt: str
    current_version: int
    created_at: datetime
    updated_at: datetime
    versions: Optional[list[DesignVersionResponse]] = None

    model_config = ConfigDict(from_attributes=True)
