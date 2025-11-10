"""Requirements Agent for extracting design specifications from natural language."""
from typing import Dict, Any, Optional, List
import json
import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.agents.base_agent import BaseAgent
from app.api.websockets.agent_stream import agent_stream_manager

logger = structlog.get_logger()


class RequirementsAgentV2(BaseAgent):
    """Requirements agent that extracts design specifications and asks clarifying questions."""

    def __init__(self, session_id: Optional[str] = None) -> None:
        """
        Initialize requirements agent.

        Args:
            session_id: Session ID for WebSocket streaming
        """
        super().__init__("requirements_v2")
        self.session_id = session_id
        self.conversation_history: List[Dict[str, str]] = []

    def get_system_prompt(self) -> str:
        """Get system prompt for requirements agent."""
        return """You are a senior mechanical engineer helping extract design specifications from natural language for 3D printing and CAD design.

Your role is to ask clarifying questions about:
- Dimensions and tolerances (be specific: length, width, height in mm)
- Material requirements (consider 3D printing materials: PLA, PETG, ABS, TPU, Nylon, Resin)
- Load/stress requirements (weight it needs to support, forces applied)
- Manufacturing method (FDM, SLA, SLS, CNC, etc.)
- Functional requirements (what does it need to do?)
- Assembly requirements (single part or multi-part?)
- Special features (holes, threads, slots, mounting points, cable management)
- Surface finish requirements
- Cost and timeline constraints

When you have enough information, output a JSON object with this EXACT structure:
{
  "status": "complete" or "needs_clarification",
  "confidence": 0.0 to 1.0,
  "questions": ["question 1", "question 2"] (only if needs_clarification),
  "requirements": {
    "dimensions": {"length": "50mm", "width": "30mm", "height": "20mm"},
    "material": "PLA",
    "manufacturing_method": "FDM",
    "load_requirements": {"max_load": "5kg", "direction": "vertical"},
    "tolerances": "±0.2mm",
    "special_features": ["mounting holes", "cable management"],
    "functional_description": "detailed description",
    "part_count": 1,
    "assembly_notes": "assembly instructions if multi-part"
  }
}

Rules:
1. If confidence < 0.7, set status to "needs_clarification" and ask 2-3 specific questions
2. Be conversational but thorough
3. Don't make critical assumptions about dimensions, loads, or materials
4. If user says "simple bracket" or "phone stand", ask for specific dimensions
5. Always consider 3D printing constraints (overhangs, support material, print orientation)
6. For load-bearing parts, always ask about expected weight/force
7. Output ONLY valid JSON when you have sufficient information
8. Use metric units (mm, kg, N) unless user specifies otherwise

Be helpful and guide the user to provide all necessary information for a successful 3D design."""

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process user input and extract requirements.

        Args:
            input_data: Contains 'prompt' and optional 'conversation_history'

        Returns:
            Requirements with status and optional clarifying questions
        """
        try:
            prompt = input_data.get("prompt", "")
            history = input_data.get("conversation_history", [])

            logger.info("requirements_agent_processing", prompt=prompt[:100], session=self.session_id)

            # Stream thinking
            if self.session_id:
                await agent_stream_manager.stream_agent_thinking(
                    job_id=self.session_id,
                    agent_type="requirements",
                    thinking="Analyzing design request and extracting specifications...",
                    metadata={"step": "analysis"}
                )

            # Build conversation with history
            messages = []
            if history:
                messages.extend(history)

            # Add current prompt
            messages.append({
                "role": "user",
                "content": prompt
            })

            # Send to Claude
            response = await self.send_message(messages)
            response_text = self.extract_text_content(response)

            logger.info("requirements_response", response_length=len(response_text))

            # Try to extract JSON from response
            try:
                # Find JSON in response (could be wrapped in markdown or text)
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1

                if json_start != -1 and json_end > json_start:
                    json_str = response_text[json_start:json_end]
                    requirements_data = json.loads(json_str)

                    # Validate structure
                    if "status" not in requirements_data:
                        requirements_data["status"] = "needs_clarification"
                    if "confidence" not in requirements_data:
                        requirements_data["confidence"] = 0.5

                    # Stream results
                    if self.session_id:
                        if requirements_data["status"] == "complete":
                            await agent_stream_manager.stream_progress(
                                job_id=self.session_id,
                                progress=100,
                                stage="Requirements Complete",
                                message="All design specifications extracted successfully",
                                metadata={"confidence": requirements_data["confidence"]}
                            )
                        else:
                            await agent_stream_manager.stream_agent_thinking(
                                job_id=self.session_id,
                                agent_type="requirements",
                                thinking="Need more information to proceed with design",
                                metadata={
                                    "questions": requirements_data.get("questions", []),
                                    "confidence": requirements_data["confidence"]
                                }
                            )

                    return requirements_data

                else:
                    # No JSON found, extract as text
                    logger.warning("no_json_in_response", response=response_text[:200])

                    return {
                        "status": "needs_clarification",
                        "confidence": 0.3,
                        "questions": [response_text],
                        "raw_response": response_text
                    }

            except json.JSONDecodeError as e:
                logger.error("json_decode_failed", error=str(e), text=response_text[:200])

                # Return as clarification request
                return {
                    "status": "needs_clarification",
                    "confidence": 0.3,
                    "questions": [response_text],
                    "raw_response": response_text
                }

        except Exception as e:
            logger.error("requirements_agent_failed", error=str(e))

            if self.session_id:
                await agent_stream_manager.stream_error(
                    job_id=self.session_id,
                    error=f"Requirements analysis failed: {str(e)}",
                    agent="requirements",
                    recoverable=True
                )

            raise

    async def ask_clarifying_questions(
        self,
        initial_prompt: str,
        previous_answers: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Ask clarifying questions based on initial prompt and previous answers.

        Args:
            initial_prompt: Initial user request
            previous_answers: List of previous Q&A pairs

        Returns:
            Requirements data with questions if needed
        """
        # Build conversation history
        conversation = [
            {"role": "user", "content": initial_prompt}
        ]

        for qa in previous_answers:
            conversation.append({"role": "assistant", "content": qa["question"]})
            conversation.append({"role": "user", "content": qa["answer"]})

        return await self.process({
            "prompt": "Based on our conversation, do you have all the information needed for the design?",
            "conversation_history": conversation
        })
