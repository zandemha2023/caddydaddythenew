"""Exporter agent for converting designs to various formats."""
from typing import Dict, Any, List
import json
import structlog

from app.services.agents.base_agent import BaseAgent

logger = structlog.get_logger()


class ExporterAgent(BaseAgent):
    """Exporter agent that converts designs to various manufacturing file formats."""

    def __init__(self) -> None:
        """Initialize exporter agent."""
        super().__init__("exporter")

    def get_system_prompt(self) -> str:
        """Get system prompt for exporter."""
        return """You are the Exporter Agent for Theo CAD platform.

Your role is to:
1. Convert CAD designs to various file formats
2. Generate printer-specific configurations
3. Optimize exports for different manufacturing methods
4. Provide instructions for using exported files

Supported Formats:
- STL: Standard for 3D printing
- STEP: Industry standard CAD interchange
- OBJ: General 3D format with textures
- DXF: 2D/3D CAD format
- GCODE: Direct printer instructions
- SVG: 2D vector graphics

For each format, provide:
- Export parameters
- Format-specific optimizations
- Usage instructions
- File metadata"""

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Export design to requested formats.

        Args:
            input_data: Contains 'design', 'formats', 'printer_type'

        Returns:
            Export results and file information
        """
        try:
            design = input_data.get("design", {})
            formats = input_data.get("formats", ["stl"])
            printer_type = input_data.get("printer_type", "fdm")

            messages = [
                {
                    "role": "user",
                    "content": f"""Generate export instructions for this CAD design:

Design Data:
{json.dumps(design, indent=2)}

Target Formats: {', '.join(formats)}
Printer Type: {printer_type}

For each format, provide:
1. Export parameters (resolution, units, etc.)
2. Format-specific optimizations
3. File naming conventions
4. Usage instructions

Provide detailed export plan in JSON format."""
                }
            ]

            response = await self.send_message(messages)
            export_text = self.extract_text_content(response)

            # Try to extract JSON from response
            try:
                start_idx = export_text.find('{')
                end_idx = export_text.rfind('}') + 1
                if start_idx != -1 and end_idx > start_idx:
                    json_str = export_text[start_idx:end_idx]
                    export_data = json.loads(json_str)
                else:
                    raise ValueError("No JSON found in response")
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning("exporter_json_extraction_failed", error=str(e))
                # Fallback structure
                export_data = {
                    "formats": formats,
                    "raw_export_plan": export_text,
                    "files": {fmt: f"output.{fmt}" for fmt in formats}
                }

            # Add metadata
            export_data["export_count"] = len(formats)
            export_data["printer_type"] = printer_type

            logger.info("exporter_complete", formats=formats)
            return export_data

        except Exception as e:
            logger.error("exporter_failed", error=str(e))
            raise
