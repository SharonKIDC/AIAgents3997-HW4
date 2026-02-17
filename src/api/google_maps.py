"""Google Maps API integration for extracting route waypoints."""

import logging
import re
import requests
from typing import List
from urllib.parse import unquote

import googlemaps
from googlemaps.exceptions import ApiError

from src.models.point import Point, Coordinates


class GoogleMapsClient:
    """Client for interacting with Google Maps API."""

    def __init__(self, api_key: str, run_id: str):
        """
        Initialize Google Maps client.

        Args:
            api_key: Google Maps API key
            run_id: Unique identifier for this run (for logging)
        """
        self.client = googlemaps.Client(key=api_key)
        self.run_id = run_id
        self.logger = logging.getLogger(__name__)

    def extract_route_points_from_url(self, maps_url: str) -> List[Point]:
        """
        Extract ALL points along a walking route from a Google Maps URL.

        This method uses the Directions API to get the full walking route
        and extracts all points along the path, not just waypoints.

        Args:
            maps_url: Google Maps URL with route (supports shortened URLs)

        Returns:
            List of Point objects representing all points along the route

        Raises:
            ValueError: If URL format is invalid or no route found
        """
        self.logger.info(f"({self.run_id}, GoogleMapsClient, Extracting route points from URL)")

        # Expand shortened URL if needed
        expanded_url = self._expand_shortened_url(maps_url)
        self.logger.info(f"({self.run_id}, GoogleMapsClient, Processing URL: {expanded_url})")

        # Extract origin and destination from URL
        origin, destination = self._parse_url_for_origin_destination(expanded_url)

        if not origin or not destination:
            self.logger.error(f"({self.run_id}, GoogleMapsClient, Could not find origin/destination in URL)")
            raise ValueError("Could not extract origin and destination from URL")

        self.logger.info(f"({self.run_id}, GoogleMapsClient, Route: {origin} → {destination})")

        # Get directions from Google Maps API
        try:
            directions_result = self.client.directions(
                origin=origin,
                destination=destination,
                mode="walking"
            )

            if not directions_result:
                raise ValueError("No directions found")

            # Extract all points from the route
            points = self._extract_points_from_directions(directions_result[0])
            self.logger.info(f"({self.run_id}, GoogleMapsClient, Successfully extracted {len(points)} points from route)")
            return points

        except ApiError as e:
            self.logger.error(f"({self.run_id}, GoogleMapsClient, API error getting directions: {e})")
            raise ValueError(f"Google Maps API error: {e}")
        except Exception as e:
            self.logger.error(f"({self.run_id}, GoogleMapsClient, Error getting directions: {e})")
            raise

    def _expand_shortened_url(self, url: str) -> str:
        """
        Expand a shortened Google Maps URL (maps.app.goo.gl) to full URL.

        Args:
            url: Possibly shortened Google Maps URL

        Returns:
            Expanded URL
        """
        # If already a full URL, return as is
        if 'maps.app.goo.gl' not in url and 'goo.gl' not in url:
            return url

        try:
            # Follow redirects to get the full URL
            response = requests.head(url, allow_redirects=True, timeout=5)
            expanded = response.url
            self.logger.info(f"({self.run_id}, GoogleMapsClient, Expanded shortened URL)")
            return expanded
        except Exception as e:
            self.logger.warning(f"({self.run_id}, GoogleMapsClient, Failed to expand URL: {e})")
            return url

    def _parse_url_for_origin_destination(self, maps_url: str) -> tuple[str | None, str | None]:
        """
        Parse Google Maps URL to extract origin and destination.

        Args:
            maps_url: Google Maps URL

        Returns:
            Tuple of (origin, destination)
        """
        decoded_url = unquote(maps_url)

        # Extract locations from /dir/ pattern
        dir_match = re.search(r'/dir/([^/]+)/([^/@]+)', decoded_url)

        if not dir_match:
            return None, None

        origin = dir_match.group(1).strip()
        destination = dir_match.group(2).strip()

        # Clean up coordinate patterns if present
        if origin == "''":
            origin = None

        return origin, destination

    def _extract_points_from_directions(self, route: dict) -> List[Point]:
        """
        Extract all points from a directions route.

        Args:
            route: Route dictionary from Directions API

        Returns:
            List of Point objects for all steps in the route
        """
        points = []
        order = 0

        # Get all legs of the route
        for leg_idx, leg in enumerate(route.get('legs', [])):
            self.logger.info(f"({self.run_id}, GoogleMapsClient, Processing leg {leg_idx + 1}: {leg.get('distance', {}).get('text', 'unknown distance')})")

            # Extract point for each step
            for step_idx, step in enumerate(leg.get('steps', [])):
                # Get start location of this step
                start_location = step.get('start_location', {})

                if start_location:
                    coordinates = Coordinates(
                        lat=start_location['lat'],
                        lng=start_location['lng']
                    )

                    # Get address for this point (reverse geocoding)
                    location_name = step.get('html_instructions', f"Step {order + 1}")
                    # Clean HTML tags from instructions
                    location_name = re.sub(r'<[^>]+>', '', location_name)

                    point_id = f"{self.run_id}_point_{order}"
                    point = Point(
                        run_id=self.run_id,
                        point_id=point_id,
                        location_name=location_name,
                        coordinates=coordinates,
                        order=order,
                        place_id=None,
                        address=None
                    )
                    points.append(point)
                    order += 1

            # Add the end location of the last step in this leg
            if leg.get('steps'):
                last_step = leg['steps'][-1]
                end_location = last_step.get('end_location', {})

                if end_location:
                    coordinates = Coordinates(
                        lat=end_location['lat'],
                        lng=end_location['lng']
                    )

                    location_name = leg.get('end_address', f"Point {order + 1}")

                    point_id = f"{self.run_id}_point_{order}"
                    point = Point(
                        run_id=self.run_id,
                        point_id=point_id,
                        location_name=location_name,
                        coordinates=coordinates,
                        order=order,
                        place_id=None,
                        address=leg.get('end_address')
                    )
                    points.append(point)
                    order += 1

        return points

    def _parse_url_for_locations(self, maps_url: str) -> List[str]:
        """
        Parse Google Maps URL to extract location names.

        Google Maps URLs have format:
        /dir/''/Location1/Location2/Location3/...

        Args:
            maps_url: Google Maps URL

        Returns:
            List of location names
        """
        # Decode URL-encoded characters
        decoded_url = unquote(maps_url)

        # Extract the path part between /dir/ and /@coordinates or /data=
        # Pattern: /dir/''/Location1/Location2/.../
        dir_match = re.search(r'/dir/[^/]*/([^@]+)', decoded_url)

        if not dir_match:
            self.logger.warning(f"({self.run_id}, GoogleMapsClient, Could not find /dir/ pattern in URL)")
            return []

        locations_part = dir_match.group(1)

        # Split by '/' and filter out empty strings
        locations = [
            loc.strip()
            for loc in locations_part.split('/')
            if loc.strip() and not loc.startswith('data=')
        ]

        # Filter out coordinate patterns and data parameters
        locations = [
            loc for loc in locations
            if not re.match(r'^[\d\.,\-]+$', loc)  # Skip coordinate strings
            and not loc.startswith('!')
            and loc != "''"
        ]

        return locations

    def _geocode_location(self, location_name: str, order: int) -> Point:
        """
        Geocode a location name to get coordinates and details.

        Args:
            location_name: Name of the location
            order: Order in the route (0-based)

        Returns:
            Point object with geocoded information

        Raises:
            ValueError: If geocoding fails
        """
        try:
            # Use Geocoding API to get location details
            geocode_result = self.client.geocode(location_name)

            if not geocode_result:
                raise ValueError(f"No geocoding results for: {location_name}")

            # Take the first result
            result = geocode_result[0]

            # Extract coordinates
            location = result['geometry']['location']
            coordinates = Coordinates(
                lat=location['lat'],
                lng=location['lng']
            )

            # Extract place details
            place_id = result.get('place_id')
            formatted_address = result.get('formatted_address')
            formatted_name = result.get('formatted_address', location_name).split(',')[0]

            # Create Point object
            point_id = f"{self.run_id}_point_{order}"
            point = Point(
                run_id=self.run_id,
                point_id=point_id,
                location_name=formatted_name,
                coordinates=coordinates,
                order=order,
                place_id=place_id,
                address=formatted_address
            )

            return point

        except ApiError as e:
            self.logger.error(f"({self.run_id}, GoogleMapsClient, API error geocoding {location_name}: {e})")
            raise ValueError(f"Google Maps API error: {e}")
        except Exception as e:
            self.logger.error(f"({self.run_id}, GoogleMapsClient, Error geocoding {location_name}: {e})")
            raise

    def get_place_details(self, place_id: str) -> dict:
        """
        Get detailed information about a place.

        Args:
            place_id: Google Maps Place ID

        Returns:
            Dictionary with place details
        """
        try:
            place_details = self.client.place(place_id)
            self.logger.info(f"({self.run_id}, GoogleMapsClient, Retrieved place details for {place_id})")
            return place_details.get('result', {})
        except ApiError as e:
            self.logger.error(f"({self.run_id}, GoogleMapsClient, API error getting place details: {e})")
            raise
