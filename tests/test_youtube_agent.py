"""Tests for YouTubeAgent."""

import pytest
from unittest.mock import MagicMock, patch

from src.models.point import Point, Coordinates
from src.agents.youtube_agent import YouTubeAgent


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


@pytest.fixture
def navigation_point():
    """Create a point with navigation instructions."""
    return Point(
        run_id="test_run",
        point_id="test_point_2",
        location_name="Turn left onto Via della Strada",
        coordinates=Coordinates(lat=41.8990000, lng=12.4770000),
        order=1
    )


class TestYouTubeAgent:
    """Tests for YouTubeAgent."""

    @patch('src.agents.youtube_agent.build')
    def test_search_success(self, mock_build, sample_point):
        """Test successful YouTube search."""
        # Mock YouTube API response
        mock_youtube = MagicMock()
        mock_search = MagicMock()
        mock_list = MagicMock()

        mock_list.execute.return_value = {
            'items': [{
                'id': {'videoId': 'test_video_123'},
                'snippet': {
                    'title': 'Pantheon Rome - Ancient Architecture',
                    'description': 'A tour of the Pantheon in Rome',
                    'channelTitle': 'History Channel',
                    'thumbnails': {'default': {'url': 'http://example.com/thumb.jpg'}}
                }
            }]
        }

        mock_search.list.return_value = mock_list
        mock_youtube.search.return_value = mock_search
        mock_build.return_value = mock_youtube

        agent = YouTubeAgent(run_id="test_run", api_key="AIza_test_key")
        result = agent.search(sample_point)

        assert result.success is True
        assert result.content_type == "video"
        assert result.content['title'] == 'Pantheon Rome - Ancient Architecture'
        assert result.content['video_id'] == 'test_video_123'
        assert result.content['url'] == 'https://www.youtube.com/watch?v=test_video_123'
        assert result.agent_name == "YouTubeAgent"
        assert result.run_id == "test_run"

    @patch('src.agents.youtube_agent.build')
    def test_search_no_results(self, mock_build, sample_point):
        """Test YouTube search with no results - should return placeholder."""
        mock_youtube = MagicMock()
        mock_search = MagicMock()
        mock_list = MagicMock()

        # All searches return empty results
        mock_list.execute.return_value = {'items': []}
        mock_search.list.return_value = mock_list
        mock_youtube.search.return_value = mock_search
        mock_build.return_value = mock_youtube

        agent = YouTubeAgent(run_id="test_run", api_key="AIza_test_key")
        result = agent.search(sample_point)

        # Should succeed with placeholder content
        assert result.success is True
        assert 'Walking tour' in result.content['title']
        assert result.content['url'] == ""

    @patch('src.agents.youtube_agent.build')
    def test_search_api_error(self, mock_build, sample_point):
        """Test YouTube search with API error."""
        from googleapiclient.errors import HttpError

        mock_youtube = MagicMock()
        mock_search = MagicMock()
        mock_list = MagicMock()

        # Simulate API error
        mock_list.execute.side_effect = HttpError(
            resp=MagicMock(status=403),
            content=b'Quota exceeded'
        )
        mock_search.list.return_value = mock_list
        mock_youtube.search.return_value = mock_search
        mock_build.return_value = mock_youtube

        agent = YouTubeAgent(run_id="test_run", api_key="AIza_test_key")
        result = agent.search(sample_point)

        assert result.success is False
        assert "YouTube API error" in result.error_message

    @patch('src.agents.youtube_agent.build')
    def test_create_search_query_filters_navigation(self, mock_build, navigation_point):
        """Test that navigation words are filtered from search query."""
        mock_youtube = MagicMock()
        mock_build.return_value = mock_youtube

        agent = YouTubeAgent(run_id="test_run", api_key="AIza_test_key")
        query = agent._create_search_query(navigation_point)

        # Should filter out 'turn', 'left', 'onto'
        assert 'turn' not in query.lower()
        assert 'Via della Strada' in query

    @patch('src.agents.youtube_agent.build')
    def test_create_search_query_preserves_short_queries(self, mock_build):
        """Test that very short queries are preserved."""
        mock_youtube = MagicMock()
        mock_build.return_value = mock_youtube

        point = Point(
            run_id="test_run",
            point_id="test_point",
            location_name="Turn left",
            coordinates=Coordinates(lat=41.9, lng=12.5),
            order=0
        )

        agent = YouTubeAgent(run_id="test_run", api_key="AIza_test_key")
        query = agent._create_search_query(point)

        # Should preserve original when filtering removes too much
        assert query == "Turn left"

    @patch('src.agents.youtube_agent.build')
    def test_result_contains_all_metadata(self, mock_build, sample_point):
        """Test that result contains all expected metadata."""
        mock_youtube = MagicMock()
        mock_search = MagicMock()
        mock_list = MagicMock()

        mock_list.execute.return_value = {
            'items': [{
                'id': {'videoId': 'abc123'},
                'snippet': {
                    'title': 'Test Video',
                    'description': 'Test Description',
                    'channelTitle': 'Test Channel',
                    'thumbnails': {'default': {'url': 'http://thumb.jpg'}}
                }
            }]
        }

        mock_search.list.return_value = mock_list
        mock_youtube.search.return_value = mock_search
        mock_build.return_value = mock_youtube

        agent = YouTubeAgent(run_id="test_run", api_key="AIza_test_key")
        result = agent.search(sample_point)

        assert 'title' in result.content
        assert 'description' in result.content
        assert 'url' in result.content
        assert 'video_id' in result.content
        assert 'thumbnail' in result.content
        assert 'channel' in result.content
