"""
Task and process management functionality for Tallyfy SDK
"""

from typing import List, Optional
from .models import Task, Run, SearchResult, TaskOwners, TallyfyError


class TaskManagement:
    """Handles task and process management operations"""
    
    def __init__(self, sdk):
        self.sdk = sdk

    def get_my_tasks(self, org_id: str) -> List[Task]:
        """
        Get all tasks assigned to the current user in the organization.

        Args:
            org_id: Organization ID

        Returns:
            List of Task objects assigned to the current user

        Raises:
            TallyfyError: If the request fails
        """
        try:
            endpoint = f"organizations/{org_id}/me/tasks"
            response_data = self.sdk._make_request('GET', endpoint)

            if isinstance(response_data, dict) and 'data' in response_data:
                tasks_data = response_data['data']
                return [Task.from_dict(task_data) for task_data in tasks_data]
            else:
                if isinstance(response_data, list):
                    return [Task.from_dict(task_data) for task_data in response_data]
                else:
                    self.sdk.logger.warning("Unexpected response format for tasks")
                    return []

        except TallyfyError as e:
            self.sdk.logger.error(f"Failed to get my tasks for org {org_id}: {e}")
            raise

    def get_user_tasks(self, org_id: str, user_id: int) -> List[Task]:
        """
        Get all tasks assigned to the given user in the organization.

        Args:
            org_id: Organization ID
            user_id: User ID

        Returns:
            List of Task objects assigned to the given user ID

        Raises:
            TallyfyError: If the request fails
        """
        try:
            endpoint = f"organizations/{org_id}/users/{user_id}/tasks?per_page=100&sort_by=newest&status=all&with=run,threads_count,step,tags,folders,member_watchers.watcher"
            response_data = self.sdk._make_request('GET', endpoint)

            if isinstance(response_data, dict) and 'data' in response_data:
                tasks_data = response_data['data']
                return [Task.from_dict(task_data) for task_data in tasks_data]
            else:
                if isinstance(response_data, list):
                    return [Task.from_dict(task_data) for task_data in response_data]
                else:
                    self.sdk.logger.warning("Unexpected response format for tasks")
                    return []

        except TallyfyError as e:
            self.sdk.logger.error(f"Failed to get user tasks for org {org_id}: {e}")
            raise

    def search_processes_by_name(self, org_id: str, process_name: str) -> str:
        """
        Search for processes by name using the search endpoint.

        Args:
            org_id: Organization ID
            process_name: Name or partial name of the process to search for

        Returns:
            Process ID of the found process

        Raises:
            TallyfyError: If no process found, multiple matches, or search fails
        """
        try:
            search_endpoint = f"organizations/{org_id}/search"
            search_params = {
                'on': 'process', 
                'per_page': '20',
                'search': process_name
            }
            
            search_response = self.sdk._make_request('GET', search_endpoint, params=search_params)
            
            if isinstance(search_response, dict) and 'process' in search_response:
                process_data = search_response['process']
                if 'data' in process_data and process_data['data']:
                    processes = process_data['data']
                    
                    # First try exact match (case-insensitive)
                    exact_matches = [p for p in processes if p['name'].lower() == process_name.lower()]
                    if exact_matches:
                        return exact_matches[0]['id']
                    elif len(processes) == 1:
                        # Single search result, use it
                        return processes[0]['id']
                    else:
                        # Multiple matches found, provide helpful error with options
                        match_names = [f"'{p['name']}'" for p in processes[:5]]  # Show max 5
                        raise TallyfyError(f"Multiple processes found matching '{process_name}': {', '.join(match_names)}. Please be more specific.")
                else:
                    raise TallyfyError(f"No process found matching name: {process_name}")
            else:
                raise TallyfyError(f"Search failed for process name: {process_name}")
                
        except TallyfyError as e:
            self.sdk.logger.error(f"Failed to search for process '{process_name}': {e}")
            raise

    def get_tasks_for_process(self, org_id: str, process_id: Optional[str] = None, process_name: Optional[str] = None) -> List[Task]:
        """
        Get all tasks for a given process (run).

        Args:
            org_id: Organization ID
            process_id: Process (run) ID to get tasks for
            process_name: Process (run) name to get tasks for (alternative to process_id)

        Returns:
            List of Task objects for the specified process

        Raises:
            TallyfyError: If the request fails
            ValueError: If neither process_id nor process_name is provided
        """
        if not process_id and not process_name:
            raise ValueError("Either process_id or process_name must be provided")
        
        try:
            # If process_name is provided but not process_id, search for the process first
            if process_name and not process_id:
                process_id = self.search_processes_by_name(org_id, process_name)
            
            endpoint = f"organizations/{org_id}/runs/{process_id}/tasks"
            response_data = self.sdk._make_request('GET', endpoint)

            if isinstance(response_data, dict) and 'data' in response_data:
                tasks_data = response_data['data']
                return [Task.from_dict(task_data) for task_data in tasks_data]
            else:
                if isinstance(response_data, list):
                    return [Task.from_dict(task_data) for task_data in response_data]
                else:
                    self.sdk.logger.warning("Unexpected response format for process tasks")
                    return []

        except TallyfyError as e:
            self.sdk.logger.error(f"Failed to get tasks for process {process_id or process_name}: {e}")
            raise

    def get_organization_runs(self, org_id: str, with_data: Optional[str] = None, 
                            form_fields_values: Optional[bool] = None,
                            owners: Optional[str] = None, task_status: Optional[str] = None,
                            groups: Optional[str] = None, status: Optional[str] = None,
                            folder: Optional[str] = None, checklist_id: Optional[str] = None,
                            starred: Optional[bool] = None, run_type: Optional[str] = None,
                            tag: Optional[str] = None) -> List[Run]:
        """
        Get all processes (runs) in the organization.

        Args:
            org_id: Organization ID
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
            List of Run objects

        Raises:
            TallyfyError: If the request fails
        """
        try:
            endpoint = f"organizations/{org_id}/runs"
            params = {}
            
            if with_data:
                params['with'] = with_data
            if form_fields_values is not None:
                params['form_fields_values'] = 'true' if form_fields_values else 'false'
            if owners:
                params['owners'] = owners
            if task_status:
                params['task_status'] = task_status
            if groups:
                params['groups'] = groups
            if status:
                params['status'] = status
            if folder:
                params['folder'] = folder
            if checklist_id:
                params['checklist_id'] = checklist_id
            if starred is not None:
                params['starred'] = starred
            if run_type:
                params['type'] = run_type
            if tag:
                params['tag'] = tag
            
            response_data = self.sdk._make_request('GET', endpoint, params=params)

            if isinstance(response_data, dict) and 'data' in response_data:
                runs_data = response_data['data']
                return [Run.from_dict(run_data) for run_data in runs_data]
            else:
                if isinstance(response_data, list):
                    return [Run.from_dict(run_data) for run_data in response_data]
                else:
                    self.sdk.logger.warning("Unexpected response format for runs")
                    return []

        except TallyfyError as e:
            self.sdk.logger.error(f"Failed to get organization runs for org {org_id}: {e}")
            raise

    def search(self, org_id: str, search_query: str, search_type: str = "process", per_page: int = 20) -> List[SearchResult]:
        """
        Search for processes, templates, or tasks in the organization.

        Args:
            org_id: Organization ID
            search_query: Text to search for
            search_type: Type of search - 'process', 'blueprint', or 'task' (default: 'process'). blueprint equals template
            per_page: Number of results per page (default: 20)

        Returns:
            List of SearchResult objects

        Raises:
            TallyfyError: If the request fails
            ValueError: If search_type is not valid
        """
        # Validate search type
        valid_types = ["process", "blueprint", "task"]
        if search_type not in valid_types:
            raise ValueError(f"Search type must be one of: {', '.join(valid_types)}")
        
        try:
            endpoint = f"organizations/{org_id}/search"
            params = {
                'on': search_type,
                'per_page': str(per_page),
                'search': search_query
            }
            
            response_data = self.sdk._make_request('GET', endpoint, params=params)
            
            if isinstance(response_data, dict) and search_type in response_data:
                search_data = response_data[search_type]
                if 'data' in search_data and search_data['data']:
                    results_data = search_data['data']
                    return [SearchResult.from_dict(result_data, search_type) for result_data in results_data]
                else:
                    self.sdk.logger.info(f"No {search_type} results found for query: {search_query}")
                    return []
            else:
                self.sdk.logger.warning(f"Unexpected response format for {search_type} search")
                return []

        except TallyfyError as e:
            self.sdk.logger.error(f"Failed to search {search_type} for query '{search_query}': {e}")
            raise

    def create_task(self, org_id: str, title: str, deadline: str,
                   owners: TaskOwners, description: Optional[str] = None,
                   max_assignable: Optional[int] = None, prevent_guest_comment: Optional[bool] = None) -> Optional[Task]:
        """
        Create a standalone task in the organization.

        Args:
            org_id: Organization ID
            title: Task name (required)
            deadline: Task deadline in "YYYY-mm-dd HH:ii:ss" format
            owners: TaskOwners object with users, guests, and groups
            description: Task description (optional)
            max_assignable: Maximum number of assignees (optional)
            prevent_guest_comment: Prevent guests from commenting (optional)

        Returns:
            Task object for the created task

        Raises:
            TallyfyError: If the request fails
            ValueError: If required parameters are missing
        """
        if not title:
            raise ValueError("Task title is required")

        # Validate that at least one assignee is provided
        if not owners or (not owners.users and not owners.guests and not owners.groups):
            raise ValueError("At least one assignee is required (users, guests, or groups)")

        try:
            endpoint = f"organizations/{org_id}/tasks"

            task_data = {
                "title": title
            }

            if description:
                task_data["description"] = description
            if owners:
                task_data["owners"] = {
                    "users": owners.users,
                    "guests": owners.guests,
                    "groups": owners.groups
                }
            if deadline:
                task_data["deadline"] = deadline
            if max_assignable is not None:
                task_data["max_assignable"] = max_assignable
            if prevent_guest_comment is not None:
                task_data["prevent_guest_comment"] = prevent_guest_comment

            task_data["task_type"] = "task"
            task_data["separate_task_for_each_assignee"] = True
            task_data["status"]= "not-started"
            task_data["everyone_must_complete"] = False
            task_data["is_soft_start_date"]= True
            response_data = self.sdk._make_request('POST', endpoint, data=task_data)

            if isinstance(response_data, dict) and 'data' in response_data:
                task_data = response_data['data']
                return Task.from_dict(task_data)
            else:
                self.sdk.logger.warning("Unexpected response format for task creation")
                return None

        except TallyfyError as e:
            self.sdk.logger.error(f"Failed to create task in organization {org_id}: {e}")
            raise