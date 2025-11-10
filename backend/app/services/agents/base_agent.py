"""Base agent class for all CAD agents."""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import structlog
from anthropic import Anthropic
from anthropic.types.message import Message

from app.core.config import settings

logger = structlog.get_logger()


class BaseAgent(ABC):
    """Base class for all CAD agents."""

    def __init__(self, agent_name: str) -> None:
        """
        Initialize base agent.

        Args:
            agent_name: Name of the agent
        """
        self.agent_name = agent_name
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = settings.ANTHROPIC_MODEL
        self.max_tokens = settings.ANTHROPIC_MAX_TOKENS
        self.temperature = settings.ANTHROPIC_TEMPERATURE
        logger.info("agent_initialized", agent=agent_name)

    async def send_message(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> Message:
        """
        Send message to Claude API.

        Args:
            messages: List of message dictionaries
            system_prompt: System prompt for the agent
            temperature: Override default temperature
            max_tokens: Override default max tokens

        Returns:
            Claude API response
        """
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens or self.max_tokens,
                temperature=temperature or self.temperature,
                system=system_prompt or self.get_system_prompt(),
                messages=messages,
            )
            logger.info(
                "agent_message_sent",
                agent=self.agent_name,
                tokens=response.usage.input_tokens + response.usage.output_tokens
            )
            return response
        except Exception as e:
            logger.error("agent_message_failed", agent=self.agent_name, error=str(e))
            raise

    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        Get the system prompt for this agent.

        Returns:
            System prompt string
        """
        pass

    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input and return results.

        Args:
            input_data: Input data for processing

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
