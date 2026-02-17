"""Tests for JudgeAgent."""

import pytest
from datetime import datetime

from src.models.point import Point, Coordinates
from src.models.agent_result import AgentResult, JudgeDecision
from src.agents.judge_agent import JudgeAgent


@pytest.fixture
def sample_point():
    """Create a sample point for testing."""
    return Point(
        run_id="test_run",
        point_id="test_point_1",
        location_name="Pantheon",
        coordinates=Coordinates(lat=41.8986108, lng=12.4768729),
        order=0,
        place_id="ChIJ123",
        address="Piazza della Rotonda, Rome"
    )


class TestJudgeAgent:
    """Tests for JudgeAgent."""

    def test_judge_selects_best_result(self, sample_point):
        """Test that judge selects the highest scoring result."""
        agent = JudgeAgent(run_id="test_run")

        # Create mock results with different quality
        video_result = AgentResult(
            run_id="test_run",
            point_id=sample_point.point_id,
            agent_name="YouTubeAgent",
            content_type="video",
            content={
                'title': 'Generic video',
                'description': 'Short desc',
                'url': 'http://youtube.com/watch?v=123'
            },
            timestamp=datetime.now(),
            success=True
        )

        text_result = AgentResult(
            run_id="test_run",
            point_id=sample_point.point_id,
            agent_name="TextAgent",
            content_type="text",
            content={
                'title': 'Pantheon Rome',  # Contains location name - higher relevance
                'description': (
                    'The Pantheon is a former Roman temple, now a Catholic church, in Rome, Italy. '
                    'It is one of the best-preserved of all Ancient Roman buildings and has been in '
                    'continuous use throughout its history.'
                ),
                'url': 'https://en.wikipedia.org/wiki/Pantheon'
            },
            timestamp=datetime.now(),
            success=True
        )

        music_result = AgentResult(
            run_id="test_run",
            point_id=sample_point.point_id,
            agent_name="SpotifyAgent",
            content_type="music",
            content={
                'title': 'Some song',
                'url': 'https://spotify.com/track/123'
            },
            timestamp=datetime.now(),
            success=True
        )

        results = [video_result, text_result, music_result]
        decision = agent.judge(sample_point, results)

        # Text should win due to title relevance and comprehensive description
        assert decision.selected_content_type == "text"
        assert decision.selected_content['title'] == 'Pantheon Rome'
        assert len(decision.reasoning) > 0
        assert len(decision.all_results) == 3

    def test_judge_handles_no_successful_results(self, sample_point):
        """Test judge behavior when all results fail."""
        agent = JudgeAgent(run_id="test_run")

        failed_result = AgentResult(
            run_id="test_run",
            point_id=sample_point.point_id,
            agent_name="YouTubeAgent",
            content_type="video",
            content={},
            timestamp=datetime.now(),
            success=False,
            error_message="API error"
        )

        results = [failed_result]
        decision = agent.judge(sample_point, results)

        assert decision.reasoning == "No successful results available"
        assert decision.selected_content == {}

    def test_score_result_relevance_bonus(self, sample_point):
        """Test that scoring gives bonus for title relevance."""
        agent = JudgeAgent(run_id="test_run")

        # Result with relevant title
        relevant_result = AgentResult(
            run_id="test_run",
            point_id=sample_point.point_id,
            agent_name="TextAgent",
            content_type="text",
            content={
                'title': 'Pantheon Rome Architecture',  # Contains 'Pantheon'
                'description': 'Long description here...',
                'url': 'http://example.com'
            },
            timestamp=datetime.now(),
            success=True
        )

        # Result with irrelevant title
        irrelevant_result = AgentResult(
            run_id="test_run",
            point_id=sample_point.point_id,
            agent_name="TextAgent",
            content_type="text",
            content={
                'title': 'Random Topic',
                'description': 'Long description here...',
                'url': 'http://example.com'
            },
            timestamp=datetime.now(),
            success=True
        )

        relevant_score = agent._score_result(relevant_result, sample_point)
        irrelevant_score = agent._score_result(irrelevant_result, sample_point)

        assert relevant_score > irrelevant_score

    def test_score_result_content_type_preference(self, sample_point):
        """Test that scoring has content type preferences."""
        agent = JudgeAgent(run_id="test_run")

        # All results have similar content, different types
        text_result = AgentResult(
            run_id="test_run",
            point_id=sample_point.point_id,
            agent_name="TextAgent",
            content_type="text",
            content={'title': 'Test', 'description': 'Test', 'url': 'http://example.com'},
            timestamp=datetime.now(),
            success=True
        )

        video_result = AgentResult(
            run_id="test_run",
            point_id=sample_point.point_id,
            agent_name="YouTubeAgent",
            content_type="video",
            content={'title': 'Test', 'description': 'Test', 'url': 'http://example.com'},
            timestamp=datetime.now(),
            success=True
        )

        text_score = agent._score_result(text_result, sample_point)
        video_score = agent._score_result(video_result, sample_point)

        # Text should be preferred (gets +10 vs video's +5)
        assert text_score > video_score

    def test_judge_decision_model(self, sample_point):
        """Test JudgeDecision data model."""
        result = AgentResult(
            run_id="test_run",
            point_id=sample_point.point_id,
            agent_name="TextAgent",
            content_type="text",
            content={'title': 'Test'},
            timestamp=datetime.now(),
            success=True
        )

        decision = JudgeDecision(
            run_id="test_run",
            point_id=sample_point.point_id,
            selected_content_type="text",
            selected_content={'title': 'Test'},
            reasoning="Test reasoning",
            timestamp=datetime.now(),
            all_results=[result]
        )

        assert decision.selected_content_type == "text"
        assert len(decision.all_results) == 1
        assert "text" in str(decision)

    def test_generate_reasoning_comprehensive(self, sample_point):
        """Test that reasoning generation is comprehensive."""
        agent = JudgeAgent(run_id="test_run")

        best_result = AgentResult(
            run_id="test_run",
            point_id=sample_point.point_id,
            agent_name="TextAgent",
            content_type="text",
            content={
                'title': 'Pantheon Architecture',
                'description': 'A' * 200,  # Long description
                'url': 'http://example.com'
            },
            timestamp=datetime.now(),
            success=True
        )

        other_result = AgentResult(
            run_id="test_run",
            point_id=sample_point.point_id,
            agent_name="YouTubeAgent",
            content_type="video",
            content={'title': 'Video', 'url': 'http://youtube.com'},
            timestamp=datetime.now(),
            success=True
        )

        scored_results = [
            (best_result, 85.0),
            (other_result, 60.0)
        ]

        reasoning = agent._generate_reasoning(best_result, 85.0, scored_results, sample_point)

        assert 'text' in reasoning.lower()
        assert '85' in reasoning
        assert 'Pantheon Architecture' in reasoning
        assert 'comprehensive description' in reasoning.lower()

    def test_score_result_url_bonus(self, sample_point):
        """Test that having a URL gives a score bonus."""
        agent = JudgeAgent(run_id="test_run")

        with_url = AgentResult(
            run_id="test_run",
            point_id=sample_point.point_id,
            agent_name="TextAgent",
            content_type="text",
            content={'title': 'Test', 'url': 'http://example.com'},
            timestamp=datetime.now(),
            success=True
        )

        without_url = AgentResult(
            run_id="test_run",
            point_id=sample_point.point_id,
            agent_name="TextAgent",
            content_type="text",
            content={'title': 'Test'},
            timestamp=datetime.now(),
            success=True
        )

        score_with = agent._score_result(with_url, sample_point)
        score_without = agent._score_result(without_url, sample_point)

        assert score_with > score_without
