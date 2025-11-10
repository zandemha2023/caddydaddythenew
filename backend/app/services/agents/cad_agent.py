"""CAD Agent for generating 3D geometry using OpenSCAD/CadQuery."""
from typing import Dict, Any, Optional
import json
import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.agents.base_agent_enhanced import EnhancedBaseAgent

logger = structlog.get_logger()


class CADAgent(EnhancedBaseAgent):
    """CAD agent that generates 3D geometry code using CadQuery or OpenSCAD."""

    def __init__(self, db_session: Optional[AsyncSession] = None) -> None:
        """Initialize CAD agent."""
        super().__init__("cad", db_session)

    def get_system_prompt(self) -> str:
        """Get system prompt for CAD agent."""
        return """You are the CAD Agent for Theo CAD platform, an expert at creating parametric 3D models using CadQuery and OpenSCAD.

Your role is to:
1. Take requirements from the Requirements Agent
2. Generate parametric CAD code (CadQuery preferred for complex parts, OpenSCAD for simple geometries)
3. Create buildable, manufacturable designs
4. Provide assembly instructions for multi-part designs

Use the available tools to:
- generate_cadquery_code: Create parametric 3D models with CadQuery (Python)
- generate_openscad_code: Create 3D models with OpenSCAD (simpler alternative)
- add_assembly_instructions: For multi-part designs

CadQuery Best Practices:
- Start with a Workplane (e.g., cq.Workplane("XY"))
- Use parametric variables for all dimensions
- Add proper fillets and chamfers for printability
- Use .faces() and .edges() selectors carefully
- Combine operations with chaining
- Export with proper tolerances

OpenSCAD Best Practices:
- Use modules for reusable components
- Define all parameters at the top
- Use $fn for curve resolution
- Comment complex operations
- Use difference() and union() for boolean operations

Manufacturing Considerations:
- Minimum wall thickness: 1.2mm for FDM, 0.4mm for SLA
- Draft angles for easy support removal
- Avoid steep overhangs (>45° needs supports)
- Add chamfers on bottom layers for better bed adhesion
- Consider print orientation in design

Always produce complete, executable code that can be run directly."""

    async def execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute CAD agent tools.

        Args:
            tool_name: Name of the tool
            tool_input: Tool input parameters

        Returns:
            Tool execution result
        """
        logger.info("executing_cad_tool", tool=tool_name, input_keys=list(tool_input.keys()))

        if tool_name == "generate_cadquery_code":
            code = tool_input.get("code", "")
            parameters = tool_input.get("parameters", {})
            description = tool_input.get("description", "")

            # Validate code (basic check)
            if "import cadquery as cq" in code or "cq.Workplane" in code:
                return {
                    "success": True,
                    "code_type": "cadquery",
                    "code": code,
                    "parameters": parameters,
                    "description": description,
                    "line_count": len(code.split('\n')),
                    "message": "CadQuery code generated successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Invalid CadQuery code - missing required imports or Workplane"
                }

        elif tool_name == "generate_openscad_code":
            code = tool_input.get("code", "")
            parameters = tool_input.get("parameters", {})

            return {
                "success": True,
                "code_type": "openscad",
                "code": code,
                "parameters": parameters,
                "line_count": len(code.split('\n')),
                "message": "OpenSCAD code generated successfully"
            }

        elif tool_name == "add_assembly_instructions":
            parts = tool_input.get("parts", [])
            steps = tool_input.get("steps", [])

            return {
                "success": True,
                "parts_count": len(parts),
                "parts": parts,
                "steps": steps,
                "message": f"Assembly instructions added for {len(parts)} parts"
            }

        return {"success": False, "error": f"Unknown tool: {tool_name}"}

    async def process(
        self,
        input_data: Dict[str, Any],
        design_id: Optional[str] = None,
        job_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate CAD code based on requirements.

        Args:
            input_data: Contains 'requirements', 'prompt', 'parameters'
            design_id: Optional design ID for tracking
            job_id: Optional job ID for tracking

        Returns:
            Generated CAD code and metadata
        """
        try:
            requirements = input_data.get("requirements", {})
            prompt = input_data.get("prompt", "")
            parameters = input_data.get("parameters", {})

            logger.info("cad_agent_processing", requirements_keys=list(requirements.keys()))

            # Create detailed design brief
            messages = [{
                "role": "user",
                "content": f"""Generate parametric CAD code for this design:

Original Request: {prompt}

Requirements Analysis:
{json.dumps(requirements, indent=2)}

Additional Parameters:
{json.dumps(parameters, indent=2)}

Please use the tools to:
1. Generate CadQuery code (preferred) or OpenSCAD code for the 3D model
2. Include all dimensional parameters as variables
3. Add assembly instructions if this is a multi-part design

Requirements:
- All dimensions must be parametric (variables at top of code)
- Code must be executable and complete
- Add comments explaining key operations
- Consider manufacturability (wall thickness, overhangs, supports)
- Include proper fillets/chamfers for printability"""
            }]

            self.conversation_history = [{"role": "user", "content": messages[0]["content"]}]

            # Send to Claude with tools
            response = await self.send_message_with_tools(
                messages=messages,
                design_id=design_id,
                job_id=job_id
            )

            # Extract tool calls and text
            tool_calls = self.extract_tool_calls(response)
            text_response = self.extract_text_content(response)

            # Process tool calls
            cad_code = None
            code_type = None
            assembly_instructions = None
            tool_results = []

            if tool_calls:
                tool_results = await self.process_tool_calls(
                    tool_calls,
                    design_id=design_id,
                    job_id=job_id
                )

                # Extract CAD code from tool results
                for result in tool_results:
                    if isinstance(result, dict) and "content" in result:
                        try:
                            content = json.loads(result["content"])
                            if content.get("code_type") in ["cadquery", "openscad"]:
                                cad_code = content.get("code")
                                code_type = content.get("code_type")
                                logger.info("cad_code_extracted", type=code_type, lines=content.get("line_count"))
                            elif "parts" in content and "steps" in content:
                                assembly_instructions = content
                        except:
                            pass

            # Compile results
            design_data = {
                "success": cad_code is not None,
                "code_type": code_type,
                "cad_code": cad_code,
                "full_output": text_response,
                "design_type": requirements.get("object_type", "custom"),
                "parameters": {
                    **requirements.get("dimensions", {}),
                    **parameters
                },
                "features": requirements.get("features", []),
                "assembly_instructions": assembly_instructions,
                "tool_results": tool_results
            }

            if cad_code:
                logger.info("cad_agent_complete", code_type=code_type, success=True)
            else:
                logger.warning("cad_agent_no_code", text_length=len(text_response))

            return design_data

        except Exception as e:
            logger.error("cad_agent_failed", error=str(e))
            raise
