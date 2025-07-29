"""Monitoring for the WhiteBit MCP server.

This module provides functionality for monitoring the WhiteBit MCP server's
health and performance.
"""

import logging
import time
from typing import Any

from fastmcp import FastMCP

from aiowhitebit_mcp.cache import clear_cache, get_all_caches
from aiowhitebit_mcp.circuit_breaker import get_all_circuit_breakers
from aiowhitebit_mcp.metrics import get_metrics_collector
from aiowhitebit_mcp.rate_limiter import get_rate_limiter

# Set up logging
logger = logging.getLogger(__name__)


class HealthCheck:
    """Health check for the WhiteBit MCP server.

    This class provides methods for checking the health of the WhiteBit MCP server
    and its dependencies.
    """

    def __init__(self):
        """Initialize the health check."""
        self.checks = {}
        self.last_check_time = 0
        self.check_interval = 60  # seconds
        self.is_healthy = True
        self.health_status = {"status": "healthy", "checks": {}}

    def register_check(self, name: str, check_func):
        """Register a health check function.

        Args:
            name: The name of the health check
            check_func: The function to call to perform the health check
        """
        self.checks[name] = check_func

    async def run_checks(self) -> dict[str, Any]:
        """Run all registered health checks.

        Returns:
            A dictionary containing the results of all health checks
        """
        current_time = time.time()

        # Only run checks if the check interval has elapsed
        if current_time - self.last_check_time < self.check_interval:
            return self.health_status

        self.last_check_time = current_time
        self.is_healthy = True
        self.health_status = {"status": "healthy", "checks": {}}

        for name, check_func in self.checks.items():
            try:
                result = await check_func()
                self.health_status["checks"][name] = {"status": "healthy", "timestamp": current_time}

                if isinstance(result, dict):
                    self.health_status["checks"][name].update(result)
            except Exception as e:
                logger.error(f"Health check {name} failed: {e}")
                self.is_healthy = False
                self.health_status["checks"][name] = {"status": "unhealthy", "error": str(e), "timestamp": current_time}

        if not self.is_healthy:
            self.health_status["status"] = "unhealthy"

        return self.health_status


class MonitoringServer:
    """Monitoring server for the WhiteBit MCP server.

    This class provides an MCP server that exposes monitoring endpoints
    for the WhiteBit MCP server.
    """

    def __init__(self, name: str = "WhiteBit MCP Monitoring"):
        """Initialize the monitoring server.

        Args:
            name: The name of the monitoring server
        """
        self.name = name
        self.mcp = FastMCP(name=name)
        self.health_check = HealthCheck()
        self.metrics_collector = get_metrics_collector()

        # Register monitoring tools
        self._register_monitoring_tools()

    def _register_monitoring_tools(self):
        """Register monitoring tools."""

        @self.mcp.tool()
        async def health() -> dict:
            """Get the health status of the WhiteBit MCP server."""
            return await self.health_check.run_checks()

        @self.mcp.tool()
        async def metrics() -> dict:
            """Get metrics for the WhiteBit MCP server."""
            return self.metrics_collector.get_summary()

        @self.mcp.tool()
        async def reset_metrics() -> dict:
            """Reset all metrics."""
            self.metrics_collector.reset()
            return {"status": "ok", "message": "Metrics reset successfully"}

        @self.mcp.tool()
        async def circuit_breakers() -> dict:
            """Get the status of all circuit breakers."""
            result = {}
            for name, circuit in get_all_circuit_breakers().items():
                result[name] = circuit.get_state()
            return result

        @self.mcp.tool()
        async def reset_circuit_breaker(name: str) -> dict:
            """Reset a circuit breaker.

            Args:
                name: The name of the circuit breaker to reset
            """
            success = reset_circuit_breaker(name)  # type: ignore
            if success:
                return {"status": "ok", "message": f"Circuit breaker {name} reset successfully"}
            else:
                return {"status": "error", "message": f"Circuit breaker {name} not found"}

        @self.mcp.tool()
        async def rate_limiter_status() -> dict:
            """Get the status of the rate limiter."""
            rate_limiter = get_rate_limiter()
            return rate_limiter.get_status()

        @self.mcp.tool()
        async def cache_status() -> dict:
            """Get the status of all caches."""
            caches = get_all_caches()
            result = {}
            for name, cache in caches.items():
                result[name] = cache.get_stats()
            return result

        @self.mcp.tool()
        async def clear_cache_by_name(name: str) -> dict:
            """Clear a cache by name.

            Args:
                name: The name of the cache to clear
            """
            success = clear_cache(name)
            if success:
                return {"status": "ok", "message": f"Cache {name} cleared successfully"}
            else:
                return {"status": "error", "message": f"Cache {name} not found"}

    def register_health_check(self, name: str, check_func):
        """Register a health check function.

        Args:
            name: The name of the health check
            check_func: The function to call to perform the health check
        """
        self.health_check.register_check(name, check_func)


# Global monitoring server instance
monitoring_server = None


def get_monitoring_server(name: str = "WhiteBit MCP Monitoring") -> MonitoringServer:
    """Get the global monitoring server instance.

    Args:
        name: The name of the monitoring server

    Returns:
        The global monitoring server instance
    """
    global monitoring_server

    if monitoring_server is None:
        monitoring_server = MonitoringServer(name=name)

    return monitoring_server


def register_health_check(name: str, check_func):
    """Register a health check function with the global monitoring server.

    Args:
        name: The name of the health check
        check_func: The function to call to perform the health check
    """
    server = get_monitoring_server()
    server.register_health_check(name, check_func)
