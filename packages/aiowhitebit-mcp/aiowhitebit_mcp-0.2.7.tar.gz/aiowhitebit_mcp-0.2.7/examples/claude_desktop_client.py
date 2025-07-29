"""Example script demonstrating WhiteBit MCP client with stdio transport."""

import asyncio

from aiowhitebit_mcp.client import WhiteBitMCPClient

server_script = "claude_desktop_server.py"  # Assumes this file exists and runs mcp.run()


async def use_mcp_client(whitebit_client):
    """Use the WhiteBit MCP client to interact with the server."""
    async with whitebit_client:
        tools = await whitebit_client.client.list_tools()
        print(f"Connected via Python Stdio, found tools: {tools}")
        server_time = await whitebit_client.get_server_time()
        print(f"Server time: {server_time}")
        server_status = await whitebit_client.get_server_status()
        print(f"Server status: {server_status}")
        assets = await whitebit_client.get_asset_status_list()
        print(f"Asset status: {assets}")
        markets = await whitebit_client.get_markets_resource()
        print(f"Markets: {markets}")
        btc_usdt = await whitebit_client.get_market_resource("BTC_USDT")
        print(f"BTC/USDT Market Info: {btc_usdt}")


if __name__ == "__main__":
    extended_client = WhiteBitMCPClient(server_script)
    asyncio.run(use_mcp_client(extended_client))
