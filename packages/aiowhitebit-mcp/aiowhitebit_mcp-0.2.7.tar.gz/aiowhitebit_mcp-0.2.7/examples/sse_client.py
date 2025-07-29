"""Example script demonstrating WhiteBit MCP client with SSE transport."""

import asyncio
import os
import traceback

from aiowhitebit_mcp.client import WhiteBitMCPClient


async def check_server():
    """Check if the WhiteBit MCP server is running and accessible."""
    # Try to connect to the MCP server
    server_url = "http://localhost:8000/sse"
    os.environ["WHITEBIT_MCP_URL"] = server_url

    print(f"Connecting to MCP server at {server_url}...")

    try:
        async with WhiteBitMCPClient() as client:
            # Try some WhiteBit API calls
            try:
                # Get server time
                server_time = await client.get_server_time()
                print(f"Server time: {server_time}")

                # Get market info
                markets = await client.get_market_info()
                print(f"Available markets: {len(markets)} markets")

                # Get health and metrics using the underlying client
                health = await client.get_server_status()
                print(f"Server health: {health}")

                server_time = await client.get_server_time()
                print(f"Server metrics: {server_time}")

            except Exception as e:
                print(f"Error calling WhiteBit API: {e}")

    except Exception as e:
        print(f"Failed to connect to MCP server: {e}")
        print("\nDetailed error:")
        traceback.print_exc()
        print("\nMake sure the server is running with the correct transport.")
        print("You can start the server with:")
        print("  - python -m examples.sse_server")
        print("  - Or: aiowhitebit-mcp --transport sse --host localhost --port 8000")


if __name__ == "__main__":
    asyncio.run(check_server())
