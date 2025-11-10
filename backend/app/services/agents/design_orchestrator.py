"""Design Orchestrator for coordinating Requirements and CAD agents."""
from typing import Dict, Any, Optional, List
import structlog
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.agents.requirements_agent_v2 import RequirementsAgentV2
from app.services.agents.cad_agent_v2 import CADAgentV2
from app.api.websockets.agent_stream import agent_stream_manager
from app.models.design import Design, DesignVersion
from app.models.cad_file import CADFile, FileFormat
from app.models.agent_conversation import AgentConversation
import hashlib
from pathlib import Path

logger = structlog.get_logger()


class DesignOrchestrator:
    """Orchestrator for the complete design workflow."""

    def __init__(self, db_session: AsyncSession) -> None:
        """
        Initialize design orchestrator.

        Args:
            db_session: Database session
        """
        self.db = db_session
        self.sessions: Dict[str, Dict[str, Any]] = {}

    async def start_design_session(self, prompt: str, project_id: Optional[str] = None) -> str:
        """
        Start a new design session.

        Args:
            prompt: Initial design prompt
            project_id: Optional project ID

        Returns:
            Session ID
        """
        session_id = str(uuid.uuid4())

        # Create session state
        self.sessions[session_id] = {
            "prompt": prompt,
            "project_id": project_id,
            "status": "started",
            "conversation_history": [],
            "requirements": None,
            "design_id": None,
            "current_agent": None
        }

        logger.info("design_session_started", session_id=session_id, prompt=prompt[:100])

        # Stream initial message
        await agent_stream_manager.stream_progress(
            job_id=session_id,
            progress=0,
            stage="Session Started",
            message="Design session initiated",
            metadata={"prompt": prompt}
        )

        return session_id

    async def process_design_request(
        self,
        session_id: str,
        user_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process design request through the agent workflow.

        Args:
            session_id: Session ID
            user_message: Optional user message (for clarifications)

        Returns:
            Status and next steps
        """
        try:
            if session_id not in self.sessions:
                raise ValueError(f"Session {session_id} not found")

            session = self.sessions[session_id]

            logger.info(
                "processing_design_request",
                session_id=session_id,
                status=session["status"],
                has_message=user_message is not None
            )

            # Stream progress
            await agent_stream_manager.stream_progress(
                job_id=session_id,
                progress=10,
                stage="Requirements Analysis",
                message="Analyzing design requirements..."
            )

            # Step 1: Requirements extraction
            if session["status"] == "started" or session["status"] == "awaiting_clarification":
                requirements_result = await self._process_requirements(
                    session_id,
                    user_message or session["prompt"]
                )

                if requirements_result["status"] == "needs_clarification":
                    # Need more information
                    session["status"] = "awaiting_clarification"
                    session["current_agent"] = "requirements"

                    return {
                        "session_id": session_id,
                        "status": "awaiting_clarification",
                        "questions": requirements_result.get("questions", []),
                        "confidence": requirements_result.get("confidence", 0),
                        "message": "I need more information to proceed with the design."
                    }

                elif requirements_result["status"] == "complete":
                    # Requirements complete, proceed to CAD
                    session["requirements"] = requirements_result.get("requirements", {})
                    session["status"] = "generating_cad"
                    session["current_agent"] = "cad"

                    # Stream progress
                    await agent_stream_manager.stream_progress(
                        job_id=session_id,
                        progress=50,
                        stage="CAD Generation",
                        message="Requirements complete, generating 3D model...",
                        metadata={"requirements": session["requirements"]}
                    )

                    # Generate CAD
                    cad_result = await self._generate_cad(session_id, session["requirements"])

                    # Save to database
                    design_data = await self._save_design(
                        session_id,
                        session["prompt"],
                        session["requirements"],
                        cad_result,
                        session.get("project_id")
                    )

                    session["status"] = "complete"
                    session["design_id"] = design_data["design_id"]

                    # Stream completion
                    await agent_stream_manager.stream_completion(
                        job_id=session_id,
                        success=True,
                        result={
                            "design_id": design_data["design_id"],
                            "file_id": design_data["file_id"],
                            "file_path": cad_result["file_path"],
                            "code_lines": cad_result["code_lines"]
                        }
                    )

                    return {
                        "session_id": session_id,
                        "status": "complete",
                        "design_id": design_data["design_id"],
                        "file_id": design_data["file_id"],
                        "file_path": cad_result["file_path"],
                        "download_url": f"/api/v1/design/{session_id}/download",
                        "message": "Design complete! Your 3D model is ready for download."
                    }

            return {
                "session_id": session_id,
                "status": session["status"],
                "message": "Processing..."
            }

        except Exception as e:
            logger.error("design_request_failed", session_id=session_id, error=str(e))

            await agent_stream_manager.stream_error(
                job_id=session_id,
                error=str(e),
                agent=session.get("current_agent"),
                recoverable=False
            )

            raise

    async def _process_requirements(
        self,
        session_id: str,
        user_input: str
    ) -> Dict[str, Any]:
        """
        Process requirements extraction.

        Args:
            session_id: Session ID
            user_input: User input

        Returns:
            Requirements result
        """
        session = self.sessions[session_id]

        # Add to conversation history
        session["conversation_history"].append({
            "role": "user",
            "content": user_input
        })

        # Create requirements agent
        req_agent = RequirementsAgentV2(session_id=session_id)

        # Process
        result = await req_agent.process({
            "prompt": user_input,
            "conversation_history": session["conversation_history"][:-1]  # Exclude current message
        })

        # Add agent response to history
        if result.get("questions"):
            session["conversation_history"].append({
                "role": "assistant",
                "content": "\n".join(result["questions"])
            })

        return result

    async def _generate_cad(
        self,
        session_id: str,
        requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate CAD model.

        Args:
            session_id: Session ID
            requirements: Design requirements

        Returns:
            CAD generation result
        """
        # Create CAD agent
        cad_agent = CADAgentV2(session_id=session_id)

        # Generate
        result = await cad_agent.process({
            "requirements": requirements
        })

        return result

    async def _save_design(
        self,
        session_id: str,
        original_prompt: str,
        requirements: Dict[str, Any],
        cad_result: Dict[str, Any],
        project_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Save design to database.

        Args:
            session_id: Session ID
            original_prompt: Original user prompt
            requirements: Extracted requirements
            cad_result: CAD generation result
            project_id: Optional project ID

        Returns:
            Design data with IDs
        """
        try:
            # Create or get project
            if not project_id:
                from app.models.project import Project
                project = Project(
                    name="Quick Designs",
                    description="Designs created without a specific project",
                    owner_id="default-user"  # TODO: Get from auth
                )
                self.db.add(project)
                await self.db.flush()
                project_id = project.id

            # Create design
            design = Design(
                project_id=project_id,
                name=f"Design - {original_prompt[:50]}",
                description=requirements.get("functional_description", ""),
                original_prompt=original_prompt
            )
            self.db.add(design)
            await self.db.flush()

            # Create design version
            version = DesignVersion(
                design_id=design.id,
                version_number=1,
                prompt=original_prompt,
                parameters=requirements,
                cad_data={"code": cad_result.get("code", "")},
                agent_trace={
                    "requirements": requirements,
                    "retries": cad_result.get("retries", 0),
                    "code_lines": cad_result.get("code_lines", 0)
                }
            )
            self.db.add(version)
            await self.db.flush()

            # Create CAD file record
            file_path = Path(cad_result["file_path"])

            # Calculate checksum
            with open(file_path, 'rb') as f:
                checksum = hashlib.sha256(f.read()).hexdigest()

            cad_file = CADFile(
                design_version_id=version.id,
                filename=file_path.name,
                file_format=FileFormat.STL,
                file_path=str(file_path),
                file_size=file_path.stat().st_size,
                checksum=checksum,
                is_primary=True,
                metadata={
                    "session_id": session_id,
                    "code_lines": cad_result.get("code_lines", 0)
                }
            )
            self.db.add(cad_file)

            await self.db.commit()

            logger.info(
                "design_saved",
                design_id=design.id,
                version_id=version.id,
                file_id=cad_file.id
            )

            return {
                "design_id": design.id,
                "version_id": version.id,
                "file_id": cad_file.id
            }

        except Exception as e:
            logger.error("save_design_failed", error=str(e))
            await self.db.rollback()
            raise

    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """
        Get session status.

        Args:
            session_id: Session ID

        Returns:
            Session status
        """
        if session_id not in self.sessions:
            return {"status": "not_found"}

        session = self.sessions[session_id]
        return {
            "session_id": session_id,
            "status": session["status"],
            "current_agent": session.get("current_agent"),
            "design_id": session.get("design_id"),
            "has_requirements": session.get("requirements") is not None
        }
