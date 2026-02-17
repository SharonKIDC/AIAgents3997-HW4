"""Example usage of the four agents."""

import os
import sys
import logging
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from src.models.point import Point, Coordinates
from src.agents.youtube_agent import YouTubeAgent
from src.agents.spotify_agent import SpotifyAgent
from src.agents.text_agent import TextAgent
from src.agents.judge_agent import JudgeAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)

def main():
    """Demonstrate the four agents working together."""
    # Load environment variables
    load_dotenv()

    # Get API keys
    youtube_api_key = os.getenv('YOUTUBE_API_KEY')
    spotify_client_id = os.getenv('SPOTIFY_CLIENT_ID')
    spotify_client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')

    print("Tour Guide - Agent Demo")
    print("=" * 60)

    # Create a sample point (Pantheon in Rome)
    point = Point(
        run_id="demo_run",
        point_id="demo_point_1",
        location_name="Pantheon",
        coordinates=Coordinates(lat=41.8986108, lng=12.4768729),
        order=0,
        place_id="ChIJqUBg9g9_LxMRLM42IPpl0co",
        address="Piazza della Rotonda, 00186 Roma RM, Italy"
    )

    print(f"\nSearching for content about: {point.location_name}")
    print(f"Location: {point.address}")
    print(f"Coordinates: {point.coordinates}\n")
    print("=" * 60)

    run_id = "demo_run_001"
    results = []

    # Agent 1: YouTube
    if youtube_api_key:
        print("\n[1/4] YouTube Agent searching...")
        youtube_agent = YouTubeAgent(run_id=run_id, api_key=youtube_api_key)
        youtube_result = youtube_agent.search(point)
        results.append(youtube_result)

        if youtube_result.success:
            print(f"  ✓ Found: {youtube_result.content['title']}")
            print(f"  URL: {youtube_result.content['url']}")
        else:
            print(f"  ✗ Failed: {youtube_result.error_message}")
    else:
        print("\n[1/4] YouTube Agent - SKIPPED (no API key)")

    # Agent 2: Spotify
    if spotify_client_id and spotify_client_secret:
        print("\n[2/4] Spotify Agent searching...")
        spotify_agent = SpotifyAgent(
            run_id=run_id,
            client_id=spotify_client_id,
            client_secret=spotify_client_secret
        )
        spotify_result = spotify_agent.search(point)
        results.append(spotify_result)

        if spotify_result.success:
            print(f"  ✓ Found: {spotify_result.content['title']} by {spotify_result.content['artist']}")
            print(f"  URL: {spotify_result.content['url']}")
        else:
            print(f"  ✗ Failed: {spotify_result.error_message}")
    else:
        print("\n[2/4] Spotify Agent - SKIPPED (no API credentials)")

    # Agent 3: Text (Wikipedia)
    print("\n[3/4] Text Agent searching...")
    text_agent = TextAgent(run_id=run_id)
    text_result = text_agent.search(point)
    results.append(text_result)

    if text_result.success:
        print(f"  ✓ Found: {text_result.content['title']}")
        print(f"  Description: {text_result.content['description'][:150]}...")
        print(f"  URL: {text_result.content['url']}")
    else:
        print(f"  ✗ Failed: {text_result.error_message}")

    # Agent 4: Judge
    if results:
        print("\n[4/4] Judge Agent evaluating...")
        judge_agent = JudgeAgent(run_id=run_id)
        decision = judge_agent.judge(point, results)

        print(f"\n{'=' * 60}")
        print("JUDGE DECISION:")
        print(f"{'=' * 60}")
        print(f"Selected: {decision.selected_content_type.upper()}")
        if decision.selected_content:
            print(f"Title: {decision.selected_content.get('title', 'N/A')}")
            print(f"URL: {decision.selected_content.get('url', 'N/A')}")
        print(f"\nReasoning: {decision.reasoning}")
        print(f"{'=' * 60}")
    else:
        print("\n[4/4] Judge Agent - SKIPPED (no results to judge)")

    print("\nDemo complete!")

if __name__ == "__main__":
    main()
