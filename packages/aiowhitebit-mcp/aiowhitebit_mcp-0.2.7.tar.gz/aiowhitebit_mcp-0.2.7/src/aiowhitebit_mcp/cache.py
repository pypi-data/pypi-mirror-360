"""Caching layer for the WhiteBit MCP server.

This module provides a caching layer for the WhiteBit MCP server to improve
performance and reduce API calls.
"""

import json
import logging
import os
import time
from collections.abc import Callable
from dataclasses import asdict, dataclass, is_dataclass
from functools import wraps
from typing import Any

# Set up logging
logger = logging.getLogger(__name__)


class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles non-serializable objects."""

    def default(self, obj):
        """Handle non-serializable objects."""
        # Handle dataclasses
        if is_dataclass(obj) and not isinstance(obj, type):
            return asdict(obj)

        # Handle objects with __dict__ attribute
        if hasattr(obj, "__dict__") and not isinstance(obj, type):
            return obj.__dict__

        # Handle objects with to_dict or as_dict methods
        if not isinstance(obj, type) and hasattr(obj, "to_dict"):
            return obj.to_dict()
        if not isinstance(obj, type) and hasattr(obj, "as_dict"):
            return obj.as_dict()

        # Handle objects with __str__ method as a last resort
        try:
            return str(obj)
        except Exception as e:
            logger.error(f"Error serializing object: {e}")
            return f"<Non-serializable object of type {type(obj).__name__}>"


def _serialize_for_cache(obj: Any) -> Any:
    """Serialize an object for caching.

    Attempts to convert complex objects to JSON-serializable types.

    Args:
        obj: The object to serialize

    Returns:
        A JSON-serializable representation of the object
    """
    try:
        # Test if object is already JSON serializable
        json.dumps(obj)
        return obj
    except (TypeError, OverflowError):
        # If not, use the custom encoder
        return json.loads(json.dumps(obj, cls=CustomJSONEncoder))


@dataclass
class CacheEntry:
    """Cache entry.

    This class represents a cache entry, which contains the cached value and
    metadata about the entry.

    Attributes:
        value: The cached value
        timestamp: The time when the entry was created
        ttl: The time-to-live for the entry in seconds
    """

    value: Any
    timestamp: float
    ttl: float

    def is_valid(self) -> bool:
        """Check if the cache entry is still valid.

        Returns:
            True if the entry is still valid, False otherwise
        """
        return time.time() - self.timestamp < self.ttl


class Cache:
    """Cache for the WhiteBit MCP server.

    This class provides a cache for the WhiteBit MCP server to improve
    performance and reduce API calls.
    """

    def __init__(self, name: str, persist: bool = False, persist_dir: str | None = None):
        """Initialize the cache.

        Args:
            name: Name of the cache
            persist: Whether to persist the cache to disk
            persist_dir: Directory to persist the cache to
        """
        self.name = name
        self.persist = persist
        self.persist_dir = persist_dir or os.path.join(os.path.expanduser("~"), ".whitebit_mcp", "cache")
        self.entries: dict[str, CacheEntry] = {}

        # Create the persist directory if it doesn't exist
        if self.persist:
            os.makedirs(self.persist_dir, exist_ok=True)

            # Load the cache from disk
            self._load_from_disk()

    def get(self, key: str) -> Any | None:
        """Get a value from the cache.

        Args:
            key: The key to get

        Returns:
            The cached value, or None if the key is not in the cache or the
            entry is no longer valid
        """
        if key not in self.entries:
            return None

        entry = self.entries[key]
        if not entry.is_valid():
            # Remove the entry if it's no longer valid
            del self.entries[key]
            return None

        return entry.value

    def set(self, key: str, value: Any, ttl: float):
        """Set a value in the cache.

        Args:
            key: The key to set
            value: The value to set
            ttl: The time-to-live for the entry in seconds
        """
        # Serialize the value if needed for persistence
        serializable_value = _serialize_for_cache(value) if self.persist else value
        self.entries[key] = CacheEntry(value=serializable_value, timestamp=time.time(), ttl=ttl)

        # Persist the cache to disk
        if self.persist:
            self._persist_to_disk()

    def delete(self, key: str):
        """Delete a value from the cache.

        Args:
            key: The key to delete
        """
        if key in self.entries:
            del self.entries[key]

            # Persist the cache to disk
            if self.persist:
                self._persist_to_disk()

    def clear(self):
        """Clear the cache."""
        self.entries.clear()

        # Persist the cache to disk
        if self.persist:
            self._persist_to_disk()

    def _persist_to_disk(self):
        """Persist the cache to disk."""
        try:
            # Create a dictionary of entries that can be serialized
            entries_dict = {}
            for key, entry in self.entries.items():
                # Only persist valid entries
                if entry.is_valid():
                    entries_dict[key] = {"value": entry.value, "timestamp": entry.timestamp, "ttl": entry.ttl}

            # Write the entries to disk using the custom encoder
            cache_file = os.path.join(self.persist_dir, f"{self.name}.json")
            with open(cache_file, "w") as f:
                json.dump(entries_dict, f, cls=CustomJSONEncoder)
        except Exception as e:
            logger.error(f"Error persisting cache to disk: {e}")

    def _load_from_disk(self):
        """Load the cache from disk."""
        try:
            cache_file = os.path.join(self.persist_dir, f"{self.name}.json")
            if os.path.exists(cache_file):
                try:
                    with open(cache_file) as f:
                        entries_dict = json.load(f)

                    # Create cache entries from the loaded data
                    for key, entry_dict in entries_dict.items():
                        entry = CacheEntry(
                            value=entry_dict["value"], timestamp=entry_dict["timestamp"], ttl=entry_dict["ttl"]
                        )

                        # Only add valid entries
                        if entry.is_valid():
                            self.entries[key] = entry
                except json.JSONDecodeError as json_err:
                    logger.error(f"Invalid JSON in cache file {cache_file}: {json_err}")
                    logger.info(f"Removing corrupted cache file: {cache_file}")
                    # Backup the corrupted file for debugging
                    backup_file = f"{cache_file}.corrupted"
                    try:
                        os.rename(cache_file, backup_file)
                        logger.info(f"Corrupted cache file backed up to {backup_file}")
                    except OSError:
                        # If rename fails, try to delete the file
                        try:
                            os.remove(cache_file)
                            logger.info(f"Corrupted cache file deleted: {cache_file}")
                        except OSError as del_err:
                            logger.error(f"Failed to remove corrupted cache file: {del_err}")
        except Exception as e:
            logger.error(f"Error loading cache from disk: {e}")

    def get_stats(self) -> dict[str, Any]:
        """Get statistics about the cache.

        Returns:
            A dictionary containing statistics about the cache
        """
        valid_entries = 0
        invalid_entries = 0

        for entry in self.entries.values():
            if entry.is_valid():
                valid_entries += 1
            else:
                invalid_entries += 1

        return {
            "name": self.name,
            "valid_entries": valid_entries,
            "invalid_entries": invalid_entries,
            "total_entries": valid_entries + invalid_entries,
            "persist": self.persist,
            "persist_dir": self.persist_dir if self.persist else None,
        }


# Global cache instances
_caches: dict[str, Cache] = {}


def get_cache(name: str, persist: bool = False, persist_dir: str | None = None) -> Cache:
    """Get a cache by name.

    If the cache doesn't exist, it will be created.

    Args:
        name: The name of the cache
        persist: Whether to persist the cache to disk
        persist_dir: Directory to persist the cache to

    Returns:
        The cache
    """
    if name not in _caches:
        _caches[name] = Cache(name=name, persist=persist, persist_dir=persist_dir)

    return _caches[name]


def cached(cache_name: str, ttl: float, key_fn: Callable | None = None, persist: bool = False):
    """Decorator to cache the result of a function.

    Args:
        cache_name: The name of the cache to use
        ttl: The time-to-live for the cache entry in seconds
        key_fn: A function that takes the same arguments as the decorated function
            and returns a string to use as the cache key. If not provided, a key
            will be generated from the function name and arguments.
        persist: Whether to persist the cache to disk

    Returns:
        A decorator that caches the result of a function
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get the cache
            cache = get_cache(cache_name, persist=persist)

            # Generate the cache key
            key = key_fn(*args, **kwargs) if key_fn else f"{func.__name__}:{str(args)}:{str(kwargs)}"

            # Check if the result is in the cache
            result = cache.get(key)
            if result is not None:
                logger.debug(f"Cache hit for {key}")
                return result

            # Call the function
            logger.debug(f"Cache miss for {key}")
            result = await func(*args, **kwargs)

            # Cache the result
            cache.set(key, result, ttl)

            return result

        return wrapper

    return decorator


def get_all_caches() -> dict[str, Cache]:
    """Get all caches.

    Returns:
        A dictionary mapping cache names to caches
    """
    return _caches.copy()


def clear_cache(name: str) -> bool:
    """Clear a cache.

    Args:
        name: The name of the cache to clear

    Returns:
        True if the cache was cleared, False if it doesn't exist
    """
    if name in _caches:
        _caches[name].clear()
        return True

    return False


def clear_all_caches():
    """Clear all caches."""
    for cache in _caches.values():
        cache.clear()
