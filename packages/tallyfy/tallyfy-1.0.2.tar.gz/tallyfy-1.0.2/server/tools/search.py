"""
Search Tools
Tools for searching tasks, processes, and templates
"""

from typing import List, Dict, Any, Optional
from tallyfy import TallyfySDK, TallyfyError


def register_search_tools(mcp):
    """Register all search tools with the MCP server"""
    
    @mcp.tool()
    def search_for_tasks(org_id: str, api_key: str, query: str) -> List[Dict[str, Any]]:
        """
        Search for tasks in the organization.

        Args:
            org_id: Organization ID
            api_key: Tallyfy API key for authentication
            query: Search query string

        Returns:
            List of matching task objects
        """
        try:
            with TallyfySDK(api_key=api_key) as sdk:
                tasks = sdk.search(org_id, query, 'task')
                return [task.__dict__ for task in tasks]
        except TallyfyError as e:
            raise Exception(f"Failed to search for tasks in thr organization: {e}")

    @mcp.tool()
    def search_for_processes(org_id: str, api_key: str, query: str) -> List[Dict[str, Any]]:
        """
        Search for processes in the organization.

        Args:
            org_id: Organization ID
            api_key: Tallyfy API key for authentication
            query: Search query string

        Returns:
            List of matching process objects
        """
        try:
            with TallyfySDK(api_key=api_key) as sdk:
                processes = sdk.search(org_id, query, 'process')
                return [process.__dict__ for process in processes]
        except TallyfyError as e:
            raise Exception(f"Failed to search for processes in the organization: {e}")

    @mcp.tool()
    def search_for_templates(org_id: str, api_key: str, query: str) -> List[Dict[str, Any]]:
        """
        Search for templates in the organization.

        Args:
            org_id: Organization ID
            api_key: Tallyfy API key for authentication
            query: Search query string

        Returns:
            List of matching template objects
        """
        try:
            with TallyfySDK(api_key=api_key) as sdk:
                templates = sdk.search(org_id, query, 'blueprint')
                return [template.__dict__ for template in templates]
        except TallyfyError as e:
            raise Exception(f"Failed to search for templates in the organization: {e}")