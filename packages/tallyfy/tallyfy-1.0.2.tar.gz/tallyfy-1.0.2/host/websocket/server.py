"""WebSocket server for MCP client."""

import json
import logging
import asyncio
from typing import Dict, Any, Optional, Set
import websockets
from websockets.server import WebSocketServerProtocol
import markdown
from client.mcp_client import MCPClient
from .session_manager import SessionManager
from client.config import get_org_id

logger = logging.getLogger(__name__)
# Disable websocket server INFO logs (connection failed, connection closed, etc.)
logging.getLogger('websockets.server').setLevel(logging.WARNING)


class MCPWebSocketServer:
    """WebSocket server that provides MCP client functionality to multiple users."""
    
    def __init__(self, host: str = "localhost", port: int = 9001):
        self.host = host
        self.port = port
        self.session_manager = SessionManager()
        self.mcp_client: Optional[MCPClient] = None
        self.active_connections: Set[WebSocketServerProtocol] = set()
        self.connection_sessions: Dict[WebSocketServerProtocol, str] = {}
        self.ping_tasks: Dict[WebSocketServerProtocol, asyncio.Task] = {}
        
        # Load org_id from config
        try:
            self.org_id = get_org_id()
        except ValueError:
            logger.warning("TALLYFY_ORG_ID not configured, will not auto-inject org_id")
            self.org_id = None
    
    async def initialize_mcp_client(self) -> None:
        """Initialize the shared MCP client."""
        try:
            self.mcp_client = MCPClient()
            await self.mcp_client.__aenter__()
            logger.info("MCP client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize MCP client: {e}")
            raise
    
    async def cleanup_mcp_client(self) -> None:
        """Cleanup the shared MCP client."""
        if self.mcp_client:
            try:
                await self.mcp_client.__aexit__(None, None, None)
                logger.info("MCP client cleaned up successfully")
            except Exception as e:
                logger.error(f"Error cleaning up MCP client: {e}")
    
    async def register_connection(self, websocket: WebSocketServerProtocol) -> str:
        """Register a new WebSocket connection and create a session."""
        session_id = self.session_manager.create_session()
        self.active_connections.add(websocket)
        self.connection_sessions[websocket] = session_id
        
        # Start ping task for this connection
        ping_task = asyncio.create_task(self.ping_handler(websocket))
        self.ping_tasks[websocket] = ping_task
        
        logger.info(f"New connection registered with session: {session_id}")
        
        # Send welcome message
        welcome_msg = {
            "type": "connection_established",
            "session_id": session_id,
            "message": "Connected to Tallyfy MCP. Please authenticate with your API key and org ID to start.",
            "authenticated": False
        }
        await self.send_message(websocket, welcome_msg)
        
        return session_id
    
    async def unregister_connection(self, websocket: WebSocketServerProtocol) -> None:
        """Unregister a WebSocket connection and cleanup session."""
        session_id = self.connection_sessions.get(websocket)
        if session_id:
            self.session_manager.remove_session(session_id)
            self.connection_sessions.pop(websocket, None)
        
        # Cancel and cleanup ping task
        ping_task = self.ping_tasks.pop(websocket, None)
        if ping_task:
            ping_task.cancel()
            try:
                await ping_task
            except asyncio.CancelledError:
                pass
        
        self.active_connections.discard(websocket)
        logger.info(f"Connection unregistered for session: {session_id}")
    
    async def send_message(self, websocket: WebSocketServerProtocol, message: Dict[str, Any]) -> None:
        """Send a message to a WebSocket connection."""
        try:
            await websocket.send(json.dumps(message))
        except websockets.exceptions.ConnectionClosed:
            logger.warning("Attempted to send message to closed connection")
        except Exception as e:
            logger.error(f"Error sending message: {e}")
    
    async def ping_handler(self, websocket: WebSocketServerProtocol) -> None:
        """Handle periodic ping messages to keep connection alive."""
        try:
            while websocket in self.active_connections:
                await asyncio.sleep(30)  # Send ping every 30 seconds
                
                if websocket not in self.active_connections:
                    break
                
                try:
                    # Send ping message
                    await self.send_message(websocket, {"type": "ping"})
                    logger.debug(f"Sent ping to connection")
                except websockets.exceptions.ConnectionClosed:
                    logger.debug("Connection closed during ping")
                    break
                except Exception as e:
                    logger.error(f"Error sending ping: {e}")
                    break
                    
        except asyncio.CancelledError:
            logger.debug("Ping handler cancelled")
        except Exception as e:
            logger.error(f"Error in ping handler: {e}")
    
    async def handle_auth_message(self, websocket: WebSocketServerProtocol, session_id: str, auth_data: Dict[str, str]) -> None:
        """Handle authentication message from client."""
        try:
            # Check if user is already authenticated
            if self.session_manager.validate_session_credentials(session_id):
                await self.send_message(websocket, {
                    "type": "auth_info",
                    "message": "✅ You are already authenticated and ready to send queries.",
                    "authenticated": True
                })
                return
            
            api_key = auth_data.get("api_key", "").strip()
            org_id = auth_data.get("org_id", "").strip()
            
            if not api_key or not org_id:
                await self.send_message(websocket, {
                    "type": "auth_error",
                    "message": "Both API key and org ID are required"
                })
                return
            
            # Set credentials for the session (includes verification)
            success = self.session_manager.set_credentials(session_id, api_key, org_id)
            if success:
                await self.send_message(websocket, {
                    "type": "auth_success",
                    "message": "✅ Authentication successful! You can now send queries.",
                    "authenticated": True
                })
                logger.info(f"Session {session_id} authenticated successfully")
            else:
                await self.send_message(websocket, {
                    "type": "auth_error",
                    "message": "❌ Authentication failed: Invalid API key or org ID. Please check your credentials and try again."
                })
                
        except Exception as e:
            logger.error(f"Error handling auth: {e}")
            await self.send_message(websocket, {
                "type": "auth_error",
                "message": f"Authentication error: {str(e)}"
            })

    async def handle_query_message(self, websocket: WebSocketServerProtocol, session_id: str, query: str) -> None:
        """Handle a query message from a client."""
        try:
            # Check if session is authenticated
            if not self.session_manager.validate_session_credentials(session_id):
                await self.send_message(websocket, {
                    "type": "error",
                    "message": "Please authenticate first by sending your API key and org ID"
                })
                return
            
            # Send processing message
            await self.send_message(websocket, {
                "type": "processing",
                "message": "Processing your query..."
            })
            
            # Get conversation and credentials for this session
            conversation = self.session_manager.get_conversation(session_id)
            credentials = self.session_manager.get_credentials(session_id)
            
            if not conversation:
                await self.send_message(websocket, {
                    "type": "error",
                    "message": "Session not found"
                })
                return
            
            # Add user message to conversation
            conversation.add_user_message(query)
            
            # Use the session's org_id, fallback to server default
            org_id = credentials.get('org_id') if credentials else self.org_id
            
            # Process query using shared MCP client
            response = await self.mcp_client.process_query_with_conversation(
                query, conversation, org_id, credentials
            )
            
            # Convert markdown response to HTML for web rendering
            html_response = markdown.markdown(response, extensions=['tables', 'fenced_code', 'codehilite'])
            
            # Send response back to client
            await self.send_message(websocket, {
                "type": "response",
                "message": html_response
            })
            
        except Exception as e:
            logger.error(f"Error handling query: {e}")
            await self.send_message(websocket, {
                "type": "error",
                "message": f"Error processing query: {str(e)}"
            })
    
    async def handle_clear_message(self, websocket: WebSocketServerProtocol, session_id: str) -> None:
        """Handle a clear conversation message."""
        success = self.session_manager.clear_conversation(session_id)
        if success:
            await self.send_message(websocket, {
                "type": "info",
                "message": "✨ Conversation history cleared!"
            })
        else:
            await self.send_message(websocket, {
                "type": "error",
                "message": "Failed to clear conversation"
            })
    
    async def handle_message(self, websocket: WebSocketServerProtocol, message: str) -> None:
        """Handle incoming WebSocket message."""
        session_id = self.connection_sessions.get(websocket)
        if not session_id:
            await self.send_message(websocket, {
                "type": "error",
                "message": "Session not found"
            })
            return
        
        try:
            # Try to parse as JSON first
            data = {}
            try:
                data = json.loads(message)
                message_type = data.get("type", "query")
                content = data.get("content", "")
            except json.JSONDecodeError:
                # Treat as plain text query
                message_type = "query"
                content = message.strip()
            
            # Handle different message types
            if message_type == "auth":
                auth_data = data if isinstance(data, dict) else {}
                await self.handle_auth_message(websocket, session_id, auth_data)
            
            elif message_type == "query":
                if content.lower() == "quit":
                    await self.send_message(websocket, {
                        "type": "disconnect",
                        "message": "👋 Goodbye!"
                    })
                    await websocket.close()
                elif content.lower() == "clear":
                    await self.handle_clear_message(websocket, session_id)
                elif content:
                    await self.handle_query_message(websocket, session_id, content)
                else:
                    await self.send_message(websocket, {
                        "type": "info",
                        "message": "Please provide a query"
                    })
            
            elif message_type == "ping":
                await self.send_message(websocket, {"type": "pong"})
            
            else:
                await self.send_message(websocket, {
                    "type": "error",
                    "message": f"Unknown message type: {message_type}"
                })
                
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await self.send_message(websocket, {
                "type": "error",
                "message": f"Error processing message: {str(e)}"
            })
    
    async def connection_handler(self, websocket: WebSocketServerProtocol, path: str) -> None:
        """Handle WebSocket connection lifecycle."""
        session_id = None
        try:
            # Register the connection
            session_id = await self.register_connection(websocket)
            
            # Handle messages
            async for message in websocket:
                await self.handle_message(websocket, message)
                
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Connection closed for session: {session_id}")
        except Exception as e:
            logger.error(f"Error in connection handler: {e}")
        finally:
            # Cleanup
            await self.unregister_connection(websocket)
    
    async def periodic_cleanup(self) -> None:
        """Periodically cleanup inactive sessions."""
        while True:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes
                cleaned = self.session_manager.cleanup_inactive_sessions()
                if cleaned > 0:
                    logger.info(f"Cleaned up {cleaned} inactive sessions")
            except Exception as e:
                logger.error(f"Error in periodic cleanup: {e}")
    
    async def start_server(self) -> None:
        """Start WebSocket server."""
        try:
            # Initialize MCP client
            await self.initialize_mcp_client()
            
            # Start periodic cleanup task
            cleanup_task = asyncio.create_task(self.periodic_cleanup())
            
            # Start WebSocket server
            logger.info(f"Starting WebSocket server on {self.host}:{self.port}")
            
            async with websockets.serve(
                self.connection_handler,
                self.host,
                self.port,
                ping_interval=None,
                ping_timeout=None
            ):
                logger.info(f"🚀 MCP WebSocket Server running on ws://{self.host}:{self.port}")
                # print(f"🚀 MCP WebSocket Server running on ws://{self.host}:{self.port}")
                # print("Server is ready to accept connections...")
                
                # Keep server running
                await asyncio.Future()  # Run forever
                
        except Exception as e:
            logger.error(f"Error starting server: {e}")
            raise
        finally:
            # Cleanup
            cleanup_task.cancel()
            await self.cleanup_mcp_client()