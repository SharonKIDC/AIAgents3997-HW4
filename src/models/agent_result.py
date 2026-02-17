"""Data models for agent results."""

from dataclasses import dataclass
from typing import Optional, Literal
from datetime import datetime


@dataclass
class AgentResult:
    """Result from a content search agent."""
    run_id: str
    point_id: str
    agent_name: str
    content_type: Literal["video", "music", "text"]
    content: dict
    timestamp: datetime
    success: bool = True
    error_message: Optional[str] = None

    def __str__(self) -> str:
        if self.success:
            return f"AgentResult({self.agent_name}: {self.content.get('title', 'N/A')})"
        else:
            return f"AgentResult({self.agent_name}: FAILED - {self.error_message})"


@dataclass
class JudgeDecision:
    """Decision from the judge agent."""
    run_id: str
    point_id: str
    selected_content_type: Literal["video", "music", "text"]
    selected_content: dict
    reasoning: str
    timestamp: datetime
    all_results: list[AgentResult]

    def __str__(self) -> str:
        return f"JudgeDecision(selected: {self.selected_content_type}, title: {self.selected_content.get('title', 'N/A')})"
