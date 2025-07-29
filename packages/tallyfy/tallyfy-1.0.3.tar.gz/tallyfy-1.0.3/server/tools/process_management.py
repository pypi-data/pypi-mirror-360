"""
Process Management Tools
Tools for managing processes and runs
"""

from typing import List, Dict, Any, Optional
from tallyfy import TallyfySDK, TallyfyError


def register_process_management_tools(mcp):
    """Register all process management tools with the MCP server"""

    @mcp.tool()
    def get_organization_runs(
            org_id: str,
            api_key: str,
            with_data: Optional[str] = None,
            form_fields_values: Optional[bool] = None,
            owners: Optional[str] = None,
            task_status: Optional[str] = None,
            groups: Optional[str] = None,
            status: Optional[str] = None,
            folder: Optional[str] = None,
            checklist_id: Optional[str] = None,
            starred: Optional[bool] = None,
            run_type: Optional[str] = None,
            tag: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all processes (runs) in the organization.

        Args:
            org_id: Organization ID
            api_key: Tallyfy API key for authentication
            with_data: Comma-separated data to include (e.g., 'checklist,tasks,assets,tags')
            form_fields_values: Include form field values
            owners: Filter by specific member IDs
            task_status: Filter by task status ('all', 'in-progress', 'completed')
            groups: Filter by group IDs
            status: Filter by process status ('active', 'problem', 'delayed', 'complete', 'archived')
            folder: Filter by folder ID
            checklist_id: Filter by template ID
            starred: Filter by starred status
            run_type: Filter by type ('procedure', 'form', 'document')
            tag: Filter by tag ID

        Returns:
            List of run objects
        """
        try:
            with TallyfySDK(api_key=api_key) as sdk:
                runs = sdk.get_organization_runs(
                    org_id, with_data, form_fields_values, owners, task_status,
                    groups, status, folder, checklist_id, starred, run_type, tag
                )
                return [run.__dict__ for run in runs]
        except TallyfyError as e:
            raise Exception(f"Failed to get organization runs: {e}")