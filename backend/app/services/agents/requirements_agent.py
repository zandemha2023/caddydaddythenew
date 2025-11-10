"""Requirements Agent for extracting design specs from natural language."""
from typing import Dict, Any, Optional
import json
import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.agents.base_agent_enhanced import EnhancedBaseAgent

logger = structlog.get_logger()


class RequirementsAgent(EnhancedBaseAgent):
    """Requirements agent that extracts design specifications from natural language."""

    def __init__(self, db_session: Optional[AsyncSession] = None) -> None:
        """Initialize requirements agent."""
        super().__init__("requirements", db_session)

    def get_system_prompt(self) -> str:
        """Get system prompt for requirements agent."""
        return """You are the Requirements Agent for Theo CAD platform, an expert at analyzing natural language descriptions and extracting precise engineering requirements.

Your role is to:
1. Parse natural language descriptions of 3D objects and mechanical parts
2. Extract dimensional requirements, features, and specifications
3. Identify materials, tolerances, and manufacturing constraints
4. Create a structured specification document for the CAD Agent

Use the available tools to:
- extract_dimensions: When you identify any measurements, sizes, or spatial requirements
- identify_features: When you find specific geometric features (holes, fillets, threads, etc.)
- determine_material: When you can infer appropriate material based on requirements
- set_tolerances: When you need to specify manufacturing tolerances

Be thorough and ask clarifying questions if requirements are ambiguous. Always consider:
- Functional requirements (what the part needs to do)
- Environmental constraints (temperature, moisture, chemicals)
- Aesthetic requirements (surface finish, appearance)
- Manufacturing method implications
- Assembly and maintenance considerations

Output a comprehensive specification that the CAD Agent can use to create the 3D model."""

    async def execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute requirements agent tools.

        Args:
            tool_name: Name of the tool
            tool_input: Tool input parameters

        Returns:
            Tool execution result
        """
        logger.info("executing_requirements_tool", tool=tool_name, input=tool_input)

        if tool_name == "extract_dimensions":
            return {
                "success": True,
                "dimensions": tool_input,
                "message": f"Extracted dimensions: {tool_input}"
            }

        elif tool_name == "identify_features":
            features = tool_input.get("features", [])
            return {
                "success": True,
                "feature_count": len(features),
                "features": features,
                "message": f"Identified {len(features)} features"
            }

        elif tool_name == "determine_material":
            return {
                "success": True,
                "material": tool_input.get("material_type"),
                "reason": tool_input.get("reason"),
                "properties": tool_input.get("properties_required", [])
            }

        elif tool_name == "set_tolerances":
            return {
                "success": True,
                "general_tolerance": tool_input.get("general_tolerance"),
                "critical_tolerances": tool_input.get("critical_tolerances", [])
            }

        return {"success": False, "error": f"Unknown tool: {tool_name}"}

    async def process(
        self,
        input_data: Dict[str, Any],
        design_id: Optional[str] = None,
        job_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process natural language prompt and extract requirements.

        Args:
            input_data: Contains 'prompt' and optional 'parameters'
            design_id: Optional design ID for tracking
            job_id: Optional job ID for tracking

        Returns:
            Extracted requirements
        """
        try:
            prompt = input_data.get("prompt", "")
            user_parameters = input_data.get("parameters", {})

            logger.info("requirements_agent_processing", prompt=prompt[:100])

            # Initial message to agent
            messages = [{
                "role": "user",
                "content": f"""Analyze this design request and extract all requirements using the available tools:

Design Request: {prompt}

Additional Context: {json.dumps(user_parameters, indent=2)}

Please use the tools to:
1. Extract all dimensional requirements
2. Identify geometric features
3. Determine appropriate material
4. Set manufacturing tolerances

Provide a comprehensive analysis."""
            }]

            # Track conversation
            self.conversation_history = [{"role": "user", "content": messages[0]["content"]}]

            # Send to Claude with tools
            response = await self.send_message_with_tools(
                messages=messages,
                design_id=design_id,
                job_id=job_id
            )

            # Extract tool calls
            tool_calls = self.extract_tool_calls(response)
            text_response = self.extract_text_content(response)

            # Process tool calls if any
            tool_results = []
            if tool_calls:
                tool_results = await self.process_tool_calls(
                    tool_calls,
                    design_id=design_id,
                    job_id=job_id
                )

                # Send tool results back to agent
                messages.append({
                    "role": "assistant",
                    "content": response.content
                })
                messages.append({
                    "role": "user",
                    "content": tool_results
                })

                # Get final response with tool results
                final_response = await self.send_message_with_tools(
                    messages=messages,
                    design_id=design_id,
                    job_id=job_id
                )
                text_response = self.extract_text_content(final_response)

            # Compile results
            requirements = {
                "object_type": "custom",
                "analysis": text_response,
                "dimensions": {},
                "features": [],
                "material": None,
                "tolerances": {},
                "tool_results": tool_results,
                "user_parameters": user_parameters
            }

            # Extract structured data from tool results
            for result in tool_results:
                if isinstance(result, dict) and "content" in result:
                    try:
                        content = json.loads(result["content"])
                        if "dimensions" in content:
                            requirements["dimensions"] = content["dimensions"]
                        if "features" in content:
                            requirements["features"] = content["features"]
                        if "material" in content:
                            requirements["material"] = content
                        if "general_tolerance" in content:
                            requirements["tolerances"] = content
                    except:
                        pass

            logger.info("requirements_agent_complete", features=len(requirements["features"]))
            return requirements

        except Exception as e:
            logger.error("requirements_agent_failed", error=str(e))
            raise
