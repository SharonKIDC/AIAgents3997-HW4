"""Base agent class for all content search agents."""

import logging
from abc import ABC, abstractmethod
from datetime import datetime

from src.models.point import Point
from src.models.agent_result import AgentResult


class BaseAgent(ABC):
    """Base class for all agents."""

    def __init__(self, run_id: str, agent_name: str):
        """
        Initialize the base agent.

        Args:
            run_id: Unique identifier for this run
            agent_name: Name of this agent
        """
        self.run_id = run_id
        self.agent_name = agent_name
        self.logger = logging.getLogger(__name__)

    def log_info(self, message: str):
        """Log info message with standard format."""
        self.logger.info(f"({self.run_id}, {self.agent_name}, {message})")

    def log_warning(self, message: str):
        """Log warning message with standard format."""
        self.logger.warning(f"({self.run_id}, {self.agent_name}, {message})")

    def log_error(self, message: str):
        """Log error message with standard format."""
        self.logger.error(f"({self.run_id}, {self.agent_name}, {message})")

    @abstractmethod
    def search(self, point: Point) -> AgentResult:
        """
        Search for content relevant to the given point.

        Args:
            point: The point to search content for

        Returns:
            AgentResult with the search results
        """
        pass

    def create_result(
        self,
        point: Point,
        content_type: str,
        content: dict,
        success: bool = True,
        error_message: str = None
    ) -> AgentResult:
        """
        Create an AgentResult object.

        Args:
            point: The point this result is for
            content_type: Type of content (video, music, text)
            content: Content dictionary
            success: Whether the search was successful
            error_message: Error message if not successful

        Returns:
            AgentResult object
        """
        return AgentResult(
            run_id=self.run_id,
            point_id=point.point_id,
            agent_name=self.agent_name,
            content_type=content_type,
            content=content,
            timestamp=datetime.now(),
            success=success,
            error_message=error_message
        )
