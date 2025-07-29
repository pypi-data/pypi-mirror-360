"""
Form Field Management Tools
Tools for managing form fields in templates
"""

from typing import List, Dict, Any, Optional
from tallyfy import TallyfySDK, TallyfyError


def register_form_field_tools(mcp):
    """Register all form field management tools with the MCP server"""

    @mcp.tool()
    def add_form_field_to_step(org_id: str, api_key: str, template_id: str, step_id: str, field_data: Dict[str, Any]) -> Dict[
        str, Any]:
        """
        Add form fields (text, dropdown, date, etc.) to a step.

        Args:
            org_id: Organization ID
            api_key: Tallyfy API key for authentication
            template_id: Template ID
            step_id: Step ID
            field_data: Form field creation data including field_type, label, required, etc.

        Returns:
            Created form field object
        """
        try:
            with TallyfySDK(api_key=api_key) as sdk:
                result = sdk.add_form_field_to_step(org_id, template_id, step_id, field_data)
                return result.__dict__ if result else {}
        except TallyfyError as e:
            raise Exception(f"Failed to add form field to step: {e}")
        except ValueError as e:
            raise Exception(f"Invalid input: {e}")

    # TODO Fix kwargs issue
    # @mcp.tool()
    # def update_form_field(org_id: str, api_key: str, template_id: str, step_id: str, field_id: str, **kwargs) -> Dict[str, Any]:
    #     """
    #     Update form field properties, validation, options.
    #
    #     Args:
    #         org_id: Organization ID
    #         api_key: Tallyfy API key for authentication
    #         template_id: Template ID
    #         step_id: Step ID
    #         field_id: Form field ID
    #         **kwargs: Form field properties to update (field_type, label, required, options, etc.)
    #
    #     Returns:
    #         Updated form field object
    #     """
    #     try:
    #         with TallyfySDK(api_key=api_key) as sdk:
    #             result = sdk.update_form_field(org_id, template_id, step_id, field_id, **kwargs)
    #             return result.__dict__ if result else {}
    #     except TallyfyError as e:
    #         raise Exception(f"Failed to update form field: {e}")
    #     except ValueError as e:
    #         raise Exception(f"Invalid input: {e}")

    @mcp.tool()
    def move_form_field(org_id: str, api_key: str, template_id: str, from_step: str, field_id: str, to_step: str,
                        position: int = 1) -> bool:
        """
        Move form field between steps.

        Args:
            org_id: Organization ID
            api_key: Tallyfy API key for authentication
            template_id: Template ID
            from_step: Source step ID
            field_id: Form field ID to move
            to_step: Target step ID
            position: Position in target step (default: 1)

        Returns:
            True if move was successful
        """
        try:
            with TallyfySDK(api_key=api_key) as sdk:
                result = sdk.move_form_field(org_id, template_id, from_step, field_id, to_step, position)
                return result
        except TallyfyError as e:
            raise Exception(f"Failed to move form field: {e}")
        except ValueError as e:
            raise Exception(f"Invalid input: {e}")

    @mcp.tool()
    def delete_form_field(org_id: str, api_key: str, template_id: str, step_id: str, field_id: str) -> bool:
        """
        Delete a form field from a step.

        Args:
            org_id: Organization ID
            api_key: Tallyfy API key for authentication
            template_id: Template ID
            step_id: Step ID
            field_id: Form field ID

        Returns:
            True if deletion was successful
        """
        try:
            with TallyfySDK(api_key=api_key) as sdk:
                result = sdk.delete_form_field(org_id, template_id, step_id, field_id)
                return result
        except TallyfyError as e:
            raise Exception(f"Failed to delete form field: {e}")
        except ValueError as e:
            raise Exception(f"Invalid input: {e}")

    @mcp.tool()
    def get_dropdown_options(org_id: str, api_key: str, template_id: str, step_id: str, field_id: str) -> List[str]:
        """
        Get current dropdown options for analysis.

        Args:
            org_id: Organization ID
            api_key: Tallyfy API key for authentication
            template_id: Template ID
            step_id: Step ID
            field_id: Form field ID

        Returns:
            List of dropdown option strings
        """
        try:
            with TallyfySDK(api_key=api_key) as sdk:
                result = sdk.get_dropdown_options(org_id, template_id, step_id, field_id)
                return result
        except TallyfyError as e:
            raise Exception(f"Failed to get dropdown options: {e}")
        except ValueError as e:
            raise Exception(f"Invalid input: {e}")

    @mcp.tool()
    def update_dropdown_options(org_id: str, api_key: str, template_id: str, step_id: str, field_id: str, options: List[str]) -> bool:
        """
        Update dropdown options (for external data integration).

        Args:
            org_id: Organization ID
            api_key: Tallyfy API key for authentication
            template_id: Template ID
            step_id: Step ID
            field_id: Form field ID
            options: List of new option strings

        Returns:
            True if the update was successful
        """
        try:
            with TallyfySDK(api_key=api_key) as sdk:
                result = sdk.update_dropdown_options(org_id, template_id, step_id, field_id, options)
                return result
        except TallyfyError as e:
            raise Exception(f"Failed to update dropdown options: {e}")
        except ValueError as e:
            raise Exception(f"Invalid input: {e}")

    @mcp.tool()
    def suggest_form_fields_for_step(org_id: str, api_key: str, template_id: str, step_id: str) -> List[Dict[str, Any]]:
        """
        AI-powered suggestions for relevant form fields based on step content.

        Args:
            org_id: Organization ID
            api_key: Tallyfy API key for authentication
            template_id: Template ID
            step_id: Step ID to analyze

        Returns:
            List of suggested form field configurations with confidence scores and reasoning
        """
        try:
            with TallyfySDK(api_key=api_key) as sdk:
                result = sdk.suggest_form_fields_for_step(org_id, template_id, step_id)
                return result
        except TallyfyError as e:
            raise Exception(f"Failed to suggest form fields: {e}")
        except ValueError as e:
            raise Exception(f"Invalid input: {e}")

