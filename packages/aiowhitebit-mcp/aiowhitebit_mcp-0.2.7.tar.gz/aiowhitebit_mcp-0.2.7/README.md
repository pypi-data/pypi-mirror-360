# aiowhitebit-mcp

Message Control Protocol (MCP) server and client implementation for WhiteBit cryptocurrency exchange API. Built on
top of [aiowhitebit](https://github.com/doubledare704/aiowhitebit) library and [fastmcp](https://github.com/jlowin/fastmcp).

## Features

- MCP server for WhiteBit API with public endpoints
- Support for multiple transport protocols (stdio, SSE, WebSocket)
- Easy-to-use client for interacting with the MCP server
- Command-line interface for running the server
- Integration with Claude Desktop
- Real-time market data via WebSocket
- Comprehensive test coverage and type checking
- Modern development tools (ruff, pyright, pre-commit)
- Caching with disk persistence
- Rate limiting and circuit breaker patterns

## Quick Start

```bash
# Install the package
pip install aiowhitebit-mcp

# Run the server (stdio transport for Claude Desktop)
aiowhitebit-mcp --transport stdio

# Or run with SSE transport
aiowhitebit-mcp --transport sse --host 127.0.0.1 --port 8000
```

## Basic Usage

### Client with Network Transport

```python
import asyncio
import os
from aiowhitebit_mcp.client import WhiteBitMCPClient

async def main():
    # Set the server URL (or use environment variable)
    server_url = "http://localhost:8000/sse"
    os.environ["WHITEBIT_MCP_URL"] = server_url

    async with WhiteBitMCPClient() as client:
        # Get market info
        btc_usdt = await client.get_market_resource("BTC_USDT")
        print("BTC/USDT Market Info:", btc_usdt)

        # Get real-time price via WebSocket
        price = await client.get_last_price("BTC_USDT")
        print("Current BTC/USDT price:", price)

        # Get order book
        orderbook = await client.get_orderbook("BTC_USDT")
        print("Order book:", orderbook)

if __name__ == "__main__":
    asyncio.run(main())
```

## Server Configuration

```python
from aiowhitebit_mcp.server import create_server
import asyncio

# Create the server with custom configuration
server = create_server(
    name="WhiteBit API"
)

# Run the server with desired transport
if __name__ == "__main__":
    asyncio.run(
        server.run(
            transport="stdio",  # or "sse"
            host="127.0.0.1",   # for network transports
            port=8000           # for network transports
        )
    )
```

## Available Tools

### Public API
- `get_server_time()`: Get current server time
- `get_market_info()`: Get all markets information
- `get_orderbook(market: str)`: Get order book
- `get_recent_trades(market: str, limit: int = 100)`: Get recent trades
- `get_ticker(market: str)`: Get ticker information
- `get_fee(market: str)`: Get trading fees
- `get_server_status()`: Get server status
- `get_asset_status_list()`: Get status of all assets

### WebSocket API
- `get_last_price(market: str)`: Get real-time price
- `get_market_depth(market: str)`: Get real-time order book

### Resources
- `whitebit://markets`: Get all markets information
- `whitebit://markets/{market}`: Get specific market information
- `whitebit://assets`: Get all assets information
- `whitebit://assets/{asset}`: Get specific asset information

## Command-line Interface

```bash
# Show help
aiowhitebit-mcp --help

# Run with stdio transport (for Claude Desktop)
aiowhitebit-mcp --transport stdio

# Run with SSE transport
aiowhitebit-mcp --transport sse --host localhost --port 8000
```

## Development

```bash
# Clone the repository
git clone https://github.com/yourusername/aiowhitebit-mcp.git
cd aiowhitebit-mcp

# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run tests
pytest

# Run type checking
pyright src/aiowhitebit_mcp

# Run linting
ruff check .
```

## Examples

Check the `examples/` directory for more usage examples:

- `claude_desktop_server.py`: Run the server with stdio transport for Claude Desktop
- `claude_desktop_client.py`: Client for connecting to a stdio server
- `sse_server.py`: Run the server with SSE transport
- `sse_client.py`: Client for connecting to an SSE server

## License

Apache License 2.0
