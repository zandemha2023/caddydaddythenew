"""Agent conversation model for tracking AI agent interactions."""
from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey, Integer, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, Dict, Any, List
import uuid

from app.db.base import Base


class AgentConversation(Base):
    """Agent conversation model for tracking multi-agent interactions."""

    __tablename__ = "agent_conversations"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    design_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("designs.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    job_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("jobs.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    agent_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )  # requirements, cad, validation, export
    message_index: Mapped[int] = mapped_column(Integer, nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # user, assistant, system
    content: Mapped[str] = mapped_column(Text, nullable=False)
    tool_calls: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    tool_results: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    tokens_used: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True
    )

    # Relationships
    design: Mapped["Design"] = relationship("Design", back_populates="agent_conversations")
    job: Mapped[Optional["Job"]] = relationship("Job", back_populates="agent_conversations")

    # Composite index for efficient conversation retrieval
    __table_args__ = (
        Index('idx_conversation_design_agent', 'design_id', 'agent_type', 'message_index'),
        Index('idx_conversation_job', 'job_id', 'created_at'),
    )

    def __repr__(self) -> str:
        return f"<AgentConversation(agent={self.agent_type}, design={self.design_id}, index={self.message_index})>"
