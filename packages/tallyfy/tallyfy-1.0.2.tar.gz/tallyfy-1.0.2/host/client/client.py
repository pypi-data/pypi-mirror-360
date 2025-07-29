#!/usr/bin/env python3
"""MCP Client - Interactive CLI for Tallyfy workflow automation."""

import asyncio
import sys
import logging

from .mcp_client import MCPClient
from .config import get_api_key, get_org_id

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load configuration
api_key = get_api_key()
org_id = get_org_id()
async def main():
    """Main interactive loop for the MCP client."""
    try:
        async with MCPClient() as client:
            print("🚀 Tallyfy MCP Client started. Type 'quit' to exit, 'clear' to reset conversation.")
            
            while True:
                try:
                    query = input("\n👥 Query: ").strip()

                    if query.lower() == 'quit':
                        break
                    elif query.lower() == 'clear':
                        client.clear_conversation()
                        print("✨ Conversation history cleared!")
                        continue
                    elif not query:
                        continue

                    # Process the query
                    response = await client.process_query(query, org_id)
                    print(response)

                except KeyboardInterrupt:
                    print("\n\n👋 Interrupted by user")
                    break
                except Exception as e:
                    logger.error(f"Error processing query: {e}")
                    print(f"\n❌ Error: {str(e)}")
    
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        print(f"\n❌ Configuration Error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    finally:
        print("\n👋 Goodbye!")

if __name__ == "__main__":
    asyncio.run(main())