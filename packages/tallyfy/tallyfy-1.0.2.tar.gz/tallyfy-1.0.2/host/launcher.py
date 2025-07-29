"""Launcher for MCP host"""

import asyncio
import logging
from websocket.server import MCPWebSocketServer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MCPHost:

    def __init__(self, ws_host="localhost", ws_port=9001):
        self.ws_host = ws_host
        self.ws_port = ws_port

        # Create WebSocket server instance
        self.websocket_server = MCPWebSocketServer(host=ws_host, port=ws_port)

        logger.info("Integrated MCP Host initialized")

    async def start_websocket_server(self):
        """Start the WebSocket server."""
        try:
            # logger.info(f"Starting WebSocket server on {self.ws_host}:{self.ws_port}")
            await self.websocket_server.start_server()
        except Exception as e:
            logger.error(f"WebSocket server error: {e}")
            raise


async def start_mcp_host():
    """Start MCP host"""
    server = MCPHost()
    try:
        await server.start_websocket_server()
    except KeyboardInterrupt:
        logger.info("Servers stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")


if __name__ == "__main__":
    asyncio.run(start_mcp_host())
