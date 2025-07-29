"""Type definitions for the aiowhitebit-mcp package."""

from typing import Literal, Protocol

TransportType = Literal["stdio", "sse", "http"]


class WhiteBitMCPProtocol(Protocol):
    """Protocol defining the WhiteBitMCP interface."""

    async def run(
        self,
        transport: TransportType = "stdio",
        host: str | None = None,
        port: int | None = None,
    ) -> None:
        """Run the MCP server.

        Args:
            transport: Transport type to use
            host: Host to bind to (for network transports)
            port: Port to bind to (for network transports)
        """
        ...
