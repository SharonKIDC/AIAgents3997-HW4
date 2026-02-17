"""Tests for SpotifyAgent."""

import pytest
from unittest.mock import MagicMock, patch

from src.models.point import Point, Coordinates
from src.agents.spotify_agent import SpotifyAgent


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
        location_name="Turn right onto Borgo Santo Spirito",
        coordinates=Coordinates(lat=41.8990000, lng=12.4770000),
        order=1
    )


class TestSpotifyAgent:
    """Tests for SpotifyAgent."""

    @patch('spotipy.Spotify')
    @patch('spotipy.oauth2.SpotifyClientCredentials')
    def test_search_success(self, mock_creds, mock_spotify_class, sample_point):
        """Test successful Spotify search."""
        mock_spotify = MagicMock()
        mock_spotify.search.return_value = {
            'tracks': {
                'items': [{
                    'name': 'Roman Holiday',
                    'artists': [{'name': 'Artist One'}, {'name': 'Artist Two'}],
                    'album': {'name': 'Album Name'},
                    'external_urls': {'spotify': 'https://spotify.com/track/123'},
                    'id': 'track_123',
                    'preview_url': 'https://spotify.com/preview.mp3',
                    'duration_ms': 180000
                }]
            }
        }
        mock_spotify_class.return_value = mock_spotify

        agent = SpotifyAgent(
            run_id="test_run",
            client_id="test_client_id",
            client_secret="test_client_secret"
        )
        result = agent.search(sample_point)

        assert result.success is True
        assert result.content_type == "music"
        assert result.content['title'] == 'Roman Holiday'
        assert result.content['artist'] == 'Artist One, Artist Two'
        assert result.content['url'] == 'https://spotify.com/track/123'
        assert result.content['track_id'] == 'track_123'

    @patch('spotipy.Spotify')
    @patch('spotipy.oauth2.SpotifyClientCredentials')
    def test_search_no_results(self, mock_creds, mock_spotify_class, sample_point):
        """Test Spotify search with no results - should return placeholder."""
        mock_spotify = MagicMock()
        # All searches return empty results
        mock_spotify.search.return_value = {'tracks': {'items': []}}
        mock_spotify_class.return_value = mock_spotify

        agent = SpotifyAgent(
            run_id="test_run",
            client_id="test_client_id",
            client_secret="test_client_secret"
        )
        result = agent.search(sample_point)

        # Should succeed with placeholder content
        assert result.success is True
        assert 'Ambient music' in result.content['title']
        assert result.content['url'] == ""

    @patch('spotipy.Spotify')
    @patch('spotipy.oauth2.SpotifyClientCredentials')
    def test_search_api_error(self, mock_creds, mock_spotify_class, sample_point):
        """Test Spotify search with API error."""
        import spotipy

        mock_spotify = MagicMock()
        mock_spotify.search.side_effect = spotipy.SpotifyException(
            http_status=429,
            code=-1,
            msg='Rate limit exceeded'
        )
        mock_spotify_class.return_value = mock_spotify

        agent = SpotifyAgent(
            run_id="test_run",
            client_id="test_client_id",
            client_secret="test_client_secret"
        )
        result = agent.search(sample_point)

        assert result.success is False
        assert "Spotify API error" in result.error_message

    @patch('spotipy.Spotify')
    @patch('spotipy.oauth2.SpotifyClientCredentials')
    def test_create_search_query_adds_context(self, mock_creds, mock_spotify_class, sample_point):
        """Test that search query adds instrumental ambient context."""
        mock_spotify = MagicMock()
        mock_spotify_class.return_value = mock_spotify

        agent = SpotifyAgent(
            run_id="test_run",
            client_id="test_client_id",
            client_secret="test_client_secret"
        )
        query = agent._create_search_query(sample_point)

        assert 'instrumental ambient' in query
        assert 'Pantheon' in query

    @patch('spotipy.Spotify')
    @patch('spotipy.oauth2.SpotifyClientCredentials')
    def test_create_search_query_filters_navigation(self, mock_creds, mock_spotify_class, navigation_point):
        """Test that navigation words are filtered."""
        mock_spotify = MagicMock()
        mock_spotify_class.return_value = mock_spotify

        agent = SpotifyAgent(
            run_id="test_run",
            client_id="test_client_id",
            client_secret="test_client_secret"
        )
        query = agent._create_search_query(navigation_point)

        assert 'turn' not in query.lower()
        assert 'Borgo Santo Spirito' in query
        assert 'instrumental ambient' in query

    @patch('spotipy.Spotify')
    @patch('spotipy.oauth2.SpotifyClientCredentials')
    def test_result_handles_optional_fields(self, mock_creds, mock_spotify_class, sample_point):
        """Test that result handles optional fields like preview_url."""
        mock_spotify = MagicMock()
        mock_spotify.search.return_value = {
            'tracks': {
                'items': [{
                    'name': 'Track Name',
                    'artists': [{'name': 'Artist'}],
                    'album': {'name': 'Album'},
                    'external_urls': {'spotify': 'https://spotify.com/track/456'},
                    'id': 'track_456',
                    'preview_url': None,  # Optional field
                    'duration_ms': 200000
                }]
            }
        }
        mock_spotify_class.return_value = mock_spotify

        agent = SpotifyAgent(
            run_id="test_run",
            client_id="test_client_id",
            client_secret="test_client_secret"
        )
        result = agent.search(sample_point)

        assert result.success is True
        assert result.content['preview_url'] is None
