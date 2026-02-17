"""Tests for Google Maps API integration."""

from unittest.mock import Mock, patch

from src.api.google_maps import GoogleMapsClient
from src.models.point import Point, Coordinates


class TestGoogleMapsClient:
    """Test suite for GoogleMapsClient."""

    @patch('googlemaps.Client')
    def test_expand_shortened_url(self, mock_gmaps_client):
        """Test expanding shortened Google Maps URL."""
        mock_client_instance = Mock()
        mock_gmaps_client.return_value = mock_client_instance

        client = GoogleMapsClient(api_key="AIza_test_key", run_id="test_run")

        # Test with regular URL (should return as-is)
        regular_url = "https://www.google.com/maps/dir/Pantheon/Vatican+City/@41.9001505,12.4845882,15.25z"
        result = client._expand_shortened_url(regular_url)
        assert result == regular_url

    @patch('googlemaps.Client')
    def test_parse_url_for_origin_destination(self, mock_gmaps_client):
        """Test extracting origin and destination from URL."""
        mock_client_instance = Mock()
        mock_gmaps_client.return_value = mock_client_instance

        client = GoogleMapsClient(api_key="AIza_test_key", run_id="test_run")

        # Test URL with origin and destination
        url = "https://www.google.com/maps/dir/Pantheon/Vatican+City/@41.9001505,12.4845882,15.25z"
        origin, destination = client._parse_url_for_origin_destination(url)

        assert origin == "Pantheon"
        assert destination == "Vatican+City"

    @patch('googlemaps.Client')
    def test_extract_route_points_from_url(self, mock_gmaps_client):
        """Test full route point extraction from URL."""
        # Mock the directions API response
        mock_client_instance = Mock()
        mock_client_instance.directions.return_value = [{
            'legs': [{
                'distance': {'text': '2.5 km'},
                'end_address': 'Vatican City',
                'steps': [
                    {
                        'start_location': {'lat': 41.8986108, 'lng': 12.4768729},
                        'end_location': {'lat': 41.8990000, 'lng': 12.4770000},
                        'html_instructions': 'Head <b>west</b> on Via della Strada'
                    },
                    {
                        'start_location': {'lat': 41.8990000, 'lng': 12.4770000},
                        'end_location': {'lat': 41.9021788, 'lng': 12.4536007},
                        'html_instructions': 'Turn <b>left</b> onto Via Roma'
                    }
                ]
            }]
        }]
        mock_gmaps_client.return_value = mock_client_instance

        # Simplified URL for testing
        url = "https://www.google.com/maps/dir/Pantheon/Vatican+City/@41.9001505,12.4845882,15.25z"

        client = GoogleMapsClient(api_key="AIza_test_key", run_id="test_run")
        points = client.extract_route_points_from_url(url)

        # Should extract 3 points: start of step 1, start of step 2, and end of last step
        assert len(points) == 3
        assert points[0].location_name == "Head west on Via della Strada"
        assert points[1].location_name == "Turn left onto Via Roma"
        assert points[2].location_name == "Vatican City"

        # Verify coordinates
        assert points[0].coordinates.lat == 41.8986108
        assert points[0].coordinates.lng == 12.4768729

    @patch('googlemaps.Client')
    def test_extract_points_from_directions(self, mock_gmaps_client):
        """Test extracting points from directions response."""
        mock_client_instance = Mock()
        mock_gmaps_client.return_value = mock_client_instance

        client = GoogleMapsClient(api_key="AIza_test_key", run_id="test_run")

        # Mock route data
        route = {
            'legs': [{
                'distance': {'text': '1.0 km'},
                'end_address': 'Destination Address',
                'steps': [
                    {
                        'start_location': {'lat': 41.8986108, 'lng': 12.4768729},
                        'end_location': {'lat': 41.8990000, 'lng': 12.4770000},
                        'html_instructions': 'Walk <b>north</b>'
                    }
                ]
            }]
        }

        points = client._extract_points_from_directions(route)

        assert len(points) == 2  # Start of step and end of leg
        assert points[0].location_name == "Walk north"
        assert points[1].address == "Destination Address"


def test_point_model():
    """Test Point data model."""
    coords = Coordinates(lat=41.8986108, lng=12.4768729)
    point = Point(
        run_id="test_run",
        point_id="test_point_0",
        location_name="Piazza Navona",
        coordinates=coords,
        order=0,
        place_id="test_place_id"
    )

    assert point.location_name == "Piazza Navona"
    assert point.coordinates.lat == 41.8986108
    assert point.order == 0
    assert str(coords) == "(41.8986108, 12.4768729)"


def test_coordinates_model():
    """Test Coordinates data model."""
    coords = Coordinates(lat=41.9, lng=12.5)
    assert coords.lat == 41.9
    assert coords.lng == 12.5
    assert str(coords) == "(41.9, 12.5)"
