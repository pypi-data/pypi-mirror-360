"""
User management functionality for Tallyfy SDK
"""

from typing import List, Optional
from .models import User, Guest, TallyfyError


class UserManagement:
    """Handles user and guest management operations"""
    
    def __init__(self, sdk):
        self.sdk = sdk
    def get_current_user_info(self, org_id: str) -> Optional[User]:
        """
        Get current user with full profile data.

        Args:
            org_id: Organization ID

        Returns:
            A User object with full profile data

        Raises:
            TallyfyError: If the request fails
        """
        try:
            endpoint = f"organizations/{org_id}/me"
            params = {}

            response_data = self.sdk._make_request('GET', endpoint, params=params)

            if isinstance(response_data, dict) and 'data' in response_data:
                user_data = response_data['data']
                return User.from_dict(user_data)
            else:
                if isinstance(response_data, list):
                    return User.from_dict(response_data['data'])
                else:
                    self.sdk.logger.warning("Unexpected response format for getting current user")
                    return []

        except TallyfyError as e:
            self.sdk.logger.error(f"Failed to get organization users for org {org_id}: {e}")
            raise
    def get_organization_users(self, org_id: str, with_groups: bool = False) -> List[User]:
        """
        Get all organization members with full profile data.

        Args:
            org_id: Organization ID
            with_groups: Include user groups data

        Returns:
            List of User objects with full profile data

        Raises:
            TallyfyError: If the request fails
        """
        try:
            endpoint = f"organizations/{org_id}/users"
            params = {}
            if with_groups:
                params['with'] = 'groups'
            
            response_data = self.sdk._make_request('GET', endpoint, params=params)

            if isinstance(response_data, dict) and 'data' in response_data:
                users_data = response_data['data']
                return [User.from_dict(user_data) for user_data in users_data]
            else:
                if isinstance(response_data, list):
                    return [User.from_dict(user_data) for user_data in response_data]
                else:
                    self.sdk.logger.warning("Unexpected response format for users")
                    return []

        except TallyfyError as e:
            self.sdk.logger.error(f"Failed to get organization users for org {org_id}: {e}")
            raise

    def get_organization_users_list(self, org_id: str) -> List[User]:
        """
        Get all organization members with minimal data for listing.

        Args:
            org_id: Organization ID

        Returns:
            List of User objects with minimal data

        Raises:
            TallyfyError: If the request fails
        """
        try:
            endpoint = f"organizations/{org_id}/users-list"
            response_data = self.sdk._make_request('GET', endpoint)

            if isinstance(response_data, dict) and 'data' in response_data:
                users_data = response_data['data']
                return [User.from_dict(user_data) for user_data in users_data]
            else:
                if isinstance(response_data, list):
                    return [User.from_dict(user_data) for user_data in response_data]
                else:
                    self.sdk.logger.warning("Unexpected response format for users list")
                    return []

        except TallyfyError as e:
            self.sdk.logger.error(f"Failed to get organization users list for org {org_id}: {e}")
            raise

    def get_organization_guests(self, org_id: str, with_stats: bool = False) -> List[Guest]:
        """
        Get all guests in an organization with full profile data.

        Args:
            org_id: Organization ID
            with_stats: Include guest statistics

        Returns:
            List of Guest objects with full profile data

        Raises:
            TallyfyError: If the request fails
        """
        try:
            endpoint = f"organizations/{org_id}/guests"
            params = {}
            if with_stats:
                params['with'] = 'stats'
            
            response_data = self.sdk._make_request('GET', endpoint, params=params)

            if isinstance(response_data, dict) and 'data' in response_data:
                guests_data = response_data['data']
                return [Guest.from_dict(guest_data) for guest_data in guests_data]
            else:
                if isinstance(response_data, list):
                    return [Guest.from_dict(guest_data) for guest_data in response_data]
                else:
                    self.sdk.logger.warning("Unexpected response format for guests")
                    return []

        except TallyfyError as e:
            self.sdk.logger.error(f"Failed to get organization guests for org {org_id}: {e}")
            raise

    def get_organization_guests_list(self, org_id: str) -> List[Guest]:
        """
        Get organization guests with minimal data.

        Args:
            org_id: Organization ID

        Returns:
            List of Guest objects with minimal data

        Raises:
            TallyfyError: If the request fails
        """
        try:
            endpoint = f"organizations/{org_id}/guests-list"
            response_data = self.sdk._make_request('GET', endpoint)

            # Handle different response formats
            if isinstance(response_data, dict) and 'data' in response_data:
                guests_data = response_data['data']
                if isinstance(guests_data, list):
                    return [Guest.from_dict(guest_data) for guest_data in guests_data]
                else:
                    return [Guest.from_dict(guests_data)]
            elif isinstance(response_data, list):
                # Direct list response
                return [Guest.from_dict(guest_data) for guest_data in response_data]
            else:
                self.sdk.logger.warning("Unexpected response format for guests list")
                return []

        except TallyfyError as e:
            self.sdk.logger.error(f"Failed to get organization guests list for org {org_id}: {e}")
            raise

    def invite_user_to_organization(self, org_id: str, email: str, first_name: str, last_name: str, role: str = "light", message: Optional[str] = None) -> Optional[User]:
        """
        Invite a member to your organization.

        Args:
            org_id: Organization ID
            email: Email address of the user to invite
            first_name: First name of the user (required)
            last_name: Last name of the user (required)
            role: User role - 'light', 'standard', or 'admin' (default: 'light')
            message: Custom invitation message (optional)

        Returns:
            User object for the invited user

        Raises:
            TallyfyError: If the request fails
            ValueError: If role is not valid
        """
        # Validate role
        valid_roles = ["light", "standard", "admin"]
        if role not in valid_roles:
            raise ValueError(f"Role must be one of: {', '.join(valid_roles)}")
        
        try:
            endpoint = f"organizations/{org_id}/users/invite"
            
            invite_data = {
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "role": role
            }
            
            # Add message if provided, otherwise use default
            if message:
                invite_data["message"] = message
            else:
                invite_data["message"] = "Please join Tallyfy - it's going to help us automate tasks between people."
            
            response_data = self.sdk._make_request('POST', endpoint, data=invite_data)

            if isinstance(response_data, dict) and 'data' in response_data:
                user_data = response_data['data']
                return User.from_dict(user_data)
            else:
                self.sdk.logger.warning("Unexpected response format for user invitation")
                return None

        except TallyfyError as e:
            self.sdk.logger.error(f"Failed to invite user to organization {org_id}: {e}")
            raise