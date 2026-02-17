"""Example usage of extracting ALL points from a walking route."""

import os
import sys
import logging
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from src.api.google_maps import GoogleMapsClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)

def main():
    """Demonstrate extracting all points from a walking route."""
    # Load environment variables
    load_dotenv()

    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    if not api_key:
        print("Error: GOOGLE_MAPS_API_KEY not found in environment variables")
        print("Please create a .env file with your API key (see .env.example)")
        return

    # Example: Shortened Google Maps URL for walking route
    # Pantheon to Vatican City walking route
    shortened_url = "https://maps.app.goo.gl/5A5xc4qnSdL8DcVp6"

    print("Tour Guide - Walking Route Point Extraction")
    print("=" * 60)
    print(f"\nExtracting ALL points from walking route...\n")

    # Create client and extract all route points
    run_id = "route_run_001"
    client = GoogleMapsClient(api_key=api_key, run_id=run_id)

    try:
        points = client.extract_route_points_from_url(shortened_url)

        print(f"\n{'=' * 60}")
        print(f"Successfully extracted {len(points)} points from the route:\n")

        for point in points:
            print(f"  {point.order + 1}. {point.location_name}")
            print(f"     Coordinates: {point.coordinates}")
            if point.address:
                print(f"     Address: {point.address}")
            print()

    except Exception as e:
        print(f"\nError: {e}")
        return

    print("=" * 60)
    print("Next steps: These points will be processed by the orchestrator")
    print("to find relevant content (videos, music, text) for each location.")

if __name__ == "__main__":
    main()
