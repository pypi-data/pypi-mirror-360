"""Standalone FastAPI admin server for MCP WebSocket monitoring."""

import logging
from typing import Dict, Any
from datetime import datetime
from fastapi import FastAPI

logger = logging.getLogger(__name__)


class MCPAdminServer:
    """Standalone admin server for monitoring MCP WebSocket connections."""

    def __init__(self, websocket_server_instance=None):
        self.websocket_server = websocket_server_instance
        self.app = self._create_app()

    def _create_app(self) -> FastAPI:
        """Create FastAPI application."""
        app = FastAPI(
            title="MCP Server Admin",
            description="Admin interface for MCP WebSocket Server",
            version="1.0.0"
        )

        @app.get("/")
        def admin_home():
            """Admin home page with basic server info."""
            return {
                "title": "MCP Server Admin",
                "description": "Admin interface for monitoring MCP WebSocket connections and sessions",
                "status": "running",
                "endpoints": {
                    "/stats": "Server statistics",
                    "/sessions": "Detailed session information",
                    "/connections": "Active WebSocket connections",
                    "/sessions/{session_id}": "Individual session details"
                }
            }

        @app.get("/stats")
        def get_stats():
            """Get basic server statistics."""
            if not self.websocket_server:
                return {"error": "WebSocket server not available"}
            return self._get_server_stats()

        @app.get("/sessions")
        def get_sessions():
            """Get detailed information about all sessions."""
            if not self.websocket_server:
                return {"error": "WebSocket server not available"}
            return self.websocket_server.session_manager.get_all_sessions_info()

        @app.get("/connections")
        def get_connections():
            """Get information about active WebSocket connections."""
            if not self.websocket_server:
                return {"error": "WebSocket server not available"}
            return self._get_connections_info()

        @app.get("/sessions/{session_id}")
        def get_session_detail(session_id: str):
            """Get detailed information about a specific session."""
            if not self.websocket_server:
                return {"error": "WebSocket server not available"}
            return self._get_session_detail(session_id)

        return app

    def _get_server_stats(self) -> Dict[str, Any]:
        """Get server statistics."""
        if not self.websocket_server:
            return {"error": "WebSocket server not available"}

        return {
            "active_connections": len(self.websocket_server.active_connections),
            "session_stats": self.websocket_server.session_manager.get_session_stats(),
            "server_info": {
                "host": self.websocket_server.host,
                "port": self.websocket_server.port,
                "admin_port": getattr(self.websocket_server, 'admin_port', 'N/A'),
                "org_id_configured": self.websocket_server.org_id is not None
            }
        }

    def _get_connections_info(self) -> Dict[str, Any]:
        """Get information about active WebSocket connections."""
        if not self.websocket_server:
            return {"error": "WebSocket server not available"}

        connections_info = []

        for websocket, session_id in self.websocket_server.connection_sessions.items():
            session = self.websocket_server.session_manager.get_session(session_id)
            if session:
                try:
                    remote_addr = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}" if websocket.remote_address else "unknown"
                except (TypeError, IndexError, AttributeError):
                    remote_addr = "unknown"

                connection_info = {
                    "session_id": session_id,
                    "remote_address": remote_addr,
                    "state": str(websocket.state) if hasattr(websocket, 'state') else "unknown",
                    "has_credentials": session.has_credentials(),
                    "org_id": session.org_id if session.has_credentials() else None,
                    "created_at": session.created_at.isoformat(),
                    "last_activity": session.last_activity.isoformat()
                }
                connections_info.append(connection_info)

        return {
            "total_connections": len(self.websocket_server.active_connections),
            "connections": connections_info
        }

    def _get_session_detail(self, session_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific session."""
        if not self.websocket_server:
            return {"error": "WebSocket server not available"}

        session = self.websocket_server.session_manager.get_session(session_id)
        if not session:
            return {"error": "Session not found"}

        # Calculate session duration
        duration_seconds = (datetime.now() - session.created_at).total_seconds()
        idle_seconds = (datetime.now() - session.last_activity).total_seconds()

        return {
            "session_id": session_id,
            "user_id": session.user_id,
            "created_at": session.created_at.isoformat(),
            "last_activity": session.last_activity.isoformat(),
            "duration_seconds": int(duration_seconds),
            "idle_seconds": int(idle_seconds),
            "has_credentials": session.has_credentials(),
            "org_id": session.org_id if session.has_credentials() else None,
            "is_active": session_id in self.websocket_server.session_manager._active_connections,
            "conversation_messages": len(session.conversation.history) if session.conversation else 0,
            "conversation_history": [
                {
                    "role": msg.get("role", "unknown"),
                    "content_length": len(str(msg.get("content", "")))
                } for msg in session.conversation.history
            ] if session.conversation else []
        }

    def set_websocket_server(self, websocket_server):
        """Set the WebSocket server instance for monitoring."""
        self.websocket_server = websocket_server
        logger.info("WebSocket server instance attached to admin server")