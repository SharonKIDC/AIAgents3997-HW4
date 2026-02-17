"""Judge agent for selecting the best content from search results."""

import logging
from typing import List
from datetime import datetime

from src.models.point import Point
from src.models.agent_result import AgentResult, JudgeDecision


class JudgeAgent:
    """Agent for judging and selecting the best content."""

    def __init__(self, run_id: str):
        """
        Initialize Judge agent.

        Args:
            run_id: Unique identifier for this run
        """
        self.run_id = run_id
        self.agent_name = "JudgeAgent"
        self.logger = logging.getLogger(__name__)

    def log_info(self, message: str):
        """Log info message with standard format."""
        self.logger.info(f"({self.run_id}, {self.agent_name}, {message})")

    def log_error(self, message: str):
        """Log error message with standard format."""
        self.logger.error(f"({self.run_id}, {self.agent_name}, {message})")

    def judge(self, point: Point, results: List[AgentResult]) -> JudgeDecision:
        """
        Judge the results and select the best content.

        Args:
            point: The point these results are for
            results: List of results from other agents

        Returns:
            JudgeDecision with the selected content
        """
        self.log_info(f"Judging {len(results)} results for: {point.location_name}")

        # Filter successful results
        successful_results = [r for r in results if r.success]

        if not successful_results:
            self.log_error(f"No successful results to judge for: {point.location_name}")
            # Return a default decision with empty content
            return JudgeDecision(
                run_id=self.run_id,
                point_id=point.point_id,
                selected_content_type="text",
                selected_content={},
                reasoning="No successful results available",
                timestamp=datetime.now(),
                all_results=results
            )

        # Score each result
        scored_results = []
        for result in successful_results:
            score = self._score_result(result, point)
            scored_results.append((result, score))
            self.log_info(f"{result.agent_name} ({result.content_type}): score={score}")

        # Select the highest scoring result
        best_result, best_score = max(scored_results, key=lambda x: x[1])

        reasoning = self._generate_reasoning(best_result, best_score, scored_results, point)

        self.log_info(f"Selected {best_result.content_type} from {best_result.agent_name}")

        return JudgeDecision(
            run_id=self.run_id,
            point_id=point.point_id,
            selected_content_type=best_result.content_type,
            selected_content=best_result.content,
            reasoning=reasoning,
            timestamp=datetime.now(),
            all_results=results
        )

    def _score_result(self, result: AgentResult, point: Point) -> float:
        """
        Score a result based on relevance and quality.

        Args:
            result: The result to score
            point: The point this result is for

        Returns:
            Score (0-100)
        """
        score = 0.0

        # Base score for having content
        if result.content:
            score += 30

        # Check if title exists and is meaningful
        title = result.content.get('title', '')
        if title:
            score += 20

            # Bonus for title relevance (simple keyword matching)
            location_keywords = set(point.location_name.lower().split())
            title_keywords = set(title.lower().split())
            overlap = len(location_keywords & title_keywords)
            score += min(overlap * 5, 20)

        # Check if description/text exists
        description = result.content.get('description', '')
        if description:
            score += 15

        # Content type preferences (adjust as needed)
        if result.content_type == "text":
            score += 10  # Prefer text for informativeness
        elif result.content_type == "video":
            score += 5   # Videos are engaging
        elif result.content_type == "music":
            score += 5   # Music for atmosphere

        # Bonus for having URL
        if result.content.get('url'):
            score += 5

        return min(score, 100)

    def _generate_reasoning(
        self,
        best_result: AgentResult,
        best_score: float,
        all_scored: List[tuple[AgentResult, float]],
        point: Point
    ) -> str:
        """
        Generate reasoning for the selection.

        Args:
            best_result: The selected result
            best_score: Score of the best result
            all_scored: All scored results
            point: The point being judged

        Returns:
            Reasoning string
        """
        reasons = []

        # Main selection reason
        reasons.append(
            f"Selected {best_result.content_type} content from {best_result.agent_name} "
            f"(score: {best_score:.1f}/100)"
        )

        # Title relevance
        if best_result.content.get('title'):
            reasons.append(f"Title: '{best_result.content['title']}'")

        # Comparison with other options
        other_scores = [score for result, score in all_scored if result != best_result]
        if other_scores:
            avg_other = sum(other_scores) / len(other_scores)
            if best_score > avg_other + 10:
                reasons.append(f"Significantly higher relevance than alternatives")

        # Content quality indicators
        if best_result.content.get('description'):
            desc_len = len(best_result.content['description'])
            if desc_len > 100:
                reasons.append("Contains comprehensive description")

        return ". ".join(reasons) + "."
