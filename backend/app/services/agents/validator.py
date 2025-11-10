"""Validator agent for checking design manufacturability."""
from typing import Dict, Any
import json
import structlog

from app.services.agents.base_agent import BaseAgent

logger = structlog.get_logger()


class ValidatorAgent(BaseAgent):
    """Validator agent that checks designs for manufacturability and errors."""

    def __init__(self) -> None:
        """Initialize validator agent."""
        super().__init__("validator")

    def get_system_prompt(self) -> str:
        """Get system prompt for validator."""
        return """You are the Validator Agent for Theo CAD platform.

Your role is to:
1. Validate 3D designs for manufacturability
2. Check for common CAD errors (non-manifold geometry, intersecting faces, etc.)
3. Verify dimensional accuracy and tolerances
4. Assess printability/machinability for target manufacturing method
5. Suggest improvements and optimizations

Validation Checklist:
- Geometric validity (manifold, watertight for 3D printing)
- Dimensional accuracy
- Wall thickness (minimum thickness for method)
- Overhangs and support requirements (for 3D printing)
- Tool access (for CNC)
- Assembly feasibility
- Material compatibility

Output Format (JSON):
{
    "valid": true/false,
    "score": 0-100,
    "issues": [{"severity": "critical|warning|info", "description": "...", "suggestion": "..."}],
    "manufacturability": {
        "method": "fdm|sla|cnc|etc",
        "feasibility": "excellent|good|fair|poor",
        "estimated_time": "time estimate",
        "support_required": true/false
    },
    "recommendations": ["list of improvements"]
}"""

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate design for manufacturability.

        Args:
            input_data: Contains 'design', 'printer_type', 'requirements'

        Returns:
            Validation results and recommendations
        """
        try:
            design = input_data.get("design", {})
            printer_type = input_data.get("printer_type", "fdm")
            requirements = input_data.get("requirements", {})

            messages = [
                {
                    "role": "user",
                    "content": f"""Validate this CAD design for manufacturability:

Design Data:
{json.dumps(design, indent=2)}

Target Manufacturing Method: {printer_type}

Requirements:
{json.dumps(requirements, indent=2)}

Perform a thorough validation and provide detailed feedback in JSON format."""
                }
            ]

            response = await self.send_message(messages)
            validation_text = self.extract_text_content(response)

            # Try to extract JSON from response
            try:
                start_idx = validation_text.find('{')
                end_idx = validation_text.rfind('}') + 1
                if start_idx != -1 and end_idx > start_idx:
                    json_str = validation_text[start_idx:end_idx]
                    validation_data = json.loads(json_str)
                else:
                    raise ValueError("No JSON found in response")
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning("validator_json_extraction_failed", error=str(e))
                # Fallback structure
                validation_data = {
                    "valid": True,
                    "score": 75,
                    "raw_validation": validation_text,
                    "issues": []
                }

            logger.info(
                "validator_complete",
                valid=validation_data.get("valid"),
                score=validation_data.get("score")
            )
            return validation_data

        except Exception as e:
            logger.error("validator_failed", error=str(e))
            raise
