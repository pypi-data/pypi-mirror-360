"""Example script to run the WhiteBit MCP server with SSE transport."""

import asyncio

from aiowhitebit_mcp.server import create_server

# Create the server
server = create_server(name="WhiteBit API Server")

# Run the server with SSE transport
if __name__ == "__main__":
    asyncio.run(server.run(transport="sse", host="127.0.0.1", port=8000))
