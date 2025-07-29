"""Custom exceptions for the MCP client."""


class MCPClientError(Exception):
    """Base exception for MCP client errors."""
    pass


class ConfigurationError(MCPClientError):
    """Raised when there's a configuration issue."""
    pass


class ToolCallError(MCPClientError):
    """Raised when a tool call fails."""
    pass


class ConversationError(MCPClientError):
    """Raised when there's an issue with conversation management."""
    pass