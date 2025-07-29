"""Tests for the WhiteBit MCP client."""

import json
import logging

import pytest

from aiowhitebit_mcp.client import WhiteBitMCPClient
from aiowhitebit_mcp.server import MarketPair, create_server

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.fixture
async def server():
    """Create and return a test server instance."""
    server = create_server(name="WhiteBit MCP Test")
    yield server
    await server.close()


@pytest.mark.asyncio
async def test_client_initialization():
    """Test client initialization with URL."""
    server = create_server(name="WhiteBit MCP Test")
    try:
        client = WhiteBitMCPClient(server.mcp)  # type: ignore
        assert client.server_url == server.mcp
    finally:
        await server.close()


@pytest.mark.asyncio
async def test_get_market_info(server):
    """Test get_market_info method."""
    async with WhiteBitMCPClient(server.mcp) as client:
        result = await client.get_market_info()
        data = json.loads(result)

        assert isinstance(data, dict)
        assert "markets" in data
        markets = data["markets"]
        assert isinstance(markets, list)
        assert len(markets) > 0
        first_market = markets[0][0]
        assert isinstance(first_market, dict)
        assert "stock" in first_market
        assert "money" in first_market


@pytest.mark.asyncio
async def test_get_market_activity(server):
    """Test get_market_activity method."""
    async with WhiteBitMCPClient(server.mcp) as client:
        result = await client.get_market_activity()
        data = json.loads(result)

        assert isinstance(data, dict)
        assert "activities" in data
        activities = data["activities"]
        assert isinstance(activities, list)
        assert len(activities) > 0


@pytest.mark.asyncio
async def test_get_server_time(server):
    """Test get_server_time method."""
    async with WhiteBitMCPClient(server.mcp) as client:
        result = await client.get_server_time()
        data = json.loads(result)

        assert isinstance(data, dict)
        assert "time" in data
        assert isinstance(data["time"], dict)
        assert "time" in data["time"]
        assert isinstance(data["time"]["time"], int)


@pytest.mark.asyncio
async def test_get_server_status(server):
    """Test get_server_status method."""
    async with WhiteBitMCPClient(server.mcp) as client:
        result = await client.get_server_status()
        data = json.loads(result)

        assert isinstance(data, dict)
        assert "status" in data


@pytest.mark.asyncio
async def test_get_orderbook(server):
    """Test get_orderbook method."""
    async with WhiteBitMCPClient(server.mcp) as client:
        market = MarketPair(market="BTC_USDT")
        result = await client.get_orderbook(market)
        data = json.loads(result)

        assert isinstance(data, dict)
        assert "orderbook" in data
        orderbook = data["orderbook"]
        assert isinstance(orderbook, dict)
        assert "asks" in orderbook
        assert "bids" in orderbook
        assert isinstance(orderbook["asks"], list)
        assert isinstance(orderbook["bids"], list)


@pytest.mark.asyncio
async def test_get_recent_trades(server):
    """Test get_recent_trades method."""
    async with WhiteBitMCPClient(server.mcp) as client:
        market = MarketPair(market="BTC_USDT")
        result = await client.get_recent_trades(market, trade_type="buy")
        data = json.loads(result)

        assert isinstance(data, dict)
        assert "trades" in data
        trades = data["trades"]
        assert isinstance(trades, list)


@pytest.mark.asyncio
async def test_get_fee(server):
    """Test get_fee method."""
    async with WhiteBitMCPClient(server.mcp) as client:
        result = await client.get_fee("BTC")
        data = json.loads(result)

        assert isinstance(data, dict)


@pytest.mark.asyncio
async def test_get_asset_status_list(server):
    """Test get_asset_status_list method."""
    async with WhiteBitMCPClient(server.mcp) as client:
        result = await client.get_asset_status_list()
        data = json.loads(result)

        assert isinstance(data, dict)
        assert "assets" in data
        assets = data["assets"]
        assert isinstance(assets, list)
        assert len(assets) > 0


@pytest.mark.asyncio
async def test_get_markets_resource(server):
    """Test get_markets_resource method."""
    async with WhiteBitMCPClient(server.mcp) as client:
        result = await client.get_markets_resource()

        data = json.loads(result)
        assert isinstance(data, dict)
        assert "markets" in data
        markets = data["markets"]
        assert isinstance(markets, list)
        assert len(markets) > 0


@pytest.mark.asyncio
async def test_get_market_resource(server):
    """Test get_market_resource method."""
    async with WhiteBitMCPClient(server.mcp) as client:
        # First get all markets to verify server is working
        markets_result = await client.get_markets_resource()
        markets_data = json.loads(markets_result)
        assert "markets" in markets_data

        # Get the first available market from the list
        available_markets = markets_data["markets"][0]
        assert len(available_markets) > 0
        test_market = available_markets[0]["name"]  # Assuming market has a name field

        # Then test with an actual available market
        result = await client.get_market_resource(test_market)
        data = json.loads(result)
        assert isinstance(data, dict)


@pytest.mark.asyncio
async def test_get_assets_resource(server):
    """Test get_assets_resource method."""
    async with WhiteBitMCPClient(server.mcp) as client:
        result = await client.get_assets_resource()

        data = json.loads(result)
        assert isinstance(data, dict)
        assert "assets" in data
