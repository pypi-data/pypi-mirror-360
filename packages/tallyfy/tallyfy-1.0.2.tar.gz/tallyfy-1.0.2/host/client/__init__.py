"""MCP client package."""
from .mcp_client import MCPClient
from .conversation import ConversationManager
from .config import get_api_key, get_org_id, get_anthropic_api_key

__all__ = [
    'MCPClient',
    'ConversationManager',
    'get_api_key', 
    'get_org_id', 
    'get_anthropic_api_key',
]

# Optional import for WebSocket server (requires websockets dependency)
try:
    from .websocket_server import MCPWebSocketServer
    __all__.append('MCPWebSocketServer')
except ImportError:
    pass