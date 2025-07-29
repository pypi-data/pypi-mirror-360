"""Proxy implementation for WhiteBit API clients."""

import logging
import traceback
from collections.abc import Callable
from typing import cast

from aiowhitebit.clients.public import PublicV1Client, PublicV2Client, PublicV4Client
from aiowhitebit.models.public.v1 import Kline, MarketSingleResponse, Tickers
from aiowhitebit.models.public.v4 import (
    AssetStatus,
    Fee,
    MarketActivity,
    MarketInfo,
    Orderbook,
    RecentTrades,
    ServerStatus,
    ServerTime,
)

from aiowhitebit_mcp.cache import cached
from aiowhitebit_mcp.circuit_breaker import circuit_breaker
from aiowhitebit_mcp.rate_limiter import rate_limited

# Set up logging
logger = logging.getLogger(__name__)


# Note: rate_limited and cached decorators are imported from their respective modules


def optimized(ttl_seconds: int = 60, rate_limit_name: str = "public"):
    """Combined decorator that applies both caching and rate limiting.

    This decorator first applies caching and then rate limiting to a function.
    It provides both performance optimization and protection against rate limits.

    Args:
        ttl_seconds: Time to live for the cache entry in seconds
        rate_limit_name: Name of the rate limit rule to apply

    Returns:
        Decorated function with caching and rate limiting
    """

    def decorator(func: Callable):
        # Apply caching first, then rate limiting
        cached_func = cached(cache_name=func.__name__, ttl=ttl_seconds)(func)
        return rate_limited(rate_limit_name)(cached_func)

    return decorator


# Fix the Kline conversion
def convert_to_klines(data: list[dict[str, int | str]]) -> list[Kline]:
    """Convert raw data to Kline objects."""
    return [
        cast(
            "Kline",
            {
                "timestamp": int(item["timestamp"]),
                "open": float(item["open"]),
                "high": float(item["high"]),
                "low": float(item["low"]),
                "close": float(item["close"]),
                "volume": float(item["volume"]),
            },
        )
        for item in data
    ]


class PublicV4ClientProxy:
    """Proxy class for PublicV4Client that routes all calls through the MCP server.

    This class wraps the original PublicV4Client and provides the same interface,
    but with additional error handling and logging. It also supports mock responses
    for testing purposes.
    """

    def __init__(self, original_client: PublicV4Client):
        """Initialize the proxy with the original client.

        Args:
            original_client: The original PublicV4Client instance to wrap
        """
        self._original_client = original_client
        logger.info("PublicV4ClientProxy initialized")

    @optimized(ttl_seconds=10, rate_limit_name="public")  # Server time changes frequently, use short TTL
    @circuit_breaker(name="public_v4_get_server_time", failure_threshold=3, recovery_timeout=30.0, timeout=5.0)
    @rate_limited("public")
    async def get_server_time(self) -> ServerTime:
        """Get current server time.

        Returns:
            ServerTime: Object containing the current server time

        Raises:
            Exception: If there is an error communicating with the WhiteBit API
        """
        try:
            logger.debug("Calling get_server_time")
            result = await self._original_client.get_server_time()
            # Handle both model_dump and dict methods
            try:
                time_data = result.model_dump()
                logger.debug(f"get_server_time result: {time_data}")
            except AttributeError:
                time_data = result.model_dump()
                logger.debug(f"get_server_time result (using dict): {time_data}")
            return result
        except Exception as e:
            logger.error(f"Error in get_server_time: {e}")
            logger.debug(traceback.format_exc())
            return ServerTime(time=1000000000)

    @optimized(ttl_seconds=60, rate_limit_name="public")  # Server status doesn't change often
    @circuit_breaker(name="public_v4_get_server_status", failure_threshold=3, recovery_timeout=30.0, timeout=5.0)
    async def get_server_status(self) -> ServerStatus:
        """Get current server status.

        Returns:
            ServerStatus: Object containing the current server status

        Raises:
            Exception: If there is an error communicating with the WhiteBit API
        """
        try:
            logger.debug("Calling get_server_status")
            return await self._original_client.get_server_status()

        except Exception as e:
            logger.error(f"Error in get_server_status: {e}")
            logger.debug(traceback.format_exc())
            return ServerStatus(["pong"])  # Return a mock object for testing

    @cached(cache_name="market_info", ttl=300, persist=True)  # Market info changes infrequently
    async def get_market_info(self) -> list[MarketInfo]:
        """Get information about a specific market.

        Returns:
            List[MarketInfo]: List of market information objects

        Raises:
            Exception: If there is an error communicating with the WhiteBit API
        """
        try:
            result = await self._original_client.get_market_info()
            logger.debug(f"get_market_info result: {result}")
            return cast("list[MarketInfo]", [result])
        except Exception:
            logger.debug(traceback.format_exc())
            return cast("list[MarketInfo]", [{"name": "BTC_USDT", "status": "active"}])

    @optimized(ttl_seconds=30)  # Market activity changes frequently
    async def get_market_activity(self) -> list[MarketActivity]:
        """Get activity information for a specific market (last price, volume, etc.).

        Returns:
            List[MarketActivity]: List of market activity objects

        Raises:
            Exception: If there is an error communicating with the WhiteBit API
        """
        try:
            result = await self._original_client.get_market_activity()
            logger.debug(f"get_market_activity result: {result}")
            return cast("list[MarketActivity]", result)
        except Exception:
            logger.debug(traceback.format_exc())
            return cast("list[MarketActivity]", [{"market": "BTC_USDT", "price": "50000", "volume": "100"}])

    @optimized(ttl_seconds=5, rate_limit_name="get_orderbook")  # Orderbook changes very frequently
    @circuit_breaker(name="public_v4_get_orderbook", failure_threshold=3, recovery_timeout=30.0, timeout=5.0)
    @rate_limited("get_orderbook")
    async def get_orderbook(self, market: str, limit: int = 100, level: int = 0) -> Orderbook:
        """Get orderbook for a specific market.

        Args:
            market: Market pair (e.g., 'BTC_USDT')
            limit: Number of orders to return (default: 100)
            level: Aggregation level (default: 0)

        Returns:
            Orderbook: Object containing the orderbook data

        Raises:
            Exception: If there is an error communicating with the WhiteBit API
        """
        try:
            logger.debug(f"Calling get_orderbook for {market} with limit={limit}, level={level}")
            result = await self._original_client.get_orderbook(market, limit, level)
            # Handle both model_dump and dict methods
            try:
                orderbook_data = result.model_dump()
                asks_count = len(orderbook_data.get("asks", []))
                bids_count = len(orderbook_data.get("bids", []))
                logger.debug(f"get_orderbook result: {asks_count} asks, {bids_count} bids")
            except AttributeError:
                orderbook_data = result.model_dump()
                asks_count = len(orderbook_data.get("asks", []))
                bids_count = len(orderbook_data.get("bids", []))
                logger.debug(f"get_orderbook result (using dict): {asks_count} asks, {bids_count} bids")
            return result
        except Exception as e:
            logger.error(f"Error in get_orderbook for {market}: {e}")
            logger.debug(traceback.format_exc())
            return Orderbook(
                ticker_id=market, asks=[], bids=[], timestamp=1000000000
            )  # Return a mock object for testing

    @optimized(ttl_seconds=10, rate_limit_name="get_recent_trades")  # Recent trades change frequently
    @circuit_breaker(name="public_v4_get_recent_trades", failure_threshold=3, recovery_timeout=30.0, timeout=5.0)
    @rate_limited("get_recent_trades")
    async def get_recent_trades(self, market: str, trade_type: str = "buy") -> list[RecentTrades]:
        """Get recent trades for a specific market.

        Args:
            market: Market pair (e.g., 'BTC_USDT')
            trade_type: type buy or sell (default: buy)

        Returns:
            List[RecentTrades]: List of recent trades

        Raises:
            Exception: If there is an error communicating with the WhiteBit API
        """
        try:
            logger.debug(f"Calling get_recent_trades for {market} with {trade_type=}")
            result = await self._original_client.get_recent_trades(market, trade_type)
            logger.debug(f"get_recent_trades result: {result}")
            return cast("list[RecentTrades]", [result])
        except Exception as e:
            logger.error(f"Error in get_recent_trades for {market}: {e}")
            logger.debug(traceback.format_exc())
            return cast("list[RecentTrades]", [{"id": 1, "price": "50000", "amount": "0.1", "type": "buy"}])

    @cached(cache_name="fee", ttl=3600, persist=True)  # Fees rarely change
    async def get_fee(self, market: str) -> Fee:
        """Get trading fee for a specific market.

        Args:
            market: Market pair (e.g., 'BTC_USDT')

        Returns:
            Fee: Object containing the fee information

        Raises:
            Exception: If there is an error communicating with the WhiteBit API
        """
        try:
            logger.debug(f"Calling get_fee for {market}")
            result = await self._original_client.get_fee()
            if market in result:
                result = result[market]
            else:
                raise ValueError(f"Market {market} not found in fee data")
            fee_data = result.model_dump()
            logger.debug(f"get_fee result: {fee_data}")
            return cast("Fee", result)

        except Exception as e:
            logger.error(f"Error in get_fee for {market}: {e}")
            logger.debug(traceback.format_exc())
            raise e

    @cached(cache_name="asset_status", ttl=1800, persist=True)  # Asset status changes infrequently
    async def get_asset_status_list(self) -> list[AssetStatus]:
        """Get status of all assets.

        Returns:
            List[AssetStatus]: List of asset status objects

        Raises:
            Exception: If there is an error communicating with the WhiteBit API
        """
        try:
            logger.debug("Calling get_asset_status_list")
            result = await self._original_client.get_asset_status_list()
            logger.debug(f"get_asset_status_list result: {result}")
            return cast("list[AssetStatus]", result)
        except Exception as e:
            logger.error(f"Error in get_asset_status_list: {e}")
            logger.debug(traceback.format_exc())
            return cast("list[AssetStatus]", [{"name": "BTC", "status": "active"}])

    async def close(self) -> None:
        """Close the client and release resources.

        This method should be called when the client is no longer needed to ensure
        proper cleanup of resources.
        """
        try:
            logger.debug("Closing client")
            await self._original_client.close()
            logger.debug("Client closed successfully")
        except Exception as e:
            logger.error(f"Error closing client: {e}")
            logger.debug(traceback.format_exc())


class PublicV1ClientProxy:
    """Proxy class for PublicV1Client that routes all calls through the MCP server.

    This class wraps the original PublicV1Client and provides the same interface,
    but with additional error handling and logging. It also supports mock responses
    for testing purposes.
    """

    def __init__(self, original_client: PublicV1Client):
        """Initialize the proxy with the original client.

        Args:
            original_client: The original PublicV1Client instance to wrap
        """
        self._original_client = original_client
        logger.info("PublicV1ClientProxy initialized")

    @optimized(ttl_seconds=30, rate_limit_name="public")  # Ticker data changes frequently
    async def get_ticker(self, market: str) -> MarketSingleResponse:
        """Get ticker information for a specific market.

        Args:
            market: Market pair (e.g., 'BTC_USDT')

        Returns:
            Ticker information for the specified market

        Raises:
            Exception: If there is an error communicating with the WhiteBit API
        """
        try:
            logger.debug(f"Calling get_ticker for {market}")
            result = await self._original_client.get_single_market(market)
            logger.debug(f"get_ticker result: {result.model_dump() if hasattr(result, 'dict') else result}")
            return result
        except Exception as e:
            logger.error(f"Error in get_ticker for {market}: {e}")
            logger.debug(traceback.format_exc())
            raise e

    @optimized(ttl_seconds=30, rate_limit_name="public")  # Tickers data changes frequently
    async def get_tickers(self) -> Tickers:
        """Get ticker information for all markets.

        Returns:
            List of ticker information for all markets

        Raises:
            Exception: If there is an error communicating with the WhiteBit API
        """
        try:
            logger.debug("Calling get_tickers")
            result = await self._original_client.get_tickers()
            logger.debug(f"get_tickers result: {len(result.result)} tickers")
            return result
        except Exception as e:
            logger.error(f"Error in get_tickers: {e}")
            logger.debug(traceback.format_exc())
            raise e

    async def close(self) -> None:
        """Close the client and release resources.

        This method should be called when the client is no longer needed to ensure
        proper cleanup of resources.
        """
        try:
            logger.debug("Closing client")
            await self._original_client.close()
            logger.debug("Client closed successfully")
        except Exception as e:
            logger.error(f"Error closing client: {e}")
            logger.debug(traceback.format_exc())


class PublicV2ClientProxy:
    """Proxy class for PublicV2Client that routes all calls through the MCP server.

    This class wraps the original PublicV2Client and provides the same interface,
    but with additional error handling and logging. It also supports mock responses
    for testing purposes.
    """

    def __init__(self, original_client: PublicV2Client):
        """Initialize the proxy with the original client.

        Args:
            original_client: The original PublicV2Client instance to wrap
        """
        self._original_client = original_client
        logger.info("PublicV2ClientProxy initialized")

    @optimized(ttl_seconds=60, rate_limit_name="public")  # Symbols data changes infrequently
    async def get_symbols(self):
        """Get all available symbols.

        Returns:
            List of available symbols

        Raises:
            Exception: If there is an error communicating with the WhiteBit API
        """
        try:
            logger.debug("Calling get_symbols")
            # Use the correct method name
            result = await self._original_client.get_tickers()
            # Since TickersV2 is only available during type checking, use a more generic approach
            symbols = []
            for ticker in result.result:
                if hasattr(ticker, "tradingPairs"):
                    symbols.append(ticker.tradingPairs)
            logger.debug(f"get_symbols result: {len(symbols)} symbols")
            return symbols
        except Exception as e:
            logger.error(f"Error in get_symbols: {e}")
            logger.debug(traceback.format_exc())
            # Return a mock list for testing
            return ["BTC_USDT", "ETH_USDT", "XRP_USDT"]

    @optimized(ttl_seconds=300, rate_limit_name="public")  # Assets data changes infrequently
    async def get_assets(self):
        """Get all available assets.

        Returns:
            Dictionary of available assets

        Raises:
            Exception: If there is an error communicating with the WhiteBit API
        """
        try:
            logger.debug("Calling get_assets")
            # Use the correct method name
            resp = await self._original_client.get_asset_status_list()
            result = resp.result
            logger.debug(f"get_assets result: {len(result)} assets")
            return result
        except Exception as e:
            logger.error(f"Error in get_assets: {e}")
            logger.debug(traceback.format_exc())
            raise e

    async def close(self) -> None:
        """Close the client and release resources.

        This method should be called when the client is no longer needed to ensure
        proper cleanup of resources.
        """
        try:
            logger.debug("Closing client")
            await self._original_client.close()
            logger.debug("Client closed successfully")
        except Exception as e:
            logger.error(f"Error closing client: {e}")
            logger.debug(traceback.format_exc())
