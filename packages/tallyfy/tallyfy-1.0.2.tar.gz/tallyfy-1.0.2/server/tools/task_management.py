"""
Task Management Tools
Tools for managing tasks and task assignments
"""

from typing import List, Dict, Any, Optional

from tallyfy import TallyfySDK, TallyfyError, TaskOwners
from .date_utils import DateExtractor

# Global date extractor instance
date_extractor = DateExtractor()


def resolve_user_ids(org_id: str, api_key: str, user_names: List[str], user_emails: List[str]) -> List[int]:
    """Resolve user names and emails to user IDs"""
    if not user_names and not user_emails:
        return []

    try:
        with TallyfySDK(api_key=api_key) as sdk:
            users = sdk.get_organization_users_list(org_id)
            resolved_ids = []

        # Create lookup dictionaries for faster searching
        users_by_email = {user.email.lower(): user.id for user in users}
        users_by_name = {f"{user.first_name} {user.last_name}".lower(): user.id for user in users}
        users_by_username = {user.username.lower(): user.id for user in users}

        # Resolve by email
        for email in user_emails:
            if email.lower() in users_by_email:
                resolved_ids.append(users_by_email[email.lower()])

        # Resolve by name (first last)
        for name in user_names:
            name_lower = name.lower()
            if name_lower in users_by_name:
                resolved_ids.append(users_by_name[name_lower])
            elif name_lower in users_by_username:
                resolved_ids.append(users_by_username[name_lower])

        return resolved_ids
    except Exception as e:
        raise Exception(f"Failed to resolve user IDs: {e}")


def resolve_group_ids(org_id: str, api_key: str, group_names: List[str]) -> List[str]:
    """Resolve group names to group IDs"""
    ## TODO
    # Note: This would require a get_organization_groups method in the SDK
    # For now, return empty list as groups endpoint is not implemented
    return []


def register_task_management_tools(mcp):
    """Register all task management tools with the MCP server"""

    @mcp.tool()
    def get_my_tasks(org_id: str, api_key:str) -> List[Dict[str, Any]]:
        """
        Get all tasks assigned to the current user in the organization.

        Args:
            org_id: Organization ID
            api_key: Tallyfy API key for authentication

        Returns:
            List of task objects assigned to the current user
        """
        try:
            with TallyfySDK(api_key=api_key) as sdk:
                tasks = sdk.get_my_tasks(org_id)
                return [task.__dict__ for task in tasks]
        except TallyfyError as e:
            raise Exception(f"Failed to get my tasks: {e}")

    @mcp.tool()
    def get_user_tasks(org_id: str, api_key: str, user_id: int) -> List[Dict[str, Any]]:
        """
        Get all tasks assigned to the given user in the organization.

        Args:
            org_id: Organization ID
            api_key: Tallyfy API key for authentication
            user_id: User ID

        Returns:
            List of Task objects assigned to the given user ID
        """
        try:
            with TallyfySDK(api_key=api_key) as sdk:
                tasks = sdk.get_user_tasks(org_id, user_id)
                return [task.__dict__ for task in tasks]
        except TallyfyError as e:
            raise Exception(f"Failed to get user's tasks: {e}")

    @mcp.tool()
    def get_tasks_for_process(
            org_id: str,
            api_key: str,
            process_id: Optional[str] = None,
            process_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get all tasks for a given process (run). Returns validated data with search context.

        Args:
            org_id: Organization ID
            api_key: Tallyfy API key for authentication
            process_id: Process (run) ID to get tasks for
            process_name: Process (run) name to get tasks for (alternative to process_id)

        Returns:
            Dict containing:
            - tasks: List of task objects for the specified process
            - process_info: Information about the found process
            - search_context: Details about how the process was found (if searched by name)
        """
        try:
            # Validate inputs
            if not org_id or not org_id.strip():
                raise Exception("Organization ID is required and cannot be empty")

            if not process_id and not process_name:
                raise Exception("Either process_id or process_name must be provided")

            # Use SDK with context manager
            with TallyfySDK(api_key=api_key) as sdk:
                # If searching by name, get search context
                search_context = {
                    "searched_name": process_name if process_name else None,
                    "found_process_id": None,
                    "search_successful": False,
                    "error": None
                }
                resolved_process_id = process_id

                if process_name and not process_id:
                    try:
                        resolved_process_id = sdk.search_processes_by_name(org_id, process_name)
                        search_context.update({
                            "found_process_id": resolved_process_id,
                            "search_successful": True
                        })
                    except TallyfyError as search_error:
                        search_context.update({
                            "error": str(search_error)
                        })
                        raise Exception(f"Process search failed: {search_error}")

                # Get tasks for the process
                tasks = sdk.get_tasks_for_process(org_id, resolved_process_id, None)

                # Validate and sanitize task data
                validated_tasks = []
                for task in tasks:
                    task_dict = task.__dict__.copy()

                    # Ensure required fields have valid values
                    task_dict['id'] = task_dict.get('id', '')
                    task_dict['title'] = task_dict.get('title', 'Untitled Task')
                    task_dict['status'] = task_dict.get('status', 'unknown')
                    task_dict['increment_id'] = task_dict.get('increment_id', 0)

                    # Convert None values to appropriate defaults
                    for key, value in task_dict.items():
                        if value is None:
                            if key in ['created_at', 'last_updated', 'deadline', 'started_at', 'completed_at']:
                                task_dict[key] = ''
                            elif key in ['position', 'max_assignable']:
                                task_dict[key] = 0
                            elif key in ['is_completable', 'allow_guest_owners', 'is_oneoff_task',
                                         'everyone_must_complete']:
                                task_dict[key] = False
                            elif key == 'task_type':
                                task_dict[key] = 'task'

                    validated_tasks.append(task_dict)

                # Get process information for context
                process_info = None
                if resolved_process_id:
                    try:
                        # Try to get process details from runs
                        runs = sdk.get_organization_runs(org_id)
                        matching_run = next((run for run in runs if run.id == resolved_process_id), None)
                        if matching_run:
                            process_info = {
                                "id": matching_run.id,
                                "name": matching_run.name,
                                "status": matching_run.status,
                                "increment_id": matching_run.increment_id
                            }
                    except Exception:
                        # If we can't get process info, that's okay
                        process_info = {"id": resolved_process_id, "name": process_name or "Unknown"}

            return {
                "tasks": validated_tasks,
                "task_count": len(validated_tasks),
                "process_info": process_info,
                "search_context": search_context,
                "success": True
            }

        except TallyfyError as e:
            return {
                "tasks": [],
                "task_count": 0,
                "process_info": None,
                "search_context": search_context if 'search_context' in locals() else None,
                "success": False,
                "error": str(e),
                "error_type": "TallyfyError"
            }
        except ValueError as e:
            return {
                "tasks": [],
                "task_count": 0,
                "process_info": None,
                "search_context": None,
                "success": False,
                "error": str(e),
                "error_type": "ValueError"
            }
        except Exception as e:
            return {
                "tasks": [],
                "task_count": 0,
                "process_info": None,
                "search_context": search_context if 'search_context' in locals() else None,
                "success": False,
                "error": str(e),
                "error_type": "UnknownError"
            }

    @mcp.tool()
    def create_task_from_text(
            org_id: str,
            api_key: str,
            user_input: str,
            user_names: Optional[List[str]] = None,
            user_emails: Optional[List[str]] = None,
            guest_emails: Optional[List[str]] = None,
            group_names: Optional[List[str]] = None,
            max_assignable: Optional[int] = None,
            prevent_guest_comment: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        Create a task from natural language input with automatic date/time extraction.

        This tool automatically extracts task title, description, and deadline from natural language input.
        It supports various date formats like:
        - "next Monday at 12PM"
        - "2025-05-01 01:30:00"
        - "after three days"
        - "tomorrow morning"
        - "Friday at midday"

        Args:
            org_id: Organization ID
            api_key: Tallyfy API key for authentication
            user_input: Natural language description of the task including deadline
            user_names: List of member names to assign the task to (optional)
            user_emails: List of member emails to assign the task to (optional)
            guest_emails: List of guest emails to assign the task to (optional)
            group_names: List of group names to assign the task to (optional)
            max_assignable: Maximum number of assignees (optional)
            prevent_guest_comment: Prevent guests from commenting (optional)

        Returns:
            Dict containing task object and extraction info

        Example:
            user_input: "Create a task called Review Document with description Review the quarterly report the deadline is next Monday at 12PM"

            This will extract:
            - Title: "Review Document"
            - Description: "Review the quarterly report"
            - Deadline: "2025-06-02 12:00:00" (parsed from "next Monday at 12PM")
        """
        try:
            # Extract task information from natural language input
            title, description, deadline = date_extractor.extract_task_info(user_input)

            if not title.strip():
                raise ValueError("Could not extract task title from input")

            if not deadline:
                raise ValueError(
                    "Could not extract deadline from input. Please include a deadline like 'due tomorrow', 'deadline is next Friday', or a specific date/time.")

            # Resolve user names and emails to user IDs
            user_ids = resolve_user_ids(org_id, user_names or [], user_emails or [])

            # Resolve group names to group IDs
            group_ids = resolve_group_ids(org_id, group_names or [])

            # Create TaskOwners object if any owners are specified
            owners = None
            if user_ids or guest_emails or group_ids:
                owners = TaskOwners(
                    users=user_ids or [],
                    guests=guest_emails or [],
                    groups=group_ids or []
                )

            # Create the task
            with TallyfySDK(api_key=api_key) as sdk:
                task = sdk.create_task(
                    org_id=org_id,
                    title=title.strip(),
                    description=description.strip() if description else None,
                    owners=owners,
                    deadline=deadline,
                    max_assignable=max_assignable,
                    prevent_guest_comment=prevent_guest_comment,
                )

            # Return task info along with extraction details
            result = {
                "task": task.__dict__ if task else {},
                "extraction_info": {
                    "original_input": user_input,
                    "extracted_title": title.strip(),
                    "extracted_description": description.strip() if description else None,
                    "extracted_deadline": deadline,
                    "assigned_users": user_ids,
                    "assigned_guests": guest_emails or [],
                    "assigned_groups": group_ids
                }
            }

            return result

        except TallyfyError as e:
            raise Exception(f"Failed to create task: {e}")
        except ValueError as e:
            raise Exception(f"Invalid input: {e}")
        except Exception as e:
            raise Exception(f"Error processing task creation: {e}")