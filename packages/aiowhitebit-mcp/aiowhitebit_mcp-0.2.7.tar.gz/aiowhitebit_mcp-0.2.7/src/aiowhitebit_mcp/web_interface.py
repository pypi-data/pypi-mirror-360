"""Web interface for the WhiteBit MCP server.

This module provides a web interface for viewing metrics and health checks
for the WhiteBit MCP server.
"""

import logging
import os
from datetime import datetime

from aiohttp import web

from aiowhitebit_mcp.cache import clear_cache, get_all_caches
from aiowhitebit_mcp.circuit_breaker import get_all_circuit_breakers, reset_circuit_breaker
from aiowhitebit_mcp.metrics import get_metrics_collector
from aiowhitebit_mcp.monitoring import get_monitoring_server
from aiowhitebit_mcp.rate_limiter import get_rate_limiter

# Set up logging
logger = logging.getLogger(__name__)


# Load HTML templates from files
def load_template(filename):
    """Load a template from a file."""
    template_dir = os.path.join(os.path.dirname(__file__), "templates")
    with open(os.path.join(template_dir, filename)) as f:
        return f.read()


# Load templates
HTML_TEMPLATE = load_template("base.html")
DASHBOARD_TEMPLATE = load_template("dashboard.html")
HEALTH_TEMPLATE = load_template("health.html")
METRICS_TEMPLATE = load_template("metrics.html")
CIRCUIT_BREAKERS_TEMPLATE = load_template("circuit_breakers.html")
RATE_LIMITER_TEMPLATE = load_template("rate_limiter.html")
CACHE_TEMPLATE = load_template("cache.html")


class WebInterface:
    """Web interface for the WhiteBit MCP server.

    This class provides a web interface for viewing metrics and health checks
    for the WhiteBit MCP server.
    """

    def __init__(self, host: str = "localhost", port: int = 8080):
        """Initialize the web interface.

        Args:
            host: The host to bind to
            port: The port to bind to
        """
        self.host = host
        self.port = port
        self.app = web.Application()
        self.metrics_collector = get_metrics_collector()
        self.monitoring_server = get_monitoring_server()

        # Set up routes
        self.app.router.add_get("/", self.handle_dashboard)
        self.app.router.add_get("/health", self.handle_health)
        self.app.router.add_get("/metrics", self.handle_metrics)
        self.app.router.add_post("/reset-metrics", self.handle_reset_metrics)
        self.app.router.add_get("/circuit-breakers", self.handle_circuit_breakers)
        self.app.router.add_post("/reset-circuit-breaker/{name}", self.handle_reset_circuit_breaker)
        self.app.router.add_get("/rate-limiter", self.handle_rate_limiter)
        self.app.router.add_get("/cache", self.handle_cache)
        self.app.router.add_post("/clear-cache/{name}", self.handle_clear_cache)

        self.runner = None
        self.site = None

    async def start(self):
        """Start the web interface."""
        logger.info(f"Starting web interface on http://{self.host}:{self.port}")
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, self.host, self.port)
        await self.site.start()

    async def stop(self):
        """Stop the web interface."""
        logger.info("Stopping web interface")
        if self.site:
            await self.site.stop()
        if self.runner:
            await self.runner.cleanup()

    async def handle_dashboard(self, request):
        """Handle dashboard requests."""
        # Get health status
        health_status = await self.monitoring_server.health_check.run_checks()
        health_status_text = health_status["status"].upper()
        health_status_class = "healthy" if health_status_text == "HEALTHY" else "unhealthy"

        # Get circuit breaker status
        circuit_breakers = get_all_circuit_breakers()
        open_count = 0
        half_open_count = 0
        closed_count = 0

        for circuit in circuit_breakers.values():
            if circuit.state.value == "open":
                open_count += 1
            elif circuit.state.value == "half-open":
                half_open_count += 1
            else:
                closed_count += 1

        circuit_breaker_summary = f"""
        <span class="circuit-closed">{closed_count} Closed</span>,
        <span class="circuit-open">{open_count} Open</span>,
        <span class="circuit-half-open">{half_open_count} Half-Open</span>
        """

        # Get cache status
        caches = get_all_caches()
        total_entries = 0
        valid_entries = 0
        invalid_entries = 0

        for cache in caches.values():
            stats = cache.get_stats()
            total_entries += stats["total_entries"]
            valid_entries += stats["valid_entries"]
            invalid_entries += stats["invalid_entries"]

        cache_summary = f"""
        <strong>Total Caches:</strong> {len(caches)}<br>
        <strong>Valid Entries:</strong> {valid_entries}<br>
        <strong>Invalid Entries:</strong> {invalid_entries}<br>
        <strong>Total Entries:</strong> {total_entries}
        """

        # Get metrics summary
        metrics_summary = self.metrics_collector.get_summary()
        metrics_labels = []
        metrics_data = []

        for endpoint, metrics in metrics_summary.items():
            metrics_labels.append(f'"{endpoint}"')
            metrics_data.append(metrics["request_count"])

        # Render dashboard
        content = DASHBOARD_TEMPLATE.format(
            health_status=health_status_text,
            health_status_class=health_status_class,
            circuit_breaker_summary=circuit_breaker_summary,
            cache_summary=cache_summary,
            metrics_labels=f"[{', '.join(metrics_labels)}]",
            metrics_data=f"[{', '.join(map(str, metrics_data))}]",
        )

        html = HTML_TEMPLATE.format(title="WhiteBit MCP Dashboard", content=content)

        return web.Response(text=html, content_type="text/html")

    async def handle_health(self, request):
        """Handle health check requests."""
        health_status = await self.monitoring_server.health_check.run_checks()
        health_status_text = health_status["status"].upper()
        health_status_class = "healthy" if health_status_text == "HEALTHY" else "unhealthy"

        health_checks = ""
        for name, check in health_status["checks"].items():
            check_status = check["status"].upper()
            check_status_class = "healthy" if check_status == "HEALTHY" else "unhealthy"
            last_updated = datetime.fromtimestamp(check["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")

            details = ""
            for key, value in check.items():
                if key not in ["status", "timestamp"]:
                    details += f"<strong>{key}:</strong> {value}<br>"

            health_checks += f"""
            <tr>
                <td>{name}</td>
                <td><span class="status-{check_status_class}">{check_status}</span></td>
                <td>{last_updated}</td>
                <td>{details}</td>
            </tr>
            """

        content = HEALTH_TEMPLATE.format(
            health_status=health_status_text, health_status_class=health_status_class, health_checks=health_checks
        )

        html = HTML_TEMPLATE.format(title="WhiteBit MCP Health Checks", content=content)

        return web.Response(text=html, content_type="text/html")

    async def handle_metrics(self, request):
        """Handle metrics requests."""
        metrics_summary = self.metrics_collector.get_summary()

        metrics_rows = ""
        for endpoint, metrics in metrics_summary.items():
            success_rate = f"{metrics['success_rate'] * 100:.2f}%"
            avg_duration = f"{metrics['avg_duration'] * 1000:.2f}"
            p95_duration = f"{metrics['p95'] * 1000:.2f}"

            metrics_rows += f"""
            <tr>
                <td>{endpoint}</td>
                <td>{metrics["request_count"]}</td>
                <td>{success_rate}</td>
                <td>{avg_duration}</td>
                <td>{p95_duration}</td>
            </tr>
            """

        content = METRICS_TEMPLATE.format(metrics_rows=metrics_rows)

        html = HTML_TEMPLATE.format(title="WhiteBit MCP Metrics", content=content)

        return web.Response(text=html, content_type="text/html")

    async def handle_reset_metrics(self, request):
        """Handle reset metrics requests."""
        self.metrics_collector.reset()
        raise web.HTTPFound("/metrics")

    async def handle_circuit_breakers(self, request):
        """Handle circuit breaker requests."""
        circuit_breakers = get_all_circuit_breakers()

        circuit_breaker_rows = ""
        for name, circuit in circuit_breakers.items():
            state = circuit.state.value.upper()
            state_class = {"CLOSED": "circuit-closed", "OPEN": "circuit-open", "HALF-OPEN": "circuit-half-open"}.get(
                state, ""
            )

            last_failure = "Never"
            if circuit.last_failure_time > 0:
                last_failure = datetime.fromtimestamp(circuit.last_failure_time).strftime("%Y-%m-%d %H:%M:%S")

            circuit_breaker_rows += f"""
            <tr>
                <td>{name}</td>
                <td><span class="{state_class}">{state}</span></td>
                <td>{circuit.failure_count}</td>
                <td>{last_failure}</td>
                <td>
                    <form action="/reset-circuit-breaker/{name}" method="post">
                        <button type="submit" class="btn btn-sm btn-warning">Reset</button>
                    </form>
                </td>
            </tr>
            """

        content = CIRCUIT_BREAKERS_TEMPLATE.format(circuit_breaker_rows=circuit_breaker_rows)

        html = HTML_TEMPLATE.format(title="WhiteBit MCP Circuit Breakers", content=content)

        return web.Response(text=html, content_type="text/html")

    async def handle_reset_circuit_breaker(self, request):
        """Handle reset circuit breaker requests."""
        name = request.match_info["name"]
        reset_circuit_breaker(name)
        raise web.HTTPFound("/circuit-breakers")

    async def handle_rate_limiter(self, request):
        """Handle rate limiter requests."""
        rate_limiter = get_rate_limiter()
        status = rate_limiter.get_status()

        rate_limiter_rows = ""
        for name, endpoint_status in status.items():
            can_request = "Available" if endpoint_status["can_request"] else "Rate Limited"
            can_request_class = "text-success" if endpoint_status["can_request"] else "text-danger"
            time_until_available = f"{endpoint_status['time_until_available']:.2f} seconds"

            rules_html = ""
            for rule in endpoint_status["rules"]:
                rules_html += f"""
                <div>
                    <strong>Max Requests:</strong> {rule["max_requests"]}<br>
                    <strong>Period:</strong> {rule["period_seconds"]} seconds<br>
                    <strong>Current:</strong> {rule["current_requests"]}/{rule["max_requests"]}
                </div>
                <hr>
                """

            rate_limiter_rows += f"""
            <tr>
                <td>{name}</td>
                <td><span class="{can_request_class}">{can_request}</span></td>
                <td>{time_until_available}</td>
                <td>{rules_html}</td>
            </tr>
            """

        content = RATE_LIMITER_TEMPLATE.format(rate_limiter_rows=rate_limiter_rows)

        html = HTML_TEMPLATE.format(title="WhiteBit MCP Rate Limiter", content=content)

        return web.Response(text=html, content_type="text/html")

    async def handle_cache(self, request):
        """Handle cache requests."""
        caches = get_all_caches()

        cache_rows = ""
        for name, cache in caches.items():
            stats = cache.get_stats()
            persist = "Yes" if stats["persist"] else "No"

            cache_rows += f"""
            <tr>
                <td>{name}</td>
                <td>{stats["valid_entries"]}</td>
                <td>{stats["invalid_entries"]}</td>
                <td>{stats["total_entries"]}</td>
                <td>{persist}</td>
                <td>
                    <form action="/clear-cache/{name}" method="post">
                        <button type="submit" class="btn btn-sm btn-warning">Clear</button>
                    </form>
                </td>
            </tr>
            """

        content = CACHE_TEMPLATE.format(cache_rows=cache_rows)

        html = HTML_TEMPLATE.format(title="WhiteBit MCP Cache", content=content)

        return web.Response(text=html, content_type="text/html")

    async def handle_clear_cache(self, request):
        """Handle clear cache requests."""
        name = request.match_info["name"]
        clear_cache(name)
        raise web.HTTPFound("/cache")


# Global web interface instance
web_interface = None


def get_web_interface(host: str = "localhost", port: int = 8080) -> WebInterface:
    """Get the global web interface instance.

    Args:
        host: The host to bind to
        port: The port to bind to

    Returns:
        The global web interface instance
    """
    global web_interface

    if web_interface is None:
        web_interface = WebInterface(host=host, port=port)

    return web_interface


async def start_web_interface(host: str = "localhost", port: int = 8080):
    """Start the web interface.

    Args:
        host: The host to bind to
        port: The port to bind to
    """
    interface = get_web_interface(host=host, port=port)
    await interface.start()


async def stop_web_interface():
    """Stop the web interface."""
    global web_interface

    if web_interface is not None:
        await web_interface.stop()
        web_interface = None
