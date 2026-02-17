"""YouTube search agent for finding relevant videos."""

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from src.models.point import Point
from src.models.agent_result import AgentResult
from src.agents.base_agent import BaseAgent


class YouTubeAgent(BaseAgent):
    """Agent for searching YouTube videos."""

    def __init__(self, run_id: str, api_key: str):
        """
        Initialize YouTube agent.

        Args:
            run_id: Unique identifier for this run
            api_key: YouTube Data API key
        """
        super().__init__(run_id, "YouTubeAgent")
        self.api_key = api_key
        self.youtube = build('youtube', 'v3', developerKey=api_key)

    def search(self, point: Point) -> AgentResult:
        """
        Search for YouTube videos relevant to the point.

        Args:
            point: The point to search videos for

        Returns:
            AgentResult with video information
        """
        self.log_info(f"Searching for videos about: {point.location_name}")

        try:
            # Create search query from location name
            query = self._create_search_query(point)
            self.log_info(f"Search query: {query}")

            # Search YouTube
            search_response = self.youtube.search().list(
                q=query,
                part='id,snippet',
                maxResults=1,
                type='video',
                order='relevance'
            ).execute()

            # If no results with filtered query, try with address/city
            if not search_response.get('items') and point.address:
                city = self._extract_city(point.address)
                if city and city != query:
                    self.log_info(f"Retrying with city: {city}")
                    search_response = self.youtube.search().list(
                        q=city,
                        part='id,snippet',
                        maxResults=1,
                        type='video',
                        order='relevance'
                    ).execute()

            # If still no results, return placeholder
            if not search_response.get('items'):
                self.log_info(f"No videos found for: {point.location_name}")
                content = {
                    'title': f"Walking tour near {point.location_name}",
                    'description': "No specific video found for this location",
                    'url': "",
                    'video_id': "",
                    'thumbnail': "",
                    'channel': ""
                }
            else:
                # Get the top result
                video = search_response['items'][0]
                video_id = video['id']['videoId']
                snippet = video['snippet']

                content = {
                    'title': snippet['title'],
                    'description': snippet['description'],
                    'url': f"https://www.youtube.com/watch?v={video_id}",
                    'video_id': video_id,
                    'thumbnail': snippet['thumbnails']['default']['url'],
                    'channel': snippet['channelTitle']
                }

                self.log_info(f"Found video: {content['title']}")

            return self.create_result(
                point=point,
                content_type="video",
                content=content,
                success=True
            )

        except HttpError as e:
            self.log_error(f"YouTube API error: {e}")
            return self.create_result(
                point=point,
                content_type="video",
                content={},
                success=False,
                error_message=f"YouTube API error: {e}"
            )
        except Exception as e:
            self.log_error(f"Error searching YouTube: {e}")
            return self.create_result(
                point=point,
                content_type="video",
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
        if len(filtered_words) < 2:
            return query

        return ' '.join(filtered_words)

    def _extract_city(self, address: str) -> str:
        """Extract city name from address for fallback search."""
        import re
        if not address:
            return ""

        # Split by comma and clean
        parts = [p.strip() for p in address.split(',')]

        # Remove postal codes and clean region codes
        for part in parts:
            # Remove postal code prefix
            cleaned = re.sub(r'^\d+\s+', '', part)
            # Remove region codes
            cleaned = re.sub(r'\s+[A-Z]{2}$', '', cleaned)
            cleaned = cleaned.strip()

            # Return first meaningful city-like part (length > 2)
            if len(cleaned) > 2 and not cleaned.isdigit():
                return cleaned

        return ""
