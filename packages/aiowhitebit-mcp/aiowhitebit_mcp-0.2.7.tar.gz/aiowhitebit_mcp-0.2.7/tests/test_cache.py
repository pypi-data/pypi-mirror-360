"""Test script for the caching implementation.

This script tests the caching implementation to ensure it properly
caches data and improves performance.
"""

import asyncio
import logging
import sys
import time
from typing import Any

from aiowhitebit_mcp.cache import cached, clear_cache, get_all_caches, get_cache

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SlowService:
    """A service that is slow to respond."""

    def __init__(self, delay=0.5):
        """Initialize the slow service.

        Args:
            delay: The delay in seconds to simulate a slow response
        """
        self.delay = delay
        self.call_count = 0

    @cached(cache_name="slow_service", ttl=10)
    async def get_data(self, key: str) -> dict[str, Any]:
        """Get data from the slow service.

        Args:
            key: The key to get data for

        Returns:
            A dictionary containing the data
        """
        self.call_count += 1
        await asyncio.sleep(self.delay)
        return {"key": key, "value": f"Value for {key}", "timestamp": time.time(), "call_count": self.call_count}


async def test_cache():
    """Test the caching implementation."""
    print("Testing cache...")

    # Clear all caches
    for name in get_all_caches():
        clear_cache(name)

    service = SlowService(delay=0.5)

    # First call should be slow and not cached
    start_time = time.time()
    result1 = await service.get_data("test")
    duration1 = time.time() - start_time
    print(f"First call: {duration1:.2f} seconds, call_count: {result1['call_count']}")

    # Second call should be fast and cached
    start_time = time.time()
    result2 = await service.get_data("test")
    duration2 = time.time() - start_time
    print(f"Second call: {duration2:.2f} seconds, call_count: {result2['call_count']}")

    # Verify that the second call was faster
    assert duration2 < duration1, f"Second call ({duration2:.2f}s) should be faster than first call ({duration1:.2f}s)"

    # Verify that the call count is the same (cached result)
    assert result1["call_count"] == result2["call_count"], (
        f"Call count should be the same: {result1['call_count']} != {result2['call_count']}"
    )

    # Different key should not be cached
    start_time = time.time()
    result3 = await service.get_data("test2")
    duration3 = time.time() - start_time
    print(f"Different key: {duration3:.2f} seconds, call_count: {result3['call_count']}")

    # Verify that the different key call was slow
    assert duration3 > duration2, (
        f"Different key call ({duration3:.2f}s) should be slower than cached call ({duration2:.2f}s)"
    )

    # Verify that the call count increased
    assert result3["call_count"] > result2["call_count"], (
        f"Call count should increase: {result3['call_count']} <= {result2['call_count']}"
    )

    # Clear the cache
    clear_cache("slow_service")

    # After clearing the cache, the call should be slow again
    start_time = time.time()
    result4 = await service.get_data("test")
    duration4 = time.time() - start_time
    print(f"After clearing cache: {duration4:.2f} seconds, call_count: {result4['call_count']}")

    # Verify that the call after clearing the cache was slow
    assert duration4 > duration2, (
        f"Call after clearing cache ({duration4:.2f}s) should be slower than cached call ({duration2:.2f}s)"
    )

    # Verify that the call count increased
    assert result4["call_count"] > result2["call_count"], (
        f"Call count should increase: {result4['call_count']} <= {result2['call_count']}"
    )

    print("✅ Cache test passed")


async def test_cache_persistence():
    """Test cache persistence."""
    print("Testing cache persistence...")

    # Clear all caches
    for name in get_all_caches():
        clear_cache(name)

    # Create a persistent cache
    cache = get_cache("persistent_cache", persist=True)

    # Set a value in the cache
    cache.set("test", "test_value", ttl=60)

    # Verify that the value is in the cache
    value = cache.get("test")
    assert value == "test_value", f"Value should be 'test_value', got {value}"

    # Create a new cache with the same name
    cache2 = get_cache("persistent_cache", persist=True)

    # Verify that the value is still in the cache
    value = cache2.get("test")
    assert value == "test_value", f"Value should be 'test_value', got {value}"

    print("✅ Cache persistence test passed")


async def run_tests():
    """Run all tests."""
    print("Starting cache tests...")

    await test_cache()
    await test_cache_persistence()

    print("\n🎉 All cache tests passed!")

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(run_tests())
    sys.exit(exit_code)
