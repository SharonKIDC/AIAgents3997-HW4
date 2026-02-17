#!/usr/bin/env python3
"""
AI Tour Guide - Main Entry Point

Processes Google Maps walking routes and generates multimedia content recommendations.
"""

import os
import sys
import logging
import argparse
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.api.google_maps import GoogleMapsClient  # pylint: disable=wrong-import-position
from src.orchestrator import Orchestrator  # pylint: disable=wrong-import-position


def setup_logging(log_level: str, log_file: str = "tour_guide.log"):
    """
    Setup thread-safe logging to file only.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Path to log file
    """
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Create formatter with timestamp
    formatter = logging.Formatter(
        '%(asctime)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # File handler only (thread-safe) - all logs go to file
    file_handler = logging.FileHandler(log_file, mode='a')
    file_handler.setLevel(numeric_level)
    file_handler.setFormatter(formatter)

    # Configure root logger - NO console handler
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    root_logger.addHandler(file_handler)

    return root_logger


def print_banner():
    """Print welcome banner."""
    print("=" * 70)
    print("AI Tour Guide - Multimedia Content Generator")
    print("=" * 70)
    print("Enter Google Maps walking route URLs to process.")
    print("Type 'stop' to exit the program.")
    print("=" * 70)
    print()


def format_decision_summary(point, decision, point_number, total_points):
    """
    Format brief summary of judge decision for console output.

    Args:
        point: Point object
        decision: JudgeDecision object
        point_number: Current point number (1-indexed)
        total_points: Total number of points

    Returns:
        Formatted string
    """
    content = decision.selected_content
    content_title = content.get('title', 'N/A') if content else 'N/A'

    # Format: Point X/Y: Location -> Type: Title
    location = f"{point.location_name[:50]:50s}"
    content_type = f"{decision.selected_content_type.upper():5s}"
    return f"  Point {point_number:2d}/{total_points}: {location} -> {content_type}: {content_title[:50]}"


def process_map_url(url: str, google_api_key: str, youtube_api_key: str,
                   spotify_client_id: str, spotify_client_secret: str, run_id: str):
    """
    Process a Google Maps URL and generate tour guide content.

    Args:
        url: Google Maps URL
        google_api_key: Google Maps API key
        youtube_api_key: YouTube API key
        spotify_client_id: Spotify client ID
        spotify_client_secret: Spotify client secret
        run_id: Unique run identifier
    """
    logger = logging.getLogger(__name__)

    # Extract route points
    try:
        maps_client = GoogleMapsClient(api_key=google_api_key, run_id=run_id)
        points = maps_client.extract_route_points_from_url(url)

        if not points:
            print("ERROR: No points extracted from URL")
            return

        # Print initial summary
        print(f"\nGot map URL: {url}")
        print(f"Run ID: {run_id}")
        print(f"Added {len(points) * 4} tasks for {len(points)} points to orchestrator")
        print("Processing...\n")

    except Exception as e:
        print(f"ERROR: Failed to extract route points: {e}")
        logger.error(f"({run_id}, Main, Route extraction failed: {e})")
        return

    # Process points with orchestrator
    try:
        orchestrator = Orchestrator(
            run_id=run_id,
            youtube_api_key=youtube_api_key,
            spotify_client_id=spotify_client_id,
            spotify_client_secret=spotify_client_secret,
            max_workers=10
        )

        decisions = orchestrator.process_points(points)

        # Display final summary
        print("=" * 120)
        print("TOUR GUIDE SUMMARY")
        print("=" * 120)

        for point in points:
            decision = decisions.get(point.point_id)
            if decision:
                # Log detailed reasoning to file
                logger.info(f"({run_id}, Judge, Point {point.order + 1}: {decision.reasoning})")

                # Print brief summary to console
                summary = format_decision_summary(
                    point=point,
                    decision=decision,
                    point_number=point.order + 1,
                    total_points=len(points)
                )
                print(summary)

        print("=" * 120)
        print(f"Complete! Processed {len(decisions)}/{len(points)} points. Check log file for details.\n")

        orchestrator.shutdown()

    except Exception as e:
        print(f"ERROR: Processing failed: {e}")
        logger.error(f"({run_id}, Main, Processing failed: {e})")


def main():
    """Main entry point."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='AI Tour Guide - Generate multimedia content for walking routes'
    )
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Set logging level (default: INFO)'
    )
    parser.add_argument(
        '--log-file',
        default='tour_guide.log',
        help='Log file path (default: tour_guide.log)'
    )

    args = parser.parse_args()

    # Setup logging
    logger = setup_logging(args.log_level, args.log_file)

    # Load environment variables
    load_dotenv()

    # Get API keys
    google_api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    youtube_api_key = os.getenv('YOUTUBE_API_KEY')
    spotify_client_id = os.getenv('SPOTIFY_CLIENT_ID')
    spotify_client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')

    # Validate required API keys
    if not google_api_key:
        print("ERROR: GOOGLE_MAPS_API_KEY not found in environment variables")
        print("Please set it in your .env file")
        sys.exit(1)

    # Print banner
    print_banner()

    # Main loop - continuous processing
    run_counter = 0
    try:
        while True:
            # Get input
            try:
                user_input = input("Enter Google Maps URL (or 'stop' to exit): ").strip()
            except EOFError:
                print("\nReceived EOF, exiting...")
                break

            # Check for stop command
            if user_input.lower() == 'stop':
                print("\nStopping tour guide...")
                break

            # Skip empty input
            if not user_input:
                continue

            # Validate it looks like a URL
            if not user_input.startswith('http'):
                print("ERROR: Input doesn't look like a URL. Please enter a Google Maps URL.")
                continue

            # Process the URL
            run_counter += 1
            run_id = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{run_counter}"

            try:
                process_map_url(
                    url=user_input,
                    google_api_key=google_api_key,
                    youtube_api_key=youtube_api_key,
                    spotify_client_id=spotify_client_id,
                    spotify_client_secret=spotify_client_secret,
                    run_id=run_id
                )
            except KeyboardInterrupt:
                print("\n\nInterrupted by user. Stopping...")
                break
            except Exception as e:
                print(f"\nERROR: Unexpected error: {e}")
                logger.error(f"({run_id}, Main, Unexpected error: {e})")

    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Exiting...")

    print("\nGoodbye!")
    logging.shutdown()


if __name__ == "__main__":
    main()
