"""CAD Agent for generating CadQuery code and 3D models."""
from typing import Dict, Any, Optional
import json
import structlog
import tempfile
import os
from pathlib import Path
import hashlib

from app.services.agents.base_agent import BaseAgent
from app.api.websockets.agent_stream import agent_stream_manager
from app.core.config import settings

logger = structlog.get_logger()


class CADAgentV2(BaseAgent):
    """CAD agent that generates CadQuery code and creates 3D models."""

    def __init__(self, session_id: Optional[str] = None) -> None:
        """
        Initialize CAD agent.

        Args:
            session_id: Session ID for WebSocket streaming
        """
        super().__init__("cad_v2")
        self.session_id = session_id
        self.max_retries = 3

    def get_system_prompt(self) -> str:
        """Get system prompt for CAD agent."""
        return """You are an expert CAD designer using CadQuery (Python-based parametric CAD). Generate 3D models from design requirements.

CadQuery Quick Reference:
- Import: import cadquery as cq
- Workplane: cq.Workplane("XY"), cq.Workplane("YZ"), cq.Workplane("XZ")
- Basic shapes: .box(length, width, height), .cylinder(height, radius), .sphere(radius)
- Operations: .union(), .cut(), .intersect()
- Features: .hole(diameter, depth), .cboreHole(diameter, cbore_diameter, cbore_depth)
- Fillets: .fillet(radius) on edges
- Chamfers: .chamfer(length) on edges
- Edge selection: .edges("|Z"), .edges(">X"), .edges("#Z")
- Face selection: .faces(">Z"), .faces("<Z"), .faces("|X")

Rules for generating code:
1. Write clean, parametric CadQuery code
2. Add comments explaining each design decision
3. Build progressively: base geometry → features → details → fillets
4. Use proper tolerances for 3D printing (account for 0.2mm printer tolerance)
5. Follow best practices:
   - Chamfers on sharp edges (0.5-1mm)
   - Draft angles for better prints (1-2°)
   - Minimum wall thickness 1.2mm for FDM, 0.8mm for SLA
   - Avoid overhangs > 45° without supports
   - Add fillets for strength and printability (1-2mm)
6. Consider print orientation (minimize supports)
7. For holes: subtract 0.2mm from desired diameter for FDM printing
8. Use variables for all dimensions at the top

Code Structure:
```python
import cadquery as cq

# Parameters (all dimensions in mm)
length = 50
width = 30
height = 20
hole_diameter = 5
fillet_radius = 2

# Base geometry
result = cq.Workplane("XY").box(length, width, height)

# Add features (holes, slots, etc.)
result = result.faces(">Z").workplane().hole(hole_diameter)

# Fillets for printability
result = result.edges("|Z").fillet(fillet_radius)

# Export (required - do not remove)
result
```

CRITICAL:
- Always end with just `result` on the last line (this is how CadQuery exports)
- Use relative positioning (.faces(), .edges()) not absolute coordinates when possible
- Test overhangs: anything > 45° from vertical needs supports
- Output ONLY executable Python code, no explanations before or after
- Do not use .show() or .exportStl() - just end with `result`

Generate production-ready, printable 3D models."""

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate CAD code from requirements.

        Args:
            input_data: Contains 'requirements' from Requirements Agent

        Returns:
            Result with generated code, file path, and metadata
        """
        try:
            requirements = input_data.get("requirements", {})
            logger.info("cad_agent_processing", requirements_keys=list(requirements.keys()))

            # Stream thinking
            if self.session_id:
                await agent_stream_manager.stream_agent_thinking(
                    job_id=self.session_id,
                    agent_type="cad",
                    thinking="Analyzing requirements and planning 3D model structure...",
                    metadata={"step": "planning"}
                )

            # Generate code with retries
            code = None
            execution_result = None
            retry_count = 0

            while retry_count < self.max_retries:
                try:
                    # Generate CadQuery code
                    code = await self._generate_code(requirements, retry_count)

                    # Stream code generation
                    if self.session_id:
                        await agent_stream_manager.stream_code_generation(
                            job_id=self.session_id,
                            code_type="cadquery",
                            code=code,
                            line_count=len(code.split('\n'))
                        )

                    # Execute code
                    execution_result = await self._execute_code(code)

                    # Success!
                    break

                except Exception as e:
                    retry_count += 1
                    logger.warning(
                        "code_execution_failed",
                        attempt=retry_count,
                        error=str(e)
                    )

                    if self.session_id:
                        await agent_stream_manager.stream_agent_thinking(
                            job_id=self.session_id,
                            agent_type="cad",
                            thinking=f"Code execution failed, attempting fix (attempt {retry_count}/{self.max_retries}): {str(e)}",
                            metadata={"attempt": retry_count, "error": str(e)}
                        )

                    if retry_count >= self.max_retries:
                        raise Exception(f"Failed to generate valid code after {self.max_retries} attempts: {str(e)}")

            # Export to STL
            stl_path = await self._export_stl(execution_result, self.session_id or "default")

            # Stream completion
            if self.session_id:
                await agent_stream_manager.stream_progress(
                    job_id=self.session_id,
                    progress=100,
                    stage="CAD Generation Complete",
                    message="3D model generated and exported to STL",
                    metadata={
                        "file_path": stl_path,
                        "code_lines": len(code.split('\n')),
                        "retries": retry_count
                    }
                )

            return {
                "success": True,
                "code": code,
                "file_path": stl_path,
                "code_lines": len(code.split('\n')),
                "retries": retry_count,
                "requirements": requirements
            }

        except Exception as e:
            logger.error("cad_agent_failed", error=str(e))

            if self.session_id:
                await agent_stream_manager.stream_error(
                    job_id=self.session_id,
                    error=f"CAD generation failed: {str(e)}",
                    agent="cad",
                    recoverable=False
                )

            raise

    async def _generate_code(self, requirements: Dict[str, Any], retry_attempt: int = 0) -> str:
        """
        Generate CadQuery code from requirements.

        Args:
            requirements: Design requirements
            retry_attempt: Number of retry attempt (0 for first try)

        Returns:
            Generated CadQuery Python code
        """
        # Build prompt
        requirements_text = json.dumps(requirements, indent=2)

        prompt = f"""Generate CadQuery Python code for this design:

Requirements:
{requirements_text}

Generate complete, executable CadQuery code. Remember:
- Import cadquery as cq
- Use parameters at the top
- Build progressively
- Add fillets and chamfers
- End with just `result`
- No explanations, just code"""

        if retry_attempt > 0:
            prompt += f"\n\nPrevious attempt {retry_attempt} failed. Please fix the code and ensure it's valid CadQuery syntax."

        messages = [{"role": "user", "content": prompt}]

        # Stream thinking
        if self.session_id:
            await agent_stream_manager.stream_agent_thinking(
                job_id=self.session_id,
                agent_type="cad",
                thinking=f"Generating CadQuery code (attempt {retry_attempt + 1})...",
                metadata={"attempt": retry_attempt + 1}
            )

        # Get response from Claude
        response = await self.send_message(messages)
        response_text = self.extract_text_content(response)

        # Extract code from response (might be in markdown)
        code = self._extract_code(response_text)

        logger.info("code_generated", lines=len(code.split('\n')), attempt=retry_attempt)

        return code

    def _extract_code(self, response: str) -> str:
        """
        Extract Python code from response.

        Args:
            response: Claude's response

        Returns:
            Extracted Python code
        """
        # Try to find code in markdown blocks
        if "```python" in response:
            start = response.find("```python") + 9
            end = response.find("```", start)
            if end > start:
                return response[start:end].strip()

        if "```" in response:
            start = response.find("```") + 3
            end = response.find("```", start)
            if end > start:
                return response[start:end].strip()

        # If no markdown, try to find import cadquery
        if "import cadquery" in response:
            # Find the start of code
            lines = response.split('\n')
            code_lines = []
            in_code = False

            for line in lines:
                if "import cadquery" in line:
                    in_code = True
                if in_code:
                    code_lines.append(line)

            return '\n'.join(code_lines).strip()

        # Return as-is if nothing else works
        return response.strip()

    async def _execute_code(self, code: str) -> Any:
        """
        Execute CadQuery code and return result.

        Args:
            code: CadQuery Python code

        Returns:
            CadQuery result object

        Raises:
            Exception: If code execution fails
        """
        try:
            logger.info("executing_cadquery_code", lines=len(code.split('\n')))

            # Create execution environment
            exec_globals = {"__name__": "__main__"}
            exec_locals = {}

            # Execute the code
            exec(code, exec_globals, exec_locals)

            # Get result (should be last variable or 'result')
            if 'result' in exec_locals:
                result = exec_locals['result']
            else:
                # Get last defined variable
                result = exec_locals[list(exec_locals.keys())[-1]]

            logger.info("code_executed_successfully")
            return result

        except Exception as e:
            logger.error("code_execution_failed", error=str(e), code=code[:200])
            raise Exception(f"CadQuery execution failed: {str(e)}")

    async def _export_stl(self, cad_result: Any, session_id: str) -> str:
        """
        Export CadQuery result to STL file.

        Args:
            cad_result: CadQuery result object
            session_id: Session ID for file naming

        Returns:
            Path to STL file
        """
        try:
            # Create output directory
            output_dir = Path(settings.OUTPUT_DIR)
            output_dir.mkdir(parents=True, exist_ok=True)

            # Generate filename
            filename = f"{session_id}.stl"
            file_path = output_dir / filename

            logger.info("exporting_stl", path=str(file_path))

            # Export to STL
            import cadquery as cq
            cq.exporters.export(cad_result, str(file_path))

            logger.info("stl_exported", path=str(file_path), size=file_path.stat().st_size)

            return str(file_path)

        except Exception as e:
            logger.error("stl_export_failed", error=str(e))
            raise Exception(f"STL export failed: {str(e)}")
