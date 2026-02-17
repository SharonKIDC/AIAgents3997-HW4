"""Tests for TextAgent."""

import pytest
from unittest.mock import MagicMock, patch

from src.models.point import Point, Coordinates
from src.agents.text_agent import TextAgent


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
        location_name="Continue onto Via dei Coronari",
        coordinates=Coordinates(lat=41.8990000, lng=12.4770000),
        order=1
    )


class TestTextAgent:
    """Tests for TextAgent."""

    @patch('requests.get')
    def test_search_success_direct_lookup(self, mock_get, sample_point):
        """Test successful Wikipedia search with direct lookup."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'title': 'Pantheon, Rome',
            'extract': 'The Pantheon is a former Roman temple, now a Catholic church...',
            'content_urls': {
                'desktop': {
                    'page': 'https://en.wikipedia.org/wiki/Pantheon,_Rome'
                }
            },
            'extract_html': '<p>The Pantheon is a former Roman temple...</p>'
        }
        mock_get.return_value = mock_response

        agent = TextAgent(run_id="test_run")
        result = agent.search(sample_point)

        assert result.success is True
        assert result.content_type == "text"
        assert result.content['title'] == 'Pantheon, Rome'
        assert 'Pantheon' in result.content['description']
        assert result.content['source'] == 'Wikipedia'
        assert result.content['url'] == 'https://en.wikipedia.org/wiki/Pantheon,_Rome'

    @patch('requests.get')
    def test_search_with_fallback_search(self, mock_get, sample_point):
        """Test Wikipedia search with fallback to search API."""
        # With location context: search API call with location, then summary
        mock_search_response_with_location = MagicMock()
        mock_search_response_with_location.status_code = 200
        mock_search_response_with_location.json.return_value = {
            'query': {
                'search': [{
                    'title': 'Pantheon, Rome'
                }]
            }
        }

        mock_summary_response = MagicMock()
        mock_summary_response.status_code = 200
        mock_summary_response.json.return_value = {
            'title': 'Pantheon, Rome',
            'extract': 'The Pantheon...',
            'content_urls': {'desktop': {'page': 'https://en.wikipedia.org/wiki/Pantheon'}}
        }

        # Agent will try: location context search -> summary
        mock_get.side_effect = [
            mock_search_response_with_location,
            mock_summary_response
        ]

        agent = TextAgent(run_id="test_run")
        result = agent.search(sample_point)

        assert result.success is True
        assert result.content['title'] == 'Pantheon, Rome'

    @patch('requests.get')
    def test_search_no_results(self, mock_get, sample_point):
        """Test Wikipedia search with no results - should return placeholder."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        agent = TextAgent(run_id="test_run")
        result = agent.search(sample_point)

        # Should succeed with placeholder content
        assert result.success is True
        assert result.content['title'] == sample_point.location_name
        assert 'No specific information' in result.content['description']

    @patch('requests.get')
    def test_search_network_error(self, mock_get, sample_point):
        """Test handling of network errors."""
        mock_get.side_effect = Exception("Network timeout")

        agent = TextAgent(run_id="test_run")
        result = agent.search(sample_point)

        assert result.success is False
        assert "Network timeout" in result.error_message

    def test_create_search_query_filters_navigation(self, navigation_point):
        """Test that navigation words are filtered."""
        agent = TextAgent(run_id="test_run")
        query = agent._create_search_query(navigation_point)

        assert 'continue' not in query.lower()
        assert 'onto' not in query.lower()
        assert 'Via dei Coronari' in query

    def test_create_search_query_preserves_content(self):
        """Test that non-navigation content is preserved."""
        point = Point(
            run_id="test_run",
            point_id="test_point",
            location_name="Piazza Navona",
            coordinates=Coordinates(lat=41.9, lng=12.5),
            order=0
        )

        agent = TextAgent(run_id="test_run")
        query = agent._create_search_query(point)

        assert query == "Piazza Navona"

    @patch('requests.get')
    def test_wikipedia_api_timeout(self, mock_get, sample_point):
        """Test Wikipedia API timeout handling."""
        import requests
        mock_get.side_effect = requests.Timeout("Request timeout")

        agent = TextAgent(run_id="test_run")
        result = agent.search(sample_point)

        assert result.success is False

    @patch('requests.get')
    def test_result_contains_all_metadata(self, mock_get, sample_point):
        """Test that result contains all expected metadata."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'title': 'Test Title',
            'extract': 'Test extract with sufficient length to be meaningful',
            'content_urls': {'desktop': {'page': 'http://wiki.com/test'}},
            'extract_html': '<p>HTML content</p>'
        }
        mock_get.return_value = mock_response

        agent = TextAgent(run_id="test_run")
        result = agent.search(sample_point)

        assert 'title' in result.content
        assert 'description' in result.content
        assert 'url' in result.content
        assert 'source' in result.content
        assert 'extract_html' in result.content
