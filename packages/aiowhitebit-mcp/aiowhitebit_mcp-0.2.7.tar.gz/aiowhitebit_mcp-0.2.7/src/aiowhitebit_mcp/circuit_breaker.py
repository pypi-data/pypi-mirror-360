"""Circuit breaker pattern implementation for the WhiteBit MCP server.

This module provides a circuit breaker implementation to handle API outages
and prevent cascading failures.
"""

import asyncio
import logging
import time
from enum import Enum
from functools import wraps
from typing import Any

# Set up logging
logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation, requests are allowed
    OPEN = "open"  # Circuit is open, requests are not allowed
    HALF_OPEN = "half-open"  # Testing if the service is back online


class CircuitBreaker:
    """Circuit breaker implementation.

    This class implements the circuit breaker pattern to handle API outages
    and prevent cascading failures.
    """

    def __init__(self, name: str, failure_threshold: int = 5, recovery_timeout: float = 60.0, timeout: float = 10.0):
        """Initialize the circuit breaker.

        Args:
            name: The name of the circuit breaker
            failure_threshold: The number of failures before opening the circuit
            recovery_timeout: The time in seconds to wait before trying to recover
            timeout: The timeout in seconds for requests
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.timeout = timeout

        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0
        self.last_success_time = 0

    def record_success(self):
        """Record a successful request."""
        self.failure_count = 0
        self.last_success_time = time.time()

        if self.state == CircuitState.HALF_OPEN:
            logger.info(f"Circuit {self.name} is closing")
            self.state = CircuitState.CLOSED

    def record_failure(self):
        """Record a failed request."""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.state == CircuitState.CLOSED and self.failure_count >= self.failure_threshold:
            logger.warning(f"Circuit {self.name} is opening due to {self.failure_count} failures")
            self.state = CircuitState.OPEN

    def allow_request(self) -> bool:
        """Check if a request is allowed.

        Returns:
            True if the request is allowed, False otherwise
        """
        if self.state == CircuitState.CLOSED:
            return True

        if self.state == CircuitState.OPEN:
            # Check if the recovery timeout has elapsed
            if time.time() - self.last_failure_time > self.recovery_timeout:
                logger.info(f"Circuit {self.name} is half-opening")
                self.state = CircuitState.HALF_OPEN
                return True
            return False

        # Half-open state
        return True

    def get_state(self) -> dict[str, Any]:
        """Get the current state of the circuit breaker.

        Returns:
            A dictionary containing the current state of the circuit breaker
        """
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "last_failure_time": self.last_failure_time,
            "last_success_time": self.last_success_time,
            "failure_threshold": self.failure_threshold,
            "recovery_timeout": self.recovery_timeout,
            "timeout": self.timeout,
        }


# Global circuit breakers
_circuit_breakers: dict[str, CircuitBreaker] = {}


def get_circuit_breaker(
    name: str, failure_threshold: int = 5, recovery_timeout: float = 60.0, timeout: float = 10.0
) -> CircuitBreaker:
    """Get a circuit breaker by name.

    If the circuit breaker doesn't exist, it will be created.

    Args:
        name: The name of the circuit breaker
        failure_threshold: The number of failures before opening the circuit
        recovery_timeout: The time in seconds to wait before trying to recover
        timeout: The timeout in seconds for requests

    Returns:
        The circuit breaker
    """
    if name not in _circuit_breakers:
        _circuit_breakers[name] = CircuitBreaker(
            name=name, failure_threshold=failure_threshold, recovery_timeout=recovery_timeout, timeout=timeout
        )

    return _circuit_breakers[name]


def circuit_breaker(name: str, failure_threshold: int = 5, recovery_timeout: float = 60.0, timeout: float = 10.0):
    """Decorator to apply a circuit breaker to a function.

    Args:
        name: The name of the circuit breaker
        failure_threshold: The number of failures before opening the circuit
        recovery_timeout: The time in seconds to wait before trying to recover
        timeout: The timeout in seconds for requests

    Returns:
        A decorator that applies a circuit breaker to a function
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            circuit = get_circuit_breaker(
                name=name, failure_threshold=failure_threshold, recovery_timeout=recovery_timeout, timeout=timeout
            )

            if not circuit.allow_request():
                logger.warning(f"Circuit {name} is open, request rejected")
                raise Exception(f"Circuit {name} is open")

            try:
                # Set a timeout for the request
                result = await asyncio.wait_for(func(*args, **kwargs), timeout=timeout)
                circuit.record_success()
                return result
            except asyncio.TimeoutError as err:
                logger.error(f"Request to {name} timed out after {timeout} seconds")
                circuit.record_failure()
                raise Exception(f"Request to {name} timed out") from err
            except Exception as e:
                logger.error(f"Request to {name} failed: {e}")
                circuit.record_failure()
                raise

        return wrapper

    return decorator


def get_all_circuit_breakers() -> dict[str, CircuitBreaker]:
    """Get all circuit breakers.

    Returns:
        A dictionary mapping circuit breaker names to circuit breakers
    """
    return _circuit_breakers.copy()


def reset_circuit_breaker(name: str) -> bool:
    """Reset a circuit breaker.

    Args:
        name: The name of the circuit breaker

    Returns:
        True if the circuit breaker was reset, False if it doesn't exist
    """
    if name in _circuit_breakers:
        circuit = _circuit_breakers[name]
        circuit.state = CircuitState.CLOSED
        circuit.failure_count = 0
        logger.info(f"Circuit {name} has been reset")
        return True

    return False
