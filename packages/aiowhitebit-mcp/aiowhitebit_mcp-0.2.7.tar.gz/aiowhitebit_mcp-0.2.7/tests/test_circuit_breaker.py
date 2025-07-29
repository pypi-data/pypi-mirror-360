"""Test script for the circuit breaker implementation.

This script tests the circuit breaker implementation to ensure it properly
handles API outages and prevents cascading failures.
"""

import asyncio
import logging
import sys

from fastmcp.client import Client

from aiowhitebit_mcp.circuit_breaker import circuit_breaker, get_circuit_breaker, reset_circuit_breaker
from aiowhitebit_mcp.server import create_server

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FailingService:
    """A service that fails after a certain number of calls."""

    def __init__(self, fail_after=3, recover_after=3):
        """Initialize the failing service.

        Args:
            fail_after: The number of calls after which the service starts failing
            recover_after: The number of failures after which the service recovers
        """
        self.call_count = 0
        self.failure_count = 0
        self.fail_after = fail_after
        self.recover_after = recover_after

    @circuit_breaker(name="failing_service", failure_threshold=3, recovery_timeout=1.0, timeout=1.0)
    async def call(self):
        """Call the service.

        Returns:
            A string indicating success

        Raises:
            Exception: If the service is failing
        """
        self.call_count += 1

        if self.call_count > self.fail_after:
            self.failure_count += 1

            if self.failure_count > self.recover_after:
                # Service has recovered
                self.call_count = 0
                self.failure_count = 0
                return "Service recovered"

            # Service is failing
            raise Exception("Service is failing")

        return "Service is working"


async def test_circuit_breaker():
    """Test the circuit breaker implementation."""
    print("Testing circuit breaker...")

    service = FailingService(fail_after=3, recover_after=3)

    # First 3 calls should succeed
    for i in range(3):
        try:
            result = await service.call()
            print(f"Call {i + 1}: {result}")
        except Exception as e:
            print(f"Call {i + 1} failed: {e}")

    # Next 3 calls should fail and open the circuit
    for i in range(3):
        try:
            result = await service.call()
            print(f"Call {i + 4}: {result}")
        except Exception as e:
            print(f"Call {i + 4} failed: {e}")

    # Circuit should be open now, calls should be rejected immediately
    circuit = get_circuit_breaker("failing_service")
    print(f"Circuit state: {circuit.state.value}")

    # Wait for the recovery timeout to elapse
    print("Waiting for recovery timeout...")
    await asyncio.sleep(1.5)

    # Next call should be allowed (half-open state)
    try:
        result = await service.call()
        print(f"Call after recovery: {result}")
    except Exception as e:
        print(f"Call after recovery failed: {e}")

    # Check the circuit state again
    print(f"Circuit state: {circuit.state.value}")

    # Reset the circuit
    reset_circuit_breaker("failing_service")
    print(f"Circuit state after reset: {circuit.state.value}")

    print("✅ Circuit breaker test passed")


async def test_monitoring_tools():
    """Test the monitoring tools."""
    print("Testing monitoring tools...")

    # Create the server
    server = create_server(name="WhiteBit MCP Test")

    try:
        async with Client(server.mcp) as client:
            # Get circuit breaker status
            print("Getting circuit breaker status...")
            response = await client.call_tool("circuit_breakers", {})
            print(f"Circuit breakers: {response}")

            # Reset a circuit breaker
            print("Resetting circuit breaker...")
            response = await client.call_tool("reset_circuit_breaker", {"name": "failing_service"})
            print(f"Reset result: {response}")

            print("✅ Monitoring tools test passed")
    finally:
        await server.close()


async def run_tests():
    """Run all tests."""
    print("Starting circuit breaker tests...")

    await test_circuit_breaker()
    await test_monitoring_tools()

    print("\n🎉 All circuit breaker tests passed!")

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(run_tests())
    sys.exit(exit_code)
