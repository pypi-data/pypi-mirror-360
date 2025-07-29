"""MCP client operations and tool handling."""

import logging
from typing import List, Dict, Any, Optional, Tuple
from anthropic import Anthropic
from fastmcp import Client

from .config import (
    get_anthropic_api_key, 
    get_mcp_server_url, 
    DEFAULT_MODEL, 
    DEFAULT_MAX_TOKENS, 
    MAX_ITERATIONS
)
from .conversation import ConversationManager
from .prompts import SYSTEM_PROMPT, FINAL_RESPONSE_PROMPT

logger = logging.getLogger(__name__)
logging.getLogger('httpx').setLevel(logging.WARNING)

class MCPClient:
    """Handles MCP client operations and tool calls."""
    
    def __init__(self):
        self.anthropic_client = Anthropic(api_key=get_anthropic_api_key())
        self.mcp_client = Client(get_mcp_server_url())
        self.conversation = ConversationManager()
    
    async def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get available tools from the MCP server."""
        try:
            response = await self.mcp_client.list_tools()
            tools = []
            for tool in response:
                tool_def = {
                    "name": tool.name,
                    "description": tool.description or "",
                    "input_schema": tool.inputSchema or {}
                }
                tools.append(tool_def)
            return tools
        except Exception as e:
            logger.error(f"Failed to get available tools: {e}")
            raise
    
    async def call_tool(self, tool_name: str, tool_args: Dict[str, Any]) -> str:
        """Execute a tool call and return the result."""
        try:
            result = await self.mcp_client.call_tool(tool_name, tool_args)
            result_content = str(result.content) if hasattr(result, 'content') else str(result)
            return result_content
        except Exception as e:
            error_msg = f"Tool call failed: {str(e)}"
            logger.error(error_msg)
            return f"Error: {str(e)}"
    
    def create_claude_request(self, messages: List[Dict[str, Any]], tools: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a request for Claude API."""
        return {
            "model": DEFAULT_MODEL,
            "max_tokens": DEFAULT_MAX_TOKENS,
            "messages": messages,
            "tools": tools,
            "system": SYSTEM_PROMPT
        }
    
    async def process_tool_calls(self, response_content: List[Any], query_messages: List[Dict[str, Any]], credentials: Optional[Dict[str, str]] = None) -> Tuple[bool, List[str]]:
        """Process tool calls from Claude's response."""
        tool_calls_made = False
        text_responses = []
        
        for content in response_content:
            if content.type == 'text':
                # Check if this is the final response (no tool calls in the same response)
                if not any(c.type == 'tool_use' for c in response_content):
                    text_responses.append(content.text)
            elif content.type == 'tool_use':
                tool_calls_made = True
                tool_name = content.name
                tool_args = content.input or {}
                
                # Inject credentials if available
                if credentials and credentials.get('api_key') and credentials.get('org_id'):
                    tool_args['api_key'] = credentials['api_key']
                    # Only inject org_id if not already present in args
                    if 'org_id' not in tool_args:
                        tool_args['org_id'] = credentials['org_id']
                
                # Create sanitized args for logging (remove sensitive data)
                log_args = {k: v for k, v in tool_args.items() if k != 'api_key'}
                # Add user_id to log_args if available in credentials
                if credentials and credentials.get('user_id'):
                    log_args['user_id'] = credentials['user_id']
                logger.info(f"🔧 Calling {tool_name} with args: {log_args}")
                
                # Execute tool call
                result_content = await self.call_tool(tool_name, tool_args)
                logger.debug(f"Tool {tool_name} returned result of length {len(result_content)}")
                # Add Claude's message with tool call to conversation
                query_messages.append({
                    "role": "assistant",
                    "content": response_content
                })
                
                # Add tool result to conversation
                query_messages.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": content.id,
                            "content": result_content
                        }
                    ]
                })
        
        return tool_calls_made, text_responses
    
    async def get_final_response(self, query_messages: List[Dict[str, Any]]) -> List[str]:
        """Get a final response from Claude when no text was returned."""
        try:
            final_response = self.anthropic_client.messages.create(
                model=DEFAULT_MODEL,
                max_tokens=DEFAULT_MAX_TOKENS,
                messages=query_messages,
                system=SYSTEM_PROMPT + FINAL_RESPONSE_PROMPT
            )
            
            final_text = []
            for content in final_response.content:
                if content.type == 'text':
                    final_text.append(content.text)
            
            # Add final response to conversation history
            self.conversation.add_assistant_message(final_response.content)
            return final_text
        except Exception as e:
            logger.error(f"Failed to get final response: {e}")
            return [f"Error getting final response: {str(e)}"]
    
    async def process_query(self, query: str, org_id: Optional[str] = None) -> str:
        """Process a user query using Claude and available tools."""
        return await self.process_query_with_conversation(query, self.conversation, org_id)
    
    async def process_query_with_conversation(self, query: str, conversation: ConversationManager, org_id: Optional[str] = None, credentials: Optional[Dict[str, str]] = None) -> str:
        """Process a user query using Claude and available tools with a specific conversation and credentials."""
        try:
            # Enhance query with org_id if provided
            if org_id:
                query = conversation.enhance_query_with_org_id(query, org_id)
            
            # Add user query to conversation
            conversation.add_user_message(query)
            
            # Get available tools
            available_tools = await self.get_available_tools()
            
            # Track messages for this query session
            query_messages = conversation.get_history()
            final_response_text = []
            iteration_count = 0
            
            while iteration_count < MAX_ITERATIONS:
                iteration_count += 1
                logger.debug(f"Processing iteration {iteration_count}")
                
                # Make Claude API call
                request_data = self.create_claude_request(query_messages, available_tools)
                response = self.anthropic_client.messages.create(**request_data)
                
                # Process tool calls and get text responses
                tool_calls_made, text_responses = await self.process_tool_calls(
                    response.content, query_messages, credentials
                )
                
                # If we got text responses and no tool calls, we're done
                if text_responses and not tool_calls_made:
                    final_response_text.extend(text_responses)
                    break
                
                # If no tool calls were made, we have the final response
                if not tool_calls_made:
                    break
            
            # Update conversation history
            conversation.history = query_messages.copy()
            
            # Return final response
            if final_response_text:
                return "\n".join(final_response_text)
            else:
                # Get final response from Claude
                final_text = await self.get_final_response(query_messages)
                return "\n".join(final_text) if final_text else "No response received"
                
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return f"Error: {str(e)}"
    
    def clear_conversation(self) -> None:
        """Clear the conversation history."""
        self.conversation.clear()
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.mcp_client.__aenter__()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.mcp_client.__aexit__(exc_type, exc_val, exc_tb)