"""Enhanced base agent class with tool use and conversation tracking."""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import structlog
from anthropic import Anthropic
from anthropic.types.message import Message
from anthropic.types.content_block import ContentBlock
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.agent_conversation import AgentConversation
from app.services.agents.tools import get_tools_for_agent

logger = structlog.get_logger()


class EnhancedBaseAgent(ABC):
    """Enhanced base class for all CAD agents with tool use support."""

    def __init__(self, agent_type: str, db_session: Optional[AsyncSession] = None) -> None:
        """
        Initialize enhanced base agent.

        Args:
            agent_type: Type of agent (requirements, cad, validation, export)
            db_session: Database session for conversation tracking
        """
        self.agent_type = agent_type
        self.db_session = db_session
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = settings.ANTHROPIC_MODEL
        self.max_tokens = settings.ANTHROPIC_MAX_TOKENS
        self.temperature = settings.ANTHROPIC_TEMPERATURE
        self.tools = get_tools_for_agent(agent_type)
        self.conversation_history: List[Dict[str, Any]] = []
        logger.info("enhanced_agent_initialized", agent=agent_type, tools_count=len(self.tools))

    async def send_message_with_tools(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        design_id: Optional[str] = None,
        job_id: Optional[str] = None,
    ) -> Message:
        """
        Send message to Claude API with tool use support.

        Args:
            messages: List of message dictionaries
            system_prompt: System prompt for the agent
            temperature: Override default temperature
            max_tokens: Override default max tokens
            design_id: Design ID for conversation tracking
            job_id: Job ID for conversation tracking

        Returns:
            Claude API response
        """
        try:
            # Track user message
            if self.db_session and design_id:
                await self._save_conversation(
                    design_id=design_id,
                    job_id=job_id,
                    message_index=len(self.conversation_history),
                    role=messages[-1].get("role", "user"),
                    content=str(messages[-1].get("content", "")),
                )

            # Send to Claude with tools
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens or self.max_tokens,
                temperature=temperature or self.temperature,
                system=system_prompt or self.get_system_prompt(),
                messages=messages,
                tools=self.tools if self.tools else None,
            )

            # Extract tool calls
            tool_calls = []
            text_content = []

            for block in response.content:
                if block.type == "tool_use":
                    tool_calls.append({
                        "id": block.id,
                        "name": block.name,
                        "input": block.input
                    })
                elif block.type == "text":
                    text_content.append(block.text)

            # Track assistant response
            if self.db_session and design_id:
                await self._save_conversation(
                    design_id=design_id,
                    job_id=job_id,
                    message_index=len(self.conversation_history),
                    role="assistant",
                    content="\n".join(text_content),
                    tool_calls=tool_calls if tool_calls else None,
                    tokens_used=response.usage.input_tokens + response.usage.output_tokens
                )

            self.conversation_history.append({
                "role": "assistant",
                "content": response.content,
                "tool_calls": tool_calls
            })

            logger.info(
                "agent_message_sent",
                agent=self.agent_type,
                tokens=response.usage.input_tokens + response.usage.output_tokens,
                tool_calls=len(tool_calls)
            )

            return response

        except Exception as e:
            logger.error("agent_message_failed", agent=self.agent_type, error=str(e))
            raise

    async def process_tool_calls(
        self,
        tool_calls: List[Dict[str, Any]],
        design_id: Optional[str] = None,
        job_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Process tool calls and return results.

        Args:
            tool_calls: List of tool calls from Claude
            design_id: Design ID for tracking
            job_id: Job ID for tracking

        Returns:
            List of tool results
        """
        results = []

        for tool_call in tool_calls:
            tool_name = tool_call["name"]
            tool_input = tool_call["input"]
            tool_id = tool_call["id"]

            logger.info(
                "processing_tool_call",
                agent=self.agent_type,
                tool=tool_name,
                input=tool_input
            )

            try:
                # Execute tool
                result = await self.execute_tool(tool_name, tool_input)

                results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_id,
                    "content": str(result)
                })

                # Track tool result
                if self.db_session and design_id:
                    await self._save_conversation(
                        design_id=design_id,
                        job_id=job_id,
                        message_index=len(self.conversation_history),
                        role="tool",
                        content=f"Tool: {tool_name}",
                        tool_results={
                            "tool_name": tool_name,
                            "tool_input": tool_input,
                            "result": result
                        }
                    )

            except Exception as e:
                logger.error("tool_execution_failed", tool=tool_name, error=str(e))
                results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_id,
                    "content": f"Error: {str(e)}",
                    "is_error": True
                })

        return results

    async def _save_conversation(
        self,
        design_id: str,
        message_index: int,
        role: str,
        content: str,
        job_id: Optional[str] = None,
        tool_calls: Optional[List[Dict[str, Any]]] = None,
        tool_results: Optional[Dict[str, Any]] = None,
        tokens_used: Optional[int] = None,
    ) -> None:
        """
        Save conversation message to database.

        Args:
            design_id: Design ID
            message_index: Message index in conversation
            role: Message role (user, assistant, tool)
            content: Message content
            job_id: Optional job ID
            tool_calls: Optional tool calls
            tool_results: Optional tool results
            tokens_used: Optional tokens used
        """
        if not self.db_session:
            return

        try:
            conversation = AgentConversation(
                design_id=design_id,
                job_id=job_id,
                agent_type=self.agent_type,
                message_index=message_index,
                role=role,
                content=content,
                tool_calls=tool_calls,
                tool_results=tool_results,
                tokens_used=tokens_used
            )
            self.db_session.add(conversation)
            await self.db_session.commit()

        except Exception as e:
            logger.error("conversation_save_failed", error=str(e))
            await self.db_session.rollback()

    @abstractmethod
    async def execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool and return results.

        Args:
            tool_name: Name of the tool to execute
            tool_input: Tool input parameters

        Returns:
            Tool execution results
        """
        pass

    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        Get the system prompt for this agent.

        Returns:
            System prompt string
        """
        pass

    @abstractmethod
    async def process(
        self,
        input_data: Dict[str, Any],
        design_id: Optional[str] = None,
        job_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process input and return results.

        Args:
            input_data: Input data for processing
            design_id: Optional design ID for tracking
            job_id: Optional job ID for tracking

        Returns:
            Processing results
        """
        pass

    def extract_text_content(self, message: Message) -> str:
        """
        Extract text content from Claude message.

        Args:
            message: Claude API message response

        Returns:
            Extracted text content
        """
        text_content = []
        for block in message.content:
            if hasattr(block, 'text'):
                text_content.append(block.text)
        return '\n'.join(text_content)

    def extract_tool_calls(self, message: Message) -> List[Dict[str, Any]]:
        """
        Extract tool calls from Claude message.

        Args:
            message: Claude API message response

        Returns:
            List of tool calls
        """
        tool_calls = []
        for block in message.content:
            if block.type == "tool_use":
                tool_calls.append({
                    "id": block.id,
                    "name": block.name,
                    "input": block.input
                })
        return tool_calls
