"""Rate limiter for the WhiteBit MCP server.

This module provides a rate limiter for the WhiteBit MCP server to prevent
exceeding API quotas.
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from functools import wraps
from typing import Any

# Set up logging
logger = logging.getLogger(__name__)


@dataclass
class RateLimitRule:
    """Rate limit rule.

    This class defines a rate limit rule, which specifies the maximum number
    of requests allowed in a given time period.

    Attributes:
        max_requests: Maximum number of requests allowed in the time period
        period_seconds: Time period in seconds
        requests: List of timestamps of recent requests
    """

    max_requests: int
    period_seconds: float
    requests: list[float] = field(default_factory=list)

    def add_request(self):
        """Add a request to the rule.

        This method adds the current timestamp to the list of requests and
        removes any expired requests.
        """
        now = time.time()
        self.requests.append(now)

        # Remove expired requests
        cutoff = now - self.period_seconds
        self.requests = [t for t in self.requests if t >= cutoff]

    def can_request(self) -> bool:
        """Check if a request is allowed.

        Returns:
            True if the request is allowed, False otherwise
        """
        now = time.time()

        # Remove expired requests
        cutoff = now - self.period_seconds
        self.requests = [t for t in self.requests if t >= cutoff]

        # Check if we're under the limit
        return len(self.requests) < self.max_requests

    def time_until_available(self) -> float:
        """Get the time until a request is available.

        Returns:
            Time in seconds until a request is available, or 0 if a request is
            already available
        """
        if self.can_request():
            return 0

        now = time.time()
        oldest_request = self.requests[0]
        return oldest_request + self.period_seconds - now


class RateLimiter:
    """Rate limiter for the WhiteBit MCP server.

    This class provides a rate limiter for the WhiteBit MCP server to prevent
    exceeding API quotas.
    """

    def __init__(self):
        """Initialize the rate limiter."""
        self.rules: dict[str, list[RateLimitRule]] = {}

    def add_rule(self, name: str, max_requests: int, period_seconds: float):
        """Add a rate limit rule.

        Args:
            name: Name of the endpoint or group to rate limit
            max_requests: Maximum number of requests allowed in the time period
            period_seconds: Time period in seconds
        """
        if name not in self.rules:
            self.rules[name] = []

        self.rules[name].append(RateLimitRule(max_requests=max_requests, period_seconds=period_seconds))

        logger.debug(f"Added rate limit rule for {name}: {max_requests} requests per {period_seconds} seconds")

    def can_request(self, name: str) -> bool:
        """Check if a request is allowed.

        Args:
            name: Name of the endpoint or group to check

        Returns:
            True if the request is allowed, False otherwise
        """
        if name not in self.rules:
            return True

        return all(rule.can_request() for rule in self.rules[name])

    def add_request(self, name: str):
        """Add a request to the rate limiter.

        Args:
            name: Name of the endpoint or group to add a request to
        """
        if name not in self.rules:
            return

        for rule in self.rules[name]:
            rule.add_request()

    def time_until_available(self, name: str) -> float:
        """Get the time until a request is available.

        Args:
            name: Name of the endpoint or group to check

        Returns:
            Time in seconds until a request is available, or 0 if a request is
            already available
        """
        if name not in self.rules:
            return 0

        return max(rule.time_until_available() for rule in self.rules[name])

    def get_status(self) -> dict[str, dict[str, Any]]:
        """Get the status of all rate limit rules.

        Returns:
            A dictionary mapping endpoint names to rate limit status
        """
        status = {}

        for name, rules in self.rules.items():
            status[name] = {
                "can_request": self.can_request(name),
                "time_until_available": self.time_until_available(name),
                "rules": [],
            }

            for rule in rules:
                status[name]["rules"].append(
                    {
                        "max_requests": rule.max_requests,
                        "period_seconds": rule.period_seconds,
                        "current_requests": len(rule.requests),
                        "can_request": rule.can_request(),
                        "time_until_available": rule.time_until_available(),
                    }
                )

        return status


# Global rate limiter instance
_rate_limiter = RateLimiter()


def get_rate_limiter() -> RateLimiter:
    """Get the global rate limiter instance.

    Returns:
        The global rate limiter instance
    """
    return _rate_limiter


def configure_rate_limiter():
    """Configure the rate limiter with WhiteBit API quotas.

    This function configures the rate limiter with the WhiteBit API quotas.
    See https://whitebit-exchange.github.io/api-docs/private/websocket/#rate-limits
    for more information.
    """
    limiter = get_rate_limiter()

    # Public API rate limits
    # 1000 requests per minute
    limiter.add_rule("public", 1000, 60)

    # Public API endpoint-specific rate limits
    # 10 requests per second
    limiter.add_rule("get_orderbook", 10, 1)
    limiter.add_rule("get_recent_trades", 10, 1)

    # Private API rate limits
    # 100 requests per minute
    limiter.add_rule("private", 100, 60)

    # Private API endpoint-specific rate limits
    # 10 requests per second
    limiter.add_rule("create_limit_order", 10, 1)
    limiter.add_rule("cancel_order", 10, 1)

    logger.info("Rate limiter configured with WhiteBit API quotas")


def rate_limited(name: str):
    """Decorator to apply rate limiting to a function.

    Args:
        name: Name of the endpoint or group to rate limit

    Returns:
        A decorator that applies rate limiting to a function
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            limiter = get_rate_limiter()

            # Check if we can make a request
            if not limiter.can_request(name):
                # Wait until we can make a request
                wait_time = limiter.time_until_available(name)
                logger.warning(f"Rate limit exceeded for {name}, waiting {wait_time:.2f} seconds")
                await asyncio.sleep(wait_time)

            # Add the request to the rate limiter
            limiter.add_request(name)

            # Call the function
            return await func(*args, **kwargs)

        return wrapper

    return decorator
