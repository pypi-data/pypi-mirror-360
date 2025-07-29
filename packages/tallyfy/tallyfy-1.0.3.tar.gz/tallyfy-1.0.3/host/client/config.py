"""Configuration module for MCP client."""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Server configuration
# DEFAULT_MCP_SERVER_URL = 'https://server.mcp.tallyfy.com/mcp/'
DEFAULT_MCP_SERVER_URL = 'http://localhost:9000/mcp/'
DEFAULT_MODEL = "claude-sonnet-4-20250514"
DEFAULT_MAX_TOKENS = 1000
MAX_ITERATIONS = 10

# Environment variable keys
ENV_ANTHROPIC_API_KEY = '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'
ENV_TALLYFY_API_KEY = 'TALLYFY_API_KEY'
ENV_TALLYFY_ORG_ID = 'TALLYFY_ORG_ID'


def get_api_key() -> str:
    """Get Tallyfy API key from environment."""
    api_key = os.getenv(ENV_TALLYFY_API_KEY)
    if not api_key:
        raise ValueError("TALLYFY_API_KEY environment variable is required")
    return api_key


def get_org_id() -> str:
    """Get Tallyfy org_id from environment."""
    org_id = os.getenv(ENV_TALLYFY_ORG_ID)
    if not org_id:
        raise ValueError("TALLYFY_ORG_ID environment variable is required")
    return org_id


def get_anthropic_api_key() -> str:
    """Get Anthropic API key from environment."""
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable is required")
    return api_key


def get_mcp_server_url() -> str:
    """Get MCP server URL from environment or default."""
    return os.getenv('MCP_SERVER_URL', DEFAULT_MCP_SERVER_URL)