"""Orchestrator for managing multi-threaded agent execution."""

import logging
import threading
from queue import PriorityQueue, Queue
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime

from src.models.point import Point
from src.models.agent_result import AgentResult, JudgeDecision
from src.agents.youtube_agent import YouTubeAgent
from src.agents.spotify_agent import SpotifyAgent
from src.agents.text_agent import TextAgent
from src.agents.judge_agent import JudgeAgent


@dataclass
class Task:
    """Represents a task to be executed."""
    priority: int  # Lower number = higher priority
    point: Point
    task_type: str  # 'search' or 'judge'
    timestamp: datetime

    def __lt__(self, other):
        """Compare tasks by priority for PriorityQueue."""
        if self.priority != other.priority:
            return self.priority < other.priority
        return self.timestamp < other.timestamp


class Orchestrator:
    """Orchestrates multi-threaded agent execution for tour points."""

    PRIORITY_JUDGE = 1
    PRIORITY_SEARCH = 2

    def __init__(
        self,
        run_id: str,
        youtube_api_key: Optional[str] = None,
        spotify_client_id: Optional[str] = None,
        spotify_client_secret: Optional[str] = None,
        max_workers: int = 10
    ):
        """
        Initialize orchestrator.

        Args:
            run_id: Unique identifier for this run
            youtube_api_key: YouTube API key
            spotify_client_id: Spotify client ID
            spotify_client_secret: Spotify client secret
            max_workers: Maximum number of worker threads
        """
        self.run_id = run_id
        self.logger = logging.getLogger(f"{__name__}.{run_id}")

        # API credentials
        self.youtube_api_key = youtube_api_key
        self.spotify_client_id = spotify_client_id
        self.spotify_client_secret = spotify_client_secret

        # Thread-safe queues
        self.task_queue = PriorityQueue()
        self.result_queue = Queue()

        # Thread pool
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

        # Storage for results by point_id
        self.results_by_point: Dict[str, List[AgentResult]] = {}
        self.decisions_by_point: Dict[str, JudgeDecision] = {}
        self.results_lock = threading.Lock()

        # Tracking
        self.points_processed = 0
        self.total_points = 0

        self.logger.info(f"({run_id}, Orchestrator, Initialized with {max_workers} workers)")

    def process_points(self, points: List[Point]) -> Dict[str, JudgeDecision]:
        """
        Process all points and return judge decisions.

        Args:
            points: List of points to process

        Returns:
            Dictionary mapping point_id to JudgeDecision
        """
        self.total_points = len(points)
        self.points_processed = 0
        self.logger.info(f"({self.run_id}, Orchestrator, Processing {len(points)} points)")

        # Submit all search tasks
        for point in points:
            task = Task(
                priority=self.PRIORITY_SEARCH,
                point=point,
                task_type='search',
                timestamp=datetime.now()
            )
            self.task_queue.put(task)

        # Process tasks until all points are judged
        futures = []
        while self.points_processed < self.total_points or not self.task_queue.empty():
            # Get next task
            try:
                task = self.task_queue.get(timeout=1)
            except:
                continue

            # Submit task to executor
            if task.task_type == 'search':
                future = self.executor.submit(self._execute_search_agents, task.point)
            else:  # judge
                future = self.executor.submit(self._execute_judge_agent, task.point)

            futures.append(future)

        # Wait for all tasks to complete
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                self.logger.error(f"({self.run_id}, Orchestrator, Task failed: {e})")

        self.logger.info(f"({self.run_id}, Orchestrator, Completed processing all points)")
        return self.decisions_by_point.copy()

    def _execute_search_agents(self, point: Point):
        """
        Execute all search agents for a point.

        Args:
            point: Point to search for
        """
        self.logger.info(f"({self.run_id}, Orchestrator, Starting search agents for: {point.location_name})")

        results = []

        # YouTube Agent
        if self.youtube_api_key:
            try:
                youtube_agent = YouTubeAgent(run_id=self.run_id, api_key=self.youtube_api_key)
                result = youtube_agent.search(point)
                results.append(result)
            except Exception as e:
                self.logger.error(f"({self.run_id}, Orchestrator, YouTube agent failed: {e})")

        # Spotify Agent
        if self.spotify_client_id and self.spotify_client_secret:
            try:
                spotify_agent = SpotifyAgent(
                    run_id=self.run_id,
                    client_id=self.spotify_client_id,
                    client_secret=self.spotify_client_secret
                )
                result = spotify_agent.search(point)
                results.append(result)
            except Exception as e:
                self.logger.error(f"({self.run_id}, Orchestrator, Spotify agent failed: {e})")

        # Text Agent
        try:
            text_agent = TextAgent(run_id=self.run_id)
            result = text_agent.search(point)
            results.append(result)
        except Exception as e:
            self.logger.error(f"({self.run_id}, Orchestrator, Text agent failed: {e})")

        # Store results
        with self.results_lock:
            self.results_by_point[point.point_id] = results

        # Queue judge task (high priority)
        judge_task = Task(
            priority=self.PRIORITY_JUDGE,
            point=point,
            task_type='judge',
            timestamp=datetime.now()
        )
        self.task_queue.put(judge_task)

        self.logger.info(f"({self.run_id}, Orchestrator, Completed search agents for: {point.location_name})")

    def _execute_judge_agent(self, point: Point):
        """
        Execute judge agent for a point.

        Args:
            point: Point to judge
        """
        self.logger.info(f"({self.run_id}, Orchestrator, Starting judge for: {point.location_name})")

        # Get results for this point
        with self.results_lock:
            results = self.results_by_point.get(point.point_id, [])

        if not results:
            self.logger.warning(f"({self.run_id}, Orchestrator, No results available for: {point.location_name})")
            self.points_processed += 1
            return

        # Execute judge
        try:
            judge_agent = JudgeAgent(run_id=self.run_id)
            decision = judge_agent.judge(point, results)

            with self.results_lock:
                self.decisions_by_point[point.point_id] = decision

            self.logger.info(f"({self.run_id}, Orchestrator, Judge completed for: {point.location_name})")
        except Exception as e:
            self.logger.error(f"({self.run_id}, Orchestrator, Judge failed: {e})")

        self.points_processed += 1

    def shutdown(self):
        """Shutdown the orchestrator and cleanup resources."""
        self.logger.info(f"({self.run_id}, Orchestrator, Shutting down)")
        self.executor.shutdown(wait=True)
