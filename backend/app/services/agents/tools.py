"""Tool definitions for Claude agents."""
from typing import List, Dict, Any


# Requirements Agent Tools
REQUIREMENTS_TOOLS = [
    {
        "name": "extract_dimensions",
        "description": "Extract dimensional requirements from natural language description. Use this when you identify specific measurements, sizes, or spatial requirements.",
        "input_schema": {
            "type": "object",
            "properties": {
                "length": {"type": "number", "description": "Length in millimeters"},
                "width": {"type": "number", "description": "Width in millimeters"},
                "height": {"type": "number", "description": "Height in millimeters"},
                "diameter": {"type": "number", "description": "Diameter in millimeters"},
                "thickness": {"type": "number", "description": "Wall thickness in millimeters"},
                "units": {"type": "string", "enum": ["mm", "cm", "m", "in", "ft"], "description": "Unit of measurement"}
            },
            "required": []
        }
    },
    {
        "name": "identify_features",
        "description": "Identify specific geometric features required in the design such as holes, fillets, chamfers, threads, etc.",
        "input_schema": {
            "type": "object",
            "properties": {
                "features": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "type": {"type": "string", "enum": ["hole", "fillet", "chamfer", "thread", "slot", "groove", "boss", "rib"]},
                            "quantity": {"type": "integer"},
                            "diameter": {"type": "number"},
                            "depth": {"type": "number"},
                            "radius": {"type": "number"},
                            "location": {"type": "string"}
                        }
                    }
                }
            },
            "required": ["features"]
        }
    },
    {
        "name": "determine_material",
        "description": "Determine the appropriate material based on functional requirements, environment, and manufacturing method.",
        "input_schema": {
            "type": "object",
            "properties": {
                "material_type": {"type": "string", "enum": ["PLA", "PETG", "ABS", "TPU", "Nylon", "Resin", "Metal", "Other"]},
                "reason": {"type": "string", "description": "Why this material was chosen"},
                "properties_required": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            },
            "required": ["material_type", "reason"]
        }
    },
    {
        "name": "set_tolerances",
        "description": "Set manufacturing tolerances for critical dimensions and fits.",
        "input_schema": {
            "type": "object",
            "properties": {
                "general_tolerance": {"type": "number", "description": "General tolerance in mm (e.g., ±0.1)"},
                "critical_tolerances": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "feature": {"type": "string"},
                            "tolerance": {"type": "number"},
                            "fit_type": {"type": "string", "enum": ["clearance", "transition", "interference"]}
                        }
                    }
                }
            },
            "required": ["general_tolerance"]
        }
    }
]

# CAD Agent Tools
CAD_TOOLS = [
    {
        "name": "generate_cadquery_code",
        "description": "Generate CadQuery Python code to create 3D geometry. Use this to produce executable parametric CAD code.",
        "input_schema": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Complete CadQuery Python code"},
                "parameters": {
                    "type": "object",
                    "description": "Dictionary of parametric values used in the code"
                },
                "description": {"type": "string", "description": "Description of what the code creates"}
            },
            "required": ["code", "parameters"]
        }
    },
    {
        "name": "generate_openscad_code",
        "description": "Generate OpenSCAD code for 3D geometry. Alternative to CadQuery for simpler designs.",
        "input_schema": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Complete OpenSCAD code"},
                "parameters": {
                    "type": "object",
                    "description": "Dictionary of parametric values"
                }
            },
            "required": ["code"]
        }
    },
    {
        "name": "add_assembly_instructions",
        "description": "Add assembly instructions for multi-part designs.",
        "input_schema": {
            "type": "object",
            "properties": {
                "parts": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "quantity": {"type": "integer"},
                            "material": {"type": "string"}
                        }
                    }
                },
                "steps": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            },
            "required": ["parts", "steps"]
        }
    }
]

# Validation Agent Tools
VALIDATION_TOOLS = [
    {
        "name": "check_printability",
        "description": "Check if the design is printable on the target printer technology.",
        "input_schema": {
            "type": "object",
            "properties": {
                "technology": {"type": "string", "enum": ["fdm", "sla", "sls", "mjf"]},
                "issues": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "severity": {"type": "string", "enum": ["critical", "warning", "info"]},
                            "issue": {"type": "string"},
                            "location": {"type": "string"},
                            "suggestion": {"type": "string"}
                        }
                    }
                },
                "supports_required": {"type": "boolean"},
                "estimated_print_time": {"type": "integer", "description": "Minutes"}
            },
            "required": ["technology", "issues"]
        }
    },
    {
        "name": "validate_dimensions",
        "description": "Validate that dimensions meet requirements and fit within printer build volume.",
        "input_schema": {
            "type": "object",
            "properties": {
                "fits_build_volume": {"type": "boolean"},
                "build_volume_usage": {"type": "number", "description": "Percentage of build volume used"},
                "dimension_errors": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            },
            "required": ["fits_build_volume"]
        }
    },
    {
        "name": "check_structural_integrity",
        "description": "Analyze structural integrity and suggest improvements.",
        "input_schema": {
            "type": "object",
            "properties": {
                "weak_points": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "location": {"type": "string"},
                            "issue": {"type": "string"},
                            "recommendation": {"type": "string"}
                        }
                    }
                },
                "min_wall_thickness": {"type": "number"},
                "stress_concentration_points": {"type": "array", "items": {"type": "string"}}
            },
            "required": []
        }
    }
]

# Export Agent Tools
EXPORT_TOOLS = [
    {
        "name": "configure_stl_export",
        "description": "Configure STL export settings for optimal quality.",
        "input_schema": {
            "type": "object",
            "properties": {
                "resolution": {"type": "string", "enum": ["low", "medium", "high", "ultra"]},
                "binary": {"type": "boolean", "description": "Use binary format (smaller file)"},
                "tolerance": {"type": "number", "description": "Tessellation tolerance in mm"}
            },
            "required": ["resolution"]
        }
    },
    {
        "name": "generate_gcode_settings",
        "description": "Generate printer-specific G-code settings.",
        "input_schema": {
            "type": "object",
            "properties": {
                "printer_profile": {"type": "string"},
                "layer_height": {"type": "number"},
                "infill_density": {"type": "integer"},
                "supports": {"type": "boolean"},
                "temperature": {
                    "type": "object",
                    "properties": {
                        "nozzle": {"type": "integer"},
                        "bed": {"type": "integer"}
                    }
                }
            },
            "required": ["printer_profile", "layer_height"]
        }
    },
    {
        "name": "optimize_for_printer",
        "description": "Optimize export settings for specific printer model.",
        "input_schema": {
            "type": "object",
            "properties": {
                "printer_model": {"type": "string"},
                "optimizations": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            },
            "required": ["printer_model"]
        }
    }
]


def get_tools_for_agent(agent_type: str) -> List[Dict[str, Any]]:
    """
    Get tool definitions for a specific agent type.

    Args:
        agent_type: Type of agent (requirements, cad, validation, export)

    Returns:
        List of tool definitions
    """
    tools_map = {
        "requirements": REQUIREMENTS_TOOLS,
        "cad": CAD_TOOLS,
        "validation": VALIDATION_TOOLS,
        "export": EXPORT_TOOLS
    }
    return tools_map.get(agent_type, [])
