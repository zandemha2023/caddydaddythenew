"""Orchestrator agent for coordinating multi-agent workflow."""
from typing import Dict, Any, List
import structlog

from app.services.agents.base_agent import BaseAgent
from app.services.agents.analyzer import AnalyzerAgent
from app.services.agents.designer import DesignerAgent
from app.services.agents.validator import ValidatorAgent
from app.services.agents.exporter import ExporterAgent

logger = structlog.get_logger()


class OrchestratorAgent(BaseAgent):
    """Orchestrator agent that coordinates all other agents."""

    def __init__(self) -> None:
        """Initialize orchestrator agent."""
        super().__init__("orchestrator")
        self.analyzer = AnalyzerAgent()
        self.designer = DesignerAgent()
        self.validator = ValidatorAgent()
        self.exporter = ExporterAgent()

    def get_system_prompt(self) -> str:
        """Get system prompt for orchestrator."""
        return """You are the Orchestrator Agent for Theo, an advanced CAD platform.

Your role is to:
1. Understand user requests for 3D models and manufacturing files
2. Coordinate between specialized agents (Analyzer, Designer, Validator, Exporter)
3. Ensure smooth workflow from natural language to final CAD files
4. Handle errors and provide clear feedback to users

You work with these agents:
- Analyzer: Interprets natural language and extracts design parameters
- Designer: Creates 3D geometry based on analyzed specifications
- Validator: Checks designs for manufacturability and errors
- Exporter: Converts designs to various formats (STL, STEP, G-code, etc.)

Always maintain a structured workflow and provide detailed status updates."""

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orchestrate the complete CAD generation workflow.

        Args:
            input_data: Contains 'prompt', 'export_formats', 'printer_type', etc.

        Returns:
            Complete workflow results
        """
        try:
            prompt = input_data.get("prompt", "")
            export_formats = input_data.get("export_formats", ["stl"])
            printer_type = input_data.get("printer_type")
            parameters = input_data.get("parameters", {})

            workflow_trace = []

            # Step 1: Analyze the prompt
            logger.info("orchestrator_step", step="analyze", prompt=prompt)
            analysis_result = await self.analyzer.process({
                "prompt": prompt,
                "parameters": parameters
            })
            workflow_trace.append({
                "step": "analyze",
                "result": analysis_result
            })

            # Step 2: Design the model
            logger.info("orchestrator_step", step="design")
            design_result = await self.designer.process({
                "analysis": analysis_result,
                "prompt": prompt,
                "parameters": parameters
            })
            workflow_trace.append({
                "step": "design",
                "result": design_result
            })

            # Step 3: Validate the design
            logger.info("orchestrator_step", step="validate")
            validation_result = await self.validator.process({
                "design": design_result,
                "printer_type": printer_type,
                "requirements": analysis_result.get("requirements", {})
            })
            workflow_trace.append({
                "step": "validate",
                "result": validation_result
            })

            # Step 4: Export to requested formats
            logger.info("orchestrator_step", step="export", formats=export_formats)
            export_result = await self.exporter.process({
                "design": design_result,
                "formats": export_formats,
                "printer_type": printer_type
            })
            workflow_trace.append({
                "step": "export",
                "result": export_result
            })

            return {
                "success": True,
                "workflow_trace": workflow_trace,
                "final_result": {
                    "design_data": design_result,
                    "validation": validation_result,
                    "exports": export_result
                }
            }

        except Exception as e:
            logger.error("orchestrator_failed", error=str(e))
            return {
                "success": False,
                "error": str(e),
                "workflow_trace": workflow_trace
            }
