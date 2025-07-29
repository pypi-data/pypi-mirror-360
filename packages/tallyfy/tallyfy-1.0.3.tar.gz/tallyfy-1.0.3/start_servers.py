#!/usr/bin/env python3
"""Integrated launcher for both WebSocket and Admin servers."""

import uvicorn
import asyncio
import logging
import threading
from admin.server import MCPAdminServer
from websocket.server import MCPWebSocketServer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class IntegratedMCPServer:
    """Integrated server that runs both WebSocket and Admin servers."""

    def __init__(self, ws_host="localhost", ws_port=9001, admin_host="0.0.0.0", admin_port=8766):
        self.ws_host = ws_host
        self.ws_port = ws_port
        self.admin_host = admin_host
        self.admin_port = admin_port
        
        # Create WebSocket server instance
        self.websocket_server = MCPWebSocketServer(host=ws_host, port=ws_port)
        
        # Create admin server with WebSocket server reference
        self.admin_server = MCPAdminServer(websocket_server_instance=self.websocket_server)
        
        # logger.info("Integrated MCP Server initialized")

    async def start_websocket_server(self):
        """Start the WebSocket server."""
        try:
            # logger.info(f"Starting WebSocket server on {self.ws_host}:{self.ws_port}")
            await self.websocket_server.start_server()
        except Exception as e:
            logger.error(f"WebSocket server error: {e}")
            raise

    def start_admin_server(self):
        """Start the admin server in a separate thread."""
        def run_admin():
            logger.info(f"Starting Admin server on {self.admin_host}:{self.admin_port}")
            uvicorn.run(
                self.admin_server.app,
                host=self.admin_host,
                port=self.admin_port,
                log_level="info",
                access_log=False  # Reduce noise
            )
        
        admin_thread = threading.Thread(target=run_admin, daemon=True)
        admin_thread.start()
        return admin_thread

    async def start_both_servers(self):
        """Start both WebSocket and Admin servers."""
        # Start admin server in background thread
        admin_thread = self.start_admin_server()
        
        # Give admin server time to start
        await asyncio.sleep(2)
        
        # logger.info("🚀 Both servers starting...")
        print(f"🚀 WebSocket Server will run on ws://{self.ws_host}:{self.ws_port}")
        print(f"📊 Admin Server will run on http://{self.admin_host}:{self.admin_port}")
        print("📋 Admin endpoints:")
        print(f"  - http://{self.admin_host}:{self.admin_port}/stats")
        print(f"  - http://{self.admin_host}:{self.admin_port}/sessions")
        print(f"  - http://{self.admin_host}:{self.admin_port}/connections")
        
        # Start WebSocket server (this will block)
        await self.start_websocket_server()



async def start_integrated():
    """Start both servers integrated."""
    server = IntegratedMCPServer()
    try:
        await server.start_both_servers()
    except KeyboardInterrupt:
        logger.info("Servers stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")


if __name__ == "__main__":
    asyncio.run(start_integrated())
