"""Text search agent for finding relevant descriptions."""

import requests
from typing import Optional

from src.models.point import Point
from src.models.agent_result import AgentResult
from src.agents.base_agent import BaseAgent


class TextAgent(BaseAgent):
    """Agent for searching text descriptions using Wikipedia."""

    def __init__(self, run_id: str):
        """
        Initialize Text agent.

        Args:
            run_id: Unique identifier for this run
        """
        super().__init__(run_id, "TextAgent")
        self.wikipedia_api = "https://en.wikipedia.org/api/rest_v1"
        # Wikipedia requires a User-Agent header
        self.headers = {
            'User-Agent': 'AITourGuide/1.0 (Educational Project; AI Agents Course)'
        }

    def search(self, point: Point) -> AgentResult:
        """
        Search for text descriptions relevant to the point.

        Args:
            point: The point to search descriptions for

        Returns:
            AgentResult with text information
        """
        self.log_info(f"Searching for text about: {point.location_name}")

        try:
            # Create search query from location name
            query = self._create_search_query(point)
            self.log_info(f"Search query: {query}")

            # Try to get Wikipedia summary with fallback strategies
            summary = self._get_wikipedia_summary(query, point)

            if not summary:
                self.log_info(f"No Wikipedia article found for: {point.location_name}")
                # Return placeholder instead of failure
                content = {
                    'title': point.location_name,
                    'description': f"No specific information found for {point.location_name}. This may be a navigation point or specific instruction.",
                    'url': "",
                    'source': 'Wikipedia',
                    'extract_html': ''
                }

                return self.create_result(
                    point=point,
                    content_type="text",
                    content=content,
                    success=True
                )

            content = {
                'title': summary['title'],
                'description': summary['extract'],
                'url': summary.get('content_urls', {}).get('desktop', {}).get('page', ''),
                'source': 'Wikipedia',
                'extract_html': summary.get('extract_html', '')
            }

            self.log_info(f"Found article: {content['title']}")

            return self.create_result(
                point=point,
                content_type="text",
                content=content,
                success=True
            )

        except Exception as e:
            self.log_error(f"Error searching Wikipedia: {e}")
            return self.create_result(
                point=point,
                content_type="text",
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
        navigation_words = ['turn', 'head', 'continue', 'slight', 'onto', 'toward', 'right', 'left']
        words = query.split()
        filtered_words = [w for w in words if w.lower() not in navigation_words]

        # If we filtered too much, use original
        if len(filtered_words) < 1:
            return query

        return ' '.join(filtered_words)

    def _get_wikipedia_summary(self, query: str, point: Optional[Point] = None) -> Optional[dict]:
        """
        Get Wikipedia summary for a query with fallback strategies.

        Args:
            query: Search query
            point: Optional point for additional context

        Returns:
            Wikipedia summary dict or None
        """
        search_api = "https://en.wikipedia.org/w/api.php"

        # Strategy 1: If we have location context, try with it first for better specificity
        if point and point.address:
            location_context = self._extract_location_context(point.address)
            if location_context:
                enhanced_query = f"{query} {location_context}"
                self.log_info(f"Searching with location context: {enhanced_query}")

                result = self._try_wikipedia_search(enhanced_query, search_api)
                if result:
                    return result

        # Strategy 2: Try direct lookup with original query
        search_url = f"{self.wikipedia_api}/page/summary/{query}"
        response = requests.get(search_url, headers=self.headers, timeout=5)

        if response.status_code == 200:
            data = response.json()
            # Skip disambiguation pages if we can
            if 'may refer to' not in data.get('extract', '').lower():
                return data

        # Strategy 3: Try search API with original query
        result = self._try_wikipedia_search(query, search_api)
        if result:
            return result

        return None

    def _try_wikipedia_search(self, query: str, search_api: str) -> Optional[dict]:
        """
        Try to find Wikipedia article using search API.

        Args:
            query: Search query
            search_api: Wikipedia search API endpoint

        Returns:
            Wikipedia summary dict or None
        """
        params = {
            'action': 'query',
            'list': 'search',
            'srsearch': query,
            'format': 'json',
            'srlimit': 1
        }
        search_response = requests.get(search_api, params=params, headers=self.headers, timeout=5)

        if search_response.status_code == 200:
            search_data = search_response.json()
            if search_data.get('query', {}).get('search'):
                page_title = search_data['query']['search'][0]['title']
                # Get summary for the found page
                summary_url = f"{self.wikipedia_api}/page/summary/{page_title}"
                summary_response = requests.get(summary_url, headers=self.headers, timeout=5)
                if summary_response.status_code == 200:
                    return summary_response.json()

        return None

    def _extract_location_context(self, address: str) -> Optional[str]:
        """
        Extract city or country from address for search context.

        Args:
            address: Full address string

        Returns:
            Location context string or None
        """
        import re

        # Common patterns: "Street, City" or "Street, City, Country"
        parts = [p.strip() for p in address.split(',')]

        if len(parts) < 2:
            return None

        # Clean up each part - remove postal codes and region abbreviations
        cleaned_parts = []
        for part in parts:
            # Remove leading postal codes (e.g., "00186 Roma RM" -> "Roma RM")
            part = re.sub(r'^\d+\s+', '', part)
            # Remove region codes at end (e.g., "Roma RM" -> "Roma")
            part = re.sub(r'\s+[A-Z]{2}$', '', part)
            # Skip very short parts (likely abbreviations) or empty
            part = part.strip()
            if len(part) > 2:
                cleaned_parts.append(part)

        # For better Wikipedia results, use just the city name (not full address)
        # This gives better specificity than country alone
        if len(cleaned_parts) >= 2:
            # Return just the city (second-to-last part, before country)
            return cleaned_parts[-2]
        elif len(cleaned_parts) == 1:
            return cleaned_parts[0]

        return None
