"""Integration tests for the WhiteBit MCP server.

This module contains integration tests for the WhiteBit MCP server.
It tests all the public API methods exposed by the server.
"""

import json
import logging
from typing import TYPE_CHECKING

from fastmcp.client import Client

from aiowhitebit_mcp.server import MarketPair, create_server

if TYPE_CHECKING:
    from mcp.types import CallToolResult

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_get_ticker():
    """Test the get_ticker endpoint returns valid ticker data."""
    server = create_server(name="WhiteBit MCP Test")
    async with Client(server.mcp) as client:
        response = await client.call_tool("get_ticker", {"market": MarketPair(market="BTC_USDT")})
        content = response.content[0]
        assert hasattr(content, "text")

        data = json.loads(content.text)
        assert isinstance(data, dict)
        assert "ticker" in data
        ticker = data["ticker"]["result"]
        assert isinstance(ticker, dict)
        assert "last" in ticker
        assert "high" in ticker
        assert "low" in ticker
        assert "volume" in ticker
        print("✅ get_ticker test passed")

    await server.close()


async def test_get_tickers():
    """Test the get_tickers endpoint returns data for multiple markets."""
    server = create_server(name="WhiteBit MCP Test")
    async with Client(server.mcp) as client:
        print("Testing get_tickers...")
        response = await client.call_tool("get_tickers", {})
        content = response.content[0]
        assert hasattr(content, "text")

        data = json.loads(content.text)
        assert isinstance(data, dict)
        assert "tickers" in data
        tickers = data["tickers"]["result"]
        assert isinstance(tickers, list)
        assert len(tickers) > 0
        first_ticker = tickers[0]
        assert isinstance(first_ticker, dict)
        assert "name" in first_ticker
        assert "last" in first_ticker
        print("✅ get_tickers test passed")
    await server.close()


# Test cases for public v2 API
async def test_get_symbols():
    """Test the get_symbols endpoint returns a list of available trading pairs."""
    server = create_server(name="WhiteBit MCP Test")
    async with Client(server.mcp) as client:
        print("Testing get_symbols...")
        response = await client.call_tool("get_symbols", {})
        content = response.content[0]
        assert hasattr(content, "text")

        data = json.loads(content.text)
        assert isinstance(data, dict)
        assert "symbols" in data
        symbols = data["symbols"]
        assert isinstance(symbols, list)
        assert len(symbols) > 0
        print("✅ get_symbols test passed")
    await server.close()


async def test_get_assets():
    """Test the get_assets endpoint returns information about available assets."""
    server = create_server(name="WhiteBit MCP Test")
    async with Client(server.mcp) as client:
        print("Testing get_assets...")
        response = await client.call_tool("get_assets", {})
        content = response.content[0]
        assert hasattr(content, "text")

        data = json.loads(content.text)
        assert isinstance(data, dict)
        assert "assets" in data
        assets = data["assets"]
        assert isinstance(assets, list)
        assert len(assets) > 0
        for a in assets:
            assert isinstance(a, dict)
            assert "asset_name" in a
            if a["asset_name"] == "BTC":
                assert "Bitcoin" in a["name"]
                break
        print("✅ get_assets test passed")
    await server.close()


# Test cases for public v4 API
async def test_server_time():
    """Test the server time endpoint returns the current server time."""
    server = create_server(name="WhiteBit MCP Test")
    async with Client(server.mcp) as client:
        response = await client.call_tool("get_server_time", {})
        content = response.content[0]
        assert hasattr(content, "text")

        data = json.loads(content.text)
        assert isinstance(data, dict)
        assert "time" in data
        assert isinstance(data["time"], dict)
        assert "time" in data["time"]
        assert isinstance(data["time"]["time"], int)
        print("✅ get_server_time test passed")

    await server.close()


async def test_server_status():
    """Test the server status endpoint returns the current server status."""
    server = create_server(name="WhiteBit MCP Test")
    async with Client(server.mcp) as client:
        print("Testing get_server_status...")
        response = await client.call_tool("get_server_status", {})
        content = response.content[0]
        assert hasattr(content, "text")

        data = json.loads(content.text)
        assert isinstance(data, dict)
        assert "status" in data
        print("✅ get_server_status test passed")
    await server.close()


async def test_market_info():
    """Test the market info endpoint returns information about available markets."""
    server = create_server(name="WhiteBit MCP Test")
    async with Client(server.mcp) as client:
        print("Testing get_market_info...")
        response: CallToolResult = await client.call_tool("get_market_info", {})

        content = response.content[0]
        assert hasattr(content, "text")

        data = json.loads(content.text)
        assert isinstance(data, dict)
        assert "markets" in data
        markets = data["markets"]
        assert isinstance(markets, list)
        assert len(markets) > 0
        first_market = markets[0][0]
        assert isinstance(first_market, dict)
        assert "stock" in first_market
        assert "money" in first_market
        print("✅ get_market_info test passed")

    await server.close()


async def test_market_activity():
    """Test the market activity endpoint returns current market activities."""
    server = create_server(name="WhiteBit MCP Test")
    async with Client(server.mcp) as client:
        print("Testing get_market_activity...")
        response = await client.call_tool("get_market_activity", {})
        content = response.content[0]
        assert hasattr(content, "text")

        data = json.loads(content.text)
        assert isinstance(data, dict)
        assert "activities" in data
        activities = data["activities"]
        assert isinstance(activities, list)
        assert len(activities) > 0
        first_activity = activities[0]
        assert isinstance(first_activity, str)
        assert isinstance(activities, list)
        print("✅ get_market_activity test passed")
    await server.close()


async def test_orderbook():
    """Test the orderbook endpoint returns current order book data."""
    server = create_server(name="WhiteBit MCP Test")
    async with Client(server.mcp) as client:
        print("Testing get_orderbook...")
        response = await client.call_tool("get_orderbook", {"market": MarketPair(market="BTC_USDT")})
        content = response.content[0]
        assert hasattr(content, "text")

        data = json.loads(content.text)
        assert isinstance(data, dict)
        assert "orderbook" in data
        orderbook = data["orderbook"]
        assert isinstance(orderbook, dict)
        assert "asks" in orderbook
        assert "bids" in orderbook
        print("✅ get_orderbook test passed")
    await server.close()


async def test_recent_trades():
    """Test the recent trades endpoint returns latest trades."""
    server = create_server(name="WhiteBit MCP Test")
    async with Client(server.mcp) as client:
        print("Testing get_recent_trades...")
        response = await client.call_tool("get_recent_trades", {"market": MarketPair(market="BTC_USDT")})
        content = response.content[0]
        assert hasattr(content, "text")

        data = json.loads(content.text)
        assert isinstance(data, dict)
        assert "trades" in data
        trades = data["trades"]
        assert isinstance(trades, list)
        assert len(trades) > 0
        print("✅ get_recent_trades test passed")
    await server.close()


async def test_fee():
    """Test the fee endpoint returns trading fee information."""
    server = create_server(name="WhiteBit MCP Test")
    async with Client(server.mcp) as client:
        print("Testing get_fee...")
        response = await client.call_tool("get_fee", {"market": MarketPair(market="BTC")})
        content = response.content[0]
        assert hasattr(content, "text")

        data = json.loads(content.text)
        assert isinstance(data, dict)
        print("✅ get_fee test passed")

    await server.close()


async def test_asset_status_list():
    """Test the asset status list endpoint returns status of all assets."""
    server = create_server(name="WhiteBit MCP Test")
    async with Client(server.mcp) as client:
        print("Testing get_asset_status_list...")
        response = await client.call_tool("get_asset_status_list", {})
        content = response.content[0]
        assert hasattr(content, "text")

        data = json.loads(content.text)
        assert isinstance(data, dict)
        assert "assets" in data
        assets = data["assets"]
        assert isinstance(assets, list)
        assert len(assets) > 0
        print("✅ get_asset_status_list test passed")
    await server.close()
