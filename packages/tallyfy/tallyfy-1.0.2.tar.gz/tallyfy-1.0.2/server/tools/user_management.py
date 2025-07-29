"""
User Management Tools
Tools for managing organization users and guests
"""

from typing import List, Dict, Any, Optional
from tallyfy import TallyfySDK, TallyfyError


def register_user_management_tools(mcp):
    """Register all user management tools with the MCP server"""

    @mcp.tool()
    def get_organization_users(org_id: str, api_key: str, with_groups: bool = False) -> List[Dict[str, Any]]:
        """
        Get all organization members with full profile data.

        Args:
            org_id: Organization ID
            api_key: Tallyfy API key for authentication
            with_groups: Include user groups data (default: False)

        Returns:
            List of user objects with full profile data
        """
        try:
            with TallyfySDK(api_key=api_key) as sdk:
                users = sdk.get_organization_users(org_id, with_groups)
                return [user.__dict__ for user in users]
        except TallyfyError as e:
            raise Exception(f"Failed to get organization users: {e}")

    @mcp.tool()
    def get_organization_users_list(org_id: str, api_key: str) -> List[Dict[str, Any]]:
        """
        Get all organization members with minimal data for listing.

        Args:
            org_id: Organization ID
            api_key: Tallyfy API key for authentication

        Returns:
            List of user objects with minimal data
        """
        try:
            with TallyfySDK(api_key=api_key) as sdk:
                users = sdk.get_organization_users_list(org_id)
                return [user.__dict__ for user in users]
        except TallyfyError as e:
            raise Exception(f"Failed to get organization users list: {e}")

    @mcp.tool()
    def get_organization_guests(org_id: str, api_key: str, with_stats: bool = False) -> List[Dict[str, Any]]:
        """
        Get all guests in an organization with full profile data.

        Args:
            org_id: Organization ID
            api_key: Tallyfy API key for authentication
            with_stats: Include guest statistics (default: False)

        Returns:
            List of guest objects with full profile data
        """
        try:
            with TallyfySDK(api_key=api_key) as sdk:
                guests = sdk.get_organization_guests(org_id, with_stats)
                return [guest.__dict__ for guest in guests]
        except TallyfyError as e:
            raise Exception(f"Failed to get organization guests: {e}")

    @mcp.tool()
    def get_organization_guests_list(org_id: str, api_key: str) -> List[Dict[str, Any]]:
        """
        Get organization guests with minimal data.

        Args:
            org_id: Organization ID
            api_key: Tallyfy API key for authentication

        Returns:
            List of guest objects with minimal data
        """
        try:
            with TallyfySDK(api_key=api_key) as sdk:
                guests = sdk.get_organization_guests_list(org_id)
                return [guest.__dict__ for guest in guests]
        except TallyfyError as e:
            raise Exception(f"Failed to get organization guests list: {e}")

    @mcp.tool()
    def invite_user_to_organization(
            org_id: str,
            api_key: str,
            email: str,
            first_name: str,
            last_name: str,
            role: str = "light",
            message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Invite a member to your organization.

        Args:
            org_id: Organization ID
            api_key: Tallyfy API key for authentication
            email: Email address of the user to invite
            first_name: First name of the user (required)
            last_name: Last name of the user (required)
            role: User role - 'light', 'standard', or 'admin' (default: 'light')
            message: Custom invitation message (optional)

        Returns:
            User object for the invited user
        """
        try:
            with TallyfySDK(api_key=api_key) as sdk:
                user = sdk.invite_user_to_organization(
                    org_id, email, first_name, last_name, role, message
                )
                return user.__dict__ if user else {}
        except TallyfyError as e:
            raise Exception(f"Failed to invite user to organization: {e}")
        except ValueError as e:
            raise Exception(f"Invalid input: {e}")
