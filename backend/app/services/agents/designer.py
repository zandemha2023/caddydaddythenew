"""Designer agent for creating 3D CAD models."""
from typing import Dict, Any
import json
import structlog

from app.services.agents.base_agent import BaseAgent

logger = structlog.get_logger()


class DesignerAgent(BaseAgent):
    """Designer agent that creates 3D geometry from analyzed specifications."""

    def __init__(self) -> None:
        """Initialize designer agent."""
        super().__init__("designer")

    def get_system_prompt(self) -> str:
        """Get system prompt for designer."""
        return """You are the Designer Agent for Theo CAD platform.

Your role is to:
1. Take analyzed design parameters and create detailed 3D geometry
2. Generate CadQuery/OpenSCAD code for parametric models
3. Ensure proper geometric construction and feature placement
4. Optimize for manufacturability
5. Provide clear instructions for 3D model generation

You should output:
- Parametric CAD code (CadQuery preferred)
- Build instructions
- Feature descriptions
- Assembly notes if applicable

Focus on:
- Proper dimensioning and tolerances
- Manufacturable features
- Parametric design for easy modifications
- Clean, well-documented code"""

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create 3D CAD model based on analysis.

        Args:
            input_data: Contains 'analysis', 'prompt', 'parameters'

        Returns:
            Design data with CAD code and specifications
        """
        try:
            analysis = input_data.get("analysis", {})
            prompt = input_data.get("prompt", "")
            parameters = input_data.get("parameters", {})

            messages = [
                {
                    "role": "user",
                    "content": f"""Create a detailed 3D CAD model based on this analysis:

Original Request: {prompt}

Analysis:
{json.dumps(analysis, indent=2)}

Additional Parameters:
{json.dumps(parameters, indent=2)}

Generate:
1. CadQuery Python code for the 3D model
2. Detailed feature descriptions
3. Build instructions
4. Parameter definitions

Provide complete, executable code."""
                }
            ]

            response = await self.send_message(messages)
            design_output = self.extract_text_content(response)

            # Extract code blocks if present
            code_start = design_output.find('```python')
            code_end = design_output.find('```', code_start + 9)

            cad_code = ""
            if code_start != -1 and code_end != -1:
                cad_code = design_output[code_start + 9:code_end].strip()

            design_data = {
                "cad_code": cad_code,
                "full_output": design_output,
                "design_type": analysis.get("object_type", "custom"),
                "parameters": {
                    **analysis.get("primary_dimensions", {}),
                    **parameters
                },
                "features": analysis.get("features", []),
                "complexity": analysis.get("complexity", "moderate")
            }

            logger.info("designer_complete", design_type=design_data["design_type"])
            return design_data

        except Exception as e:
            logger.error("designer_failed", error=str(e))
            raise
