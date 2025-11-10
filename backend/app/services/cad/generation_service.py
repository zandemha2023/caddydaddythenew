"""CAD generation service coordinating agents and database."""
from datetime import datetime
from typing import Dict, Any
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.schemas.cad import CADGenerationRequest, CADGenerationResponse
from app.models.design import Design, DesignVersion
from app.models.job import Job, JobType, JobStatus
from app.models.project import Project
from app.services.agents.orchestrator import OrchestratorAgent
from app.services.queue.tasks import generate_cad_model

logger = structlog.get_logger()


class CADGenerationService:
    """Service for managing CAD generation workflow."""

    def __init__(self, db: AsyncSession) -> None:
        """
        Initialize CAD generation service.

        Args:
            db: Database session
        """
        self.db = db
        self.orchestrator = OrchestratorAgent()

    async def create_generation_job(
        self,
        request: CADGenerationRequest
    ) -> CADGenerationResponse:
        """
        Create a new CAD generation job.

        Args:
            request: Generation request parameters

        Returns:
            Job information
        """
        try:
            # Create or get design
            design_id = request.design_id
            if not design_id:
                # Create new design
                design = await self._create_design(request)
                design_id = design.id
            else:
                # Verify design exists
                result = await self.db.execute(
                    select(Design).where(Design.id == design_id)
                )
                design = result.scalar_one_or_none()
                if not design:
                    raise ValueError(f"Design {design_id} not found")

            # Create job record
            job = Job(
                design_id=design_id,
                job_type=JobType.DESIGN_GENERATION,
                status=JobStatus.PENDING,
                input_data={
                    "prompt": request.prompt,
                    "export_formats": [fmt.value for fmt in request.export_formats],
                    "printer_type": request.printer_type.value if request.printer_type else None,
                    "parameters": request.parameters or {}
                }
            )
            self.db.add(job)
            await self.db.commit()
            await self.db.refresh(job)

            # Queue Celery task
            task = generate_cad_model.delay(
                job_id=job.id,
                prompt=request.prompt,
                parameters={
                    "export_formats": [fmt.value for fmt in request.export_formats],
                    "printer_type": request.printer_type.value if request.printer_type else None,
                    **(request.parameters or {})
                }
            )

            # Update job with Celery task ID
            job.celery_task_id = task.id
            job.status = JobStatus.PROCESSING
            job.started_at = datetime.utcnow()
            await self.db.commit()

            logger.info(
                "cad_generation_job_queued",
                job_id=job.id,
                design_id=design_id,
                task_id=task.id
            )

            return CADGenerationResponse(
                job_id=job.id,
                design_id=design_id,
                status="queued",
                message="CAD generation job has been queued",
                estimated_time=300  # 5 minutes estimate
            )

        except Exception as e:
            logger.error("create_generation_job_failed", error=str(e))
            raise

    async def _create_design(self, request: CADGenerationRequest) -> Design:
        """
        Create a new design from request.

        Args:
            request: Generation request

        Returns:
            Created design
        """
        # Get or create default project
        project_id = request.project_id
        if not project_id:
            # Create default project
            result = await self.db.execute(
                select(Project).where(Project.name == "Default Project")
            )
            project = result.scalar_one_or_none()

            if not project:
                project = Project(
                    name="Default Project",
                    description="Auto-created project for designs",
                    owner_id="default-user"  # TODO: Replace with actual user ID
                )
                self.db.add(project)
                await self.db.commit()
                await self.db.refresh(project)

            project_id = project.id

        # Create design
        design = Design(
            project_id=project_id,
            name=f"Design - {request.prompt[:50]}",
            original_prompt=request.prompt
        )
        self.db.add(design)
        await self.db.commit()
        await self.db.refresh(design)

        return design

    async def process_generation(
        self,
        job_id: str,
        prompt: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process CAD generation using multi-agent system.

        Args:
            job_id: Job ID
            prompt: Natural language prompt
            parameters: Additional parameters

        Returns:
            Generation results
        """
        try:
            logger.info("processing_cad_generation", job_id=job_id)

            # Run orchestrator
            result = await self.orchestrator.process({
                "prompt": prompt,
                "export_formats": parameters.get("export_formats", ["stl"]),
                "printer_type": parameters.get("printer_type"),
                "parameters": parameters
            })

            # Create design version with results
            if result.get("success"):
                await self._save_design_version(job_id, result)

            return result

        except Exception as e:
            logger.error("process_generation_failed", job_id=job_id, error=str(e))
            raise

    async def _save_design_version(
        self,
        job_id: str,
        result: Dict[str, Any]
    ) -> None:
        """
        Save design version with generation results.

        Args:
            job_id: Job ID
            result: Generation results
        """
        # Get job
        job_result = await self.db.execute(
            select(Job).where(Job.id == job_id)
        )
        job = job_result.scalar_one_or_none()
        if not job or not job.design_id:
            return

        # Get design
        design_result = await self.db.execute(
            select(Design).where(Design.id == job.design_id)
        )
        design = design_result.scalar_one_or_none()
        if not design:
            return

        # Create new version
        version = DesignVersion(
            design_id=design.id,
            version_number=design.current_version + 1,
            prompt=job.input_data.get("prompt", ""),
            parameters=job.input_data.get("parameters", {}),
            cad_data=result.get("final_result", {}).get("design_data", {}),
            agent_trace=result.get("workflow_trace", [])
        )
        self.db.add(version)

        # Update design
        design.current_version = version.version_number
        await self.db.commit()

        logger.info(
            "design_version_saved",
            design_id=design.id,
            version=version.version_number
        )
