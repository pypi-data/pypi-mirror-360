"""Conversation management for the MCP client."""

from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class ConversationManager:
    """Manages conversation history and message formatting."""
    
    def __init__(self):
        self.history: List[Dict[str, Any]] = []
    
    def add_user_message(self, content: str) -> None:
        """Add a user message to the conversation history."""
        self.history.append({"role": "user", "content": content})
        logger.debug(f"Added user message: {content[:100]}...")
    
    def add_assistant_message(self, content: Any) -> None:
        """Add an assistant message to the conversation history."""
        self.history.append({"role": "assistant", "content": content})
        logger.debug("Added assistant message to history")
    
    def add_tool_result(self, tool_use_id: str, result: str) -> None:
        """Add a tool result to the conversation history."""
        self.history.append({
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": tool_use_id,
                    "content": result
                }
            ]
        })
        logger.debug(f"Added tool result for {tool_use_id}")
    
    def clear(self) -> None:
        """Clear the conversation history."""
        self.history.clear()
        logger.info("Conversation history cleared")
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get a copy of the conversation history."""
        return self.history.copy()
    
    def enhance_query_with_org_id(self, query: str, org_id: str) -> str:
        """Enhance query with org_id if not already present."""
        if 'org_id' not in query.lower() and org_id:
            return f"{query} (use org_id: {org_id})"
        return query