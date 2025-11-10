"""Analyzer agent for interpreting natural language prompts."""
from typing import Dict, Any
import json
import structlog

from app.services.agents.base_agent import BaseAgent

logger = structlog.get_logger()


class AnalyzerAgent(BaseAgent):
    """Analyzer agent that interprets natural language and extracts design parameters."""

    def __init__(self) -> None:
        """Initialize analyzer agent."""
        super().__init__("analyzer")

    def get_system_prompt(self) -> str:
        """Get system prompt for analyzer."""
        return """You are the Analyzer Agent for Theo CAD platform.

Your role is to:
1. Parse natural language descriptions of 3D objects
2. Extract key design parameters (dimensions, features, materials, tolerances)
3. Identify the type of object and its purpose
4. Suggest manufacturing methods and constraints
5. Output structured data for the Designer Agent

Output Format (JSON):
{
    "object_type": "type of object (bracket, enclosure, gear, etc.)",
    "primary_dimensions": {"length": X, "width": Y, "height": Z},
    "features": ["list of required features"],
    "material_suggestions": ["suggested materials"],
    "tolerances": {"type": "value"},
    "manufacturing_method": "suggested method",
    "complexity": "simple|moderate|complex",
    "requirements": {
        "functional": ["functional requirements"],
        "aesthetic": ["aesthetic requirements"]
    }
}

Be precise and thorough in your analysis."""

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze natural language prompt and extract design parameters.

        Args:
            input_data: Contains 'prompt' and optional 'parameters'

        Returns:
            Structured design parameters
        """
        try:
            prompt = input_data.get("prompt", "")
            user_parameters = input_data.get("parameters", {})

            messages = [
                {
                    "role": "user",
                    "content": f"""Analyze this CAD design request and extract all relevant parameters:

Request: {prompt}

Additional Parameters: {json.dumps(user_parameters, indent=2)}

Provide a detailed analysis in JSON format."""
                }
            ]

            response = await self.send_message(messages)
            analysis_text = self.extract_text_content(response)

            # Try to extract JSON from response
            try:
                # Find JSON in the response
                start_idx = analysis_text.find('{')
                end_idx = analysis_text.rfind('}') + 1
                if start_idx != -1 and end_idx > start_idx:
                    json_str = analysis_text[start_idx:end_idx]
                    analysis_data = json.loads(json_str)
                else:
                    raise ValueError("No JSON found in response")
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning("analyzer_json_extraction_failed", error=str(e))
                # Fallback to basic structure
                analysis_data = {
                    "object_type": "custom",
                    "raw_analysis": analysis_text,
                    "parameters": user_parameters
                }

            logger.info("analyzer_complete", object_type=analysis_data.get("object_type"))
            return analysis_data

        except Exception as e:
            logger.error("analyzer_failed", error=str(e))
            raise
