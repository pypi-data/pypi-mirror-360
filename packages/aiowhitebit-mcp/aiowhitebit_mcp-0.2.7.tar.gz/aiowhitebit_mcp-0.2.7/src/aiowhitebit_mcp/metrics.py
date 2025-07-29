"""Metrics collection and reporting for the WhiteBit MCP server.

This module provides functionality for collecting and reporting metrics
about the WhiteBit MCP server's performance and usage.
"""

import logging
import time
from collections import defaultdict
from dataclasses import dataclass, field

# Set up logging
logger = logging.getLogger(__name__)


@dataclass
class RequestMetrics:
    """Metrics for a single request."""

    endpoint: str
    start_time: float
    end_time: float | None = None
    success: bool | None = None
    error: str | None = None

    @property
    def duration(self) -> float | None:
        """Get the duration of the request in seconds."""
        if self.end_time is None:
            return None
        return self.end_time - self.start_time

    def complete(self, success: bool, error: str | None = None) -> None:
        """Mark the request as complete.

        Args:
            success: Whether the request was successful
            error: Error message if the request failed
        """
        self.end_time = time.time()
        self.success = success
        self.error = error


@dataclass
class EndpointMetrics:
    """Metrics for a single endpoint."""

    endpoint: str
    request_count: int = 0
    success_count: int = 0
    error_count: int = 0
    total_duration: float = 0.0
    min_duration: float | None = None
    max_duration: float | None = None
    durations: list[float] = field(default_factory=list)
    errors: dict[str, int] = field(default_factory=lambda: defaultdict(int))

    def add_request(self, metrics: RequestMetrics) -> None:
        """Add a request to the endpoint metrics.

        Args:
            metrics: Metrics for the request
        """
        self.request_count += 1

        if metrics.success:
            self.success_count += 1
        else:
            self.error_count += 1
            if metrics.error:
                self.errors[metrics.error] += 1

        if metrics.duration is not None:
            duration = metrics.duration
            self.durations.append(duration)
            self.total_duration += duration

            if self.min_duration is None or duration < self.min_duration:
                self.min_duration = duration

            if self.max_duration is None or duration > self.max_duration:
                self.max_duration = duration

    @property
    def avg_duration(self) -> float | None:
        """Get the average duration of requests to this endpoint."""
        if not self.durations:
            return None
        return self.total_duration / len(self.durations)

    @property
    def success_rate(self) -> float | None:
        """Get the success rate of requests to this endpoint."""
        if self.request_count == 0:
            return None
        return self.success_count / self.request_count

    @property
    def p50(self) -> float | None:
        """Get the 50th percentile (median) duration."""
        if not self.durations:
            return None
        sorted_durations = sorted(self.durations)
        return sorted_durations[len(sorted_durations) // 2]

    @property
    def p95(self) -> float | None:
        """Get the 95th percentile duration."""
        if not self.durations:
            return None
        sorted_durations = sorted(self.durations)
        index = int(len(sorted_durations) * 0.95)
        return sorted_durations[index]

    @property
    def p99(self) -> float | None:
        """Get the 99th percentile duration."""
        if not self.durations:
            return None
        sorted_durations = sorted(self.durations)
        index = int(len(sorted_durations) * 0.99)
        return sorted_durations[index]


class MetricsCollector:
    """Collector for WhiteBit MCP server metrics.

    This class collects metrics about the WhiteBit MCP server's performance
    and usage, and provides methods for reporting those metrics.
    """

    def __init__(self):
        """Initialize the metrics collector."""
        self.endpoints: dict[str, EndpointMetrics] = {}
        self.active_requests: dict[str, RequestMetrics] = {}
        self.request_id_counter = 0

    def start_request(self, endpoint: str) -> str:
        """Start tracking a request.

        Args:
            endpoint: The endpoint being requested

        Returns:
            A unique ID for the request
        """
        request_id = str(self.request_id_counter)
        self.request_id_counter += 1

        metrics = RequestMetrics(endpoint=endpoint, start_time=time.time())

        self.active_requests[request_id] = metrics

        return request_id

    def end_request(self, request_id: str, success: bool, error: str | None = None) -> None:
        """End tracking a request.

        Args:
            request_id: The ID of the request
            success: Whether the request was successful
            error: Error message if the request failed
        """
        if request_id not in self.active_requests:
            logger.warning(f"Request ID {request_id} not found in active requests")
            return

        metrics = self.active_requests.pop(request_id)
        metrics.complete(success, error)

        endpoint = metrics.endpoint
        if endpoint not in self.endpoints:
            self.endpoints[endpoint] = EndpointMetrics(endpoint=endpoint)

        self.endpoints[endpoint].add_request(metrics)

    def get_endpoint_metrics(self, endpoint: str) -> EndpointMetrics | None:
        """Get metrics for a specific endpoint.

        Args:
            endpoint: The endpoint to get metrics for

        Returns:
            Metrics for the endpoint, or None if no metrics are available
        """
        return self.endpoints.get(endpoint)

    def get_all_endpoint_metrics(self) -> dict[str, EndpointMetrics]:
        """Get metrics for all endpoints.

        Returns:
            A dictionary mapping endpoint names to metrics
        """
        return self.endpoints.copy()

    def get_summary(self) -> dict[str, dict[str, float]]:
        """Get a summary of metrics for all endpoints.

        Returns:
            A dictionary mapping endpoint names to summary metrics
        """
        summary = {}

        for endpoint, metrics in self.endpoints.items():
            summary[endpoint] = {
                "request_count": metrics.request_count,
                "success_rate": metrics.success_rate or 0.0,
                "avg_duration": metrics.avg_duration or 0.0,
                "min_duration": metrics.min_duration or 0.0,
                "max_duration": metrics.max_duration or 0.0,
                "p50": metrics.p50 or 0.0,
                "p95": metrics.p95 or 0.0,
                "p99": metrics.p99 or 0.0,
            }

        return summary

    def reset(self) -> None:
        """Reset all metrics."""
        self.endpoints.clear()
        self.active_requests.clear()
        self.request_id_counter = 0


# Global metrics collector instance
metrics_collector = MetricsCollector()


def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector instance.

    Returns:
        The global metrics collector instance
    """
    return metrics_collector


def track_request(endpoint: str):
    """Decorator to track metrics for a request.

    Args:
        endpoint: The endpoint being requested

    Returns:
        A decorator that tracks metrics for the decorated function
    """

    def decorator(func):
        async def wrapper(*args, **kwargs):
            request_id = metrics_collector.start_request(endpoint)

            try:
                result = await func(*args, **kwargs)
                metrics_collector.end_request(request_id, success=True)
                return result
            except Exception as e:
                metrics_collector.end_request(request_id, success=False, error=str(e))
                raise

        return wrapper

    return decorator
