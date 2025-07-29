"""
Template Management Tools
Tools for managing templates, steps, and template health
"""

from typing import List, Dict, Any, Optional
from tallyfy import TallyfySDK, TallyfyError


def register_template_management_tools(mcp):
    """Register all template management tools with the MCP server"""

    @mcp.tool()
    def get_template(
            org_id: str, api_key: str, template_id: Optional[str] = None, template_name: Optional[str] = None) -> Dict[str, Any]:
        """
            Get a template (checklist) by its ID or name with full details including prerun fields,
            automated actions, linked tasks, and metadata.

            Args:
                org_id: Organization ID
                api_key: Tallyfy API key for authentication
                template_id: Template (checklist) ID
                template_name: Template (checklist) name

            Returns:
                Template object with complete template data

            Raises:
                TallyfyError: If the request fails
            """
        try:
            with TallyfySDK(api_key=api_key) as sdk:
                if template_name and not template_id:
                    template = sdk.get_template(org_id, template_name=template_name)
                    return template.__dict__ if template else {}
                elif template_id and not template_name:
                    template = sdk.get_template(org_id, template_id=template_id)
                    return template.__dict__ if template else {}
                return {}
        except TallyfyError as e:
            raise Exception(f"Failed to invite user to organization: {e}")
        except ValueError as e:
            raise Exception(f"Invalid input: {e}")

    @mcp.tool()
    def get_step_dependencies(org_id: str, api_key: str, template_id: str, step_id: str) -> Dict[str, Any]:
        """
        Analyze which automations affect when this step appears.

        Args:
            org_id: Organization ID
            api_key: Tallyfy API key for authentication
            template_id: Template ID
            step_id: Step ID to analyze

        Returns:
            Dictionary containing dependency analysis with:
            - step_info: Basic step information
            - automation_rules: List of automations that affect this step
            - dependencies: List of conditions that must be met for step to show
            - affected_by: List of other steps/fields that influence this step's visibility
        """
        try:
            with TallyfySDK(api_key=api_key) as sdk:
                result = sdk.get_step_dependencies(org_id, template_id, step_id)
                return result
        except TallyfyError as e:
            raise Exception(f"Failed to analyze step dependencies: {e}")
        except ValueError as e:
            raise Exception(f"Invalid input: {e}")

    @mcp.tool()
    def suggest_step_deadline(org_id: str, api_key: str, template_id: str, step_id: str) -> Dict[str, Any]:
        """
        Suggest reasonable deadline based on step type and complexity.

        Args:
            org_id: Organization ID
            api_key: Tallyfy API key for authentication
            template_id: Template ID
            step_id: Step ID to analyze

        Returns:
            Dictionary containing deadline suggestions with:
            - step_info: Basic step information
            - suggested_deadline: Recommended deadline configuration
            - reasoning: Explanation for the suggestion
            - alternatives: Other deadline options
        """
        try:
            with TallyfySDK(api_key=api_key) as sdk:
                result = sdk.suggest_step_deadline(org_id, template_id, step_id)
                return result
        except TallyfyError as e:
            raise Exception(f"Failed to suggest step deadline: {e}")
        except ValueError as e:
            raise Exception(f"Invalid input: {e}")

    @mcp.tool()
    def add_assignees_to_step(org_id: str, api_key: str, template_id: str, step_id: str, assignees: dict[str, Any]) -> dict[str, Any]:
        """
        Add assignees to a specific step in a template.

        Args:
            org_id: Organization ID
            api_key: Tallyfy API key for authentication
            template_id: Template ID
            step_id: Step ID to add assignees to
            assignees: Dictionary containing assignee data with users and guests
                Expected format: {
                    'assignees': [user_id1, user_id2, ...],  # List of user IDs
                    'guests': [guest_email1, guest_email2, ...]  # List of guest emails
                }

        Returns:
            Dictionary containing updated step information
        """
        try:
            with TallyfySDK(api_key=api_key) as sdk:
                result = sdk.add_assignees_to_step(org_id, template_id, step_id, assignees)
                return result
        except TallyfyError as e:
            raise Exception(f"Failed to add assignees to step: {e}")
        except ValueError as e:
            raise Exception(f"Invalid input: {e}")

    @mcp.tool()
    def edit_description_on_step(org_id: str, api_key: str, template_id: str, step_id: str, description: str) -> dict[str, Any]:
        """
        Edit the description/summary of a specific step in a template.

        Args:
            org_id: Organization ID
            api_key: Tallyfy API key for authentication
            template_id: Template ID
            step_id: Step ID to edit description for
            description: New description/summary text for the step

        Returns:
            Dictionary containing updated step information
        """
        try:
            with TallyfySDK(api_key=api_key) as sdk:
                result = sdk.edit_description_on_step(org_id, template_id, step_id, description)
                return result
        except TallyfyError as e:
            raise Exception(f"Failed to edit step description: {e}")
        except ValueError as e:
            raise Exception(f"Invalid input: {e}")

    @mcp.tool()
    def add_step_to_template(org_id: str, api_key: str, template_id: str, step_data: dict[str, Any]) -> dict[str, Any]:
        """
        Add a new step to a template.

        Args:
            org_id: Organization ID
            api_key: Tallyfy API key for authentication
            template_id: Template ID
            step_data: Dictionary containing step data including title, summary, position, etc.
                Expected format: {
                    'title': 'Step title',
                    'summary': 'Step description (optional)',
                    'position': 1,  # Position in workflow (optional, defaults to end)
                    'step_type': 'task',  # Optional: 'task', 'decision', 'form', etc.
                    'allow_guest_owners': False,  # Optional: allow guest assignees
                    'max_assignable': 1,  # Optional: max number of assignees
                    'skip_start_process': False,  # Optional: skip when starting process
                    'can_complete_only_assignees': False,  # Optional: only assignees can complete
                    'everyone_must_complete': False,  # Optional: all assignees must complete
                    'webhook': 'url',  # Optional: webhook URL
                    'prevent_guest_comment': False,  # Optional: prevent guest comments
                    'is_soft_start_date': True,  # Optional: soft start date
                    'assignees': [123, 456],  # Optional: list of user IDs
                    'guests': ['email@example.com'],  # Optional: list of guest emails
                    'roles': ['Project Manager'],  # Optional: list of roles
                    'role_changes_every_time': True  # Optional: role changes each time
                }

        Returns:
            Dictionary containing created step information
        """
        try:
            with TallyfySDK(api_key=api_key) as sdk:
                result = sdk.add_step_to_template(org_id, template_id, step_data)
                return result
        except TallyfyError as e:
            raise Exception(f"Failed to add step to template: {e}")
        except ValueError as e:
            raise Exception(f"Invalid input: {e}")

    @mcp.tool()
    def suggest_kickoff_fields(org_id: str, api_key: str, template_id: str) -> list[dict[str, Any]]:
        """
        Suggest relevant kickoff fields based on template analysis.

        Args:
            org_id: Organization ID
            api_key: Tallyfy API key for authentication
            template_id: Template ID

        Returns:
            List of suggested kickoff field configurations with reasoning
        """
        try:
            with TallyfySDK(api_key=api_key) as sdk:
                result = sdk.suggest_kickoff_fields(org_id, template_id)
                return result
        except TallyfyError as e:
            raise Exception(f"Failed to suggest kickoff fields: {e}")
        except ValueError as e:
            raise Exception(f"Invalid input: {e}")

    @mcp.tool()
    def assess_template_health(org_id: str, api_key: str, template_id: str) -> dict[str, Any]:
        """
        Comprehensive template health check analyzing multiple aspects.

        This tool performs a complete health assessment of a template, evaluating:
        - Step title clarity and descriptiveness
        - Form field completeness and quality
        - Automation efficiency and conflicts
        - Deadline reasonableness for workflow steps
        - Overall workflow logic and structure
        - Template metadata quality

        Args:
            org_id: Organization ID
            api_key: Tallyfy API key for authentication
            template_id: Template ID to assess

        Returns:
            Dictionary containing:
            - overall_health_score: Score from 0-100
            - health_rating: Text rating (excellent/good/fair/poor/critical)
            - health_categories: Breakdown by category with individual scores
            - issues: List of identified problems with severity levels
            - recommendations: Improvement suggestions with priorities
            - improvement_plan: Prioritized action items for enhancement
            - assessment_details: Template information and analysis timestamp
        """
        try:
            with TallyfySDK(api_key=api_key) as sdk:
                result = sdk.assess_template_health(org_id, template_id)
                return result
        except TallyfyError as e:
            raise Exception(f"Failed to assess template health: {e}")
        except ValueError as e:
            raise Exception(f"Invalid input: {e}")