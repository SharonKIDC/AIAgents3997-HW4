"""Spotify search agent for finding relevant music."""

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from src.models.point import Point
from src.models.agent_result import AgentResult
from src.agents.base_agent import BaseAgent


class SpotifyAgent(BaseAgent):
    """Agent for searching Spotify music."""

    def __init__(self, run_id: str, client_id: str, client_secret: str):
        """
        Initialize Spotify agent.

        Args:
            run_id: Unique identifier for this run
            client_id: Spotify client ID
            client_secret: Spotify client secret
        """
        super().__init__(run_id, "SpotifyAgent")
        self.client_id = client_id
        self.client_secret = client_secret

        # Initialize Spotify client
        auth_manager = SpotifyClientCredentials(
            client_id=client_id,
            client_secret=client_secret
        )
        self.spotify = spotipy.Spotify(auth_manager=auth_manager)

    def search(self, point: Point) -> AgentResult:
        """
        Search for Spotify tracks relevant to the point.

        Args:
            point: The point to search music for

        Returns:
            AgentResult with track information
        """
        self.log_info(f"Searching for music about: {point.location_name}")

        try:
            # Create search query from location name
            query = self._create_search_query(point)
            self.log_info(f"Search query: {query}")

            # Search Spotify
            results = self.spotify.search(q=query, type='track', limit=1)

            # If no results, try with just "ambient" or "instrumental"
            if not results['tracks']['items']:
                self.log_info(f"No tracks found, trying ambient instrumental")
                results = self.spotify.search(q="ambient instrumental", type='track', limit=1)

            # If still no results, return placeholder
            if not results['tracks']['items']:
                self.log_info(f"No tracks found for: {point.location_name}")
                content = {
                    'title': f"Ambient music for {point.location_name}",
                    'artist': "Various Artists",
                    'album': "",
                    'url': "",
                    'track_id': "",
                    'preview_url': None,
                    'duration_ms': 0
                }
            else:
                # Get the top result
                track = results['tracks']['items'][0]

                content = {
                    'title': track['name'],
                    'artist': ', '.join([artist['name'] for artist in track['artists']]),
                    'album': track['album']['name'],
                    'url': track['external_urls']['spotify'],
                    'track_id': track['id'],
                    'preview_url': track.get('preview_url'),
                    'duration_ms': track['duration_ms']
                }

                self.log_info(f"Found track: {content['title']} by {content['artist']}")

            return self.create_result(
                point=point,
                content_type="music",
                content=content,
                success=True
            )

        except spotipy.SpotifyException as e:
            self.log_error(f"Spotify API error: {e}")
            return self.create_result(
                point=point,
                content_type="music",
                content={},
                success=False,
                error_message=f"Spotify API error: {e}"
            )
        except Exception as e:
            self.log_error(f"Error searching Spotify: {e}")
            return self.create_result(
                point=point,
                content_type="music",
                content={},
                success=False,
                error_message=str(e)
            )

    def _create_search_query(self, point: Point) -> str:
        """
        Create a search query from the point information.

        Args:
            point: The point to create query for

        Returns:
            Search query string
        """
        # Use location name, clean up navigation instructions
        query = point.location_name

        # Remove common navigation words
        navigation_words = ['turn', 'head', 'continue', 'slight', 'onto', 'toward']
        words = query.split()
        filtered_words = [w for w in words if w.lower() not in navigation_words]

        # If we filtered too much, use original
        if len(filtered_words) < 1:
            filtered_query = query
        else:
            filtered_query = ' '.join(filtered_words)

        # Add context keywords for better music search
        return filtered_query + " instrumental ambient"
