"""
Automation Tools
Tools for managing template automation rules and analysis
"""

from typing import List, Dict, Any, Optional
from tallyfy import TallyfySDK, TallyfyError


def register_automation_tools(mcp):
    """Register all automation tools with the MCP server"""

    @mcp.tool()
    def create_automation_rule(org_id: str, api_key: str, template_id: str, automation_data: dict) -> dict[str, Any]:
        """
        Create conditional automation (if-then rules).

        Args:
            org_id: Organization ID
            api_key: Tallyfy API key for authentication
            template_id: Template ID
            automation_data: Dictionary containing automation rule data with conditions and actions

        Returns:
            Created AutomatedAction object data
        """
        try:
            with TallyfySDK(api_key=api_key) as sdk:
                result = sdk.create_automation_rule(org_id, template_id, automation_data)
                return result.__dict__ if result else {}
        except TallyfyError as e:
            raise Exception(f"Failed to create automation rule: {e}")
        except ValueError as e:
            raise Exception(f"Invalid input: {e}")

    # TODO Fix kwargs issue
    # @mcp.tool()
    # def update_automation_rule(org_id: str, api_key: str, template_id: str, automation_id: str, **kwargs) -> dict[str, Any]:
    #     """
    #     Modify automation conditions and actions.
    #
    #     Args:
    #         org_id: Organization ID
    #         api_key: Tallyfy API key for authentication
    #         template_id: Template ID
    #         automation_id: Automation rule ID
    #         **kwargs: Automation fields to update
    #
    #     Returns:
    #         Updated AutomatedAction object data
    #     """
    #     try:
    #         with TallyfySDK(api_key=api_key) as sdk:
    #             result = sdk.update_automation_rule(org_id, template_id, automation_id, **kwargs)
    #             return result.__dict__ if result else {}
    #     except TallyfyError as e:
    #         raise Exception(f"Failed to update automation rule: {e}")
    #     except ValueError as e:
    #         raise Exception(f"Invalid input: {e}")

    @mcp.tool()
    def delete_automation_rule(org_id: str, api_key: str, template_id: str, automation_id: str) -> bool:
        """
        Remove an automation rule.

        Args:
            org_id: Organization ID
            api_key: Tallyfy API key for authentication
            template_id: Template ID
            automation_id: Automation rule ID

        Returns:
            True if deletion was successful
        """
        try:
            with TallyfySDK(api_key=api_key) as sdk:
                result = sdk.delete_automation_rule(org_id, template_id, automation_id)
                return result
        except TallyfyError as e:
            raise Exception(f"Failed to delete automation rule: {e}")
        except ValueError as e:
            raise Exception(f"Invalid input: {e}")

    @mcp.tool()
    def analyze_template_automations(org_id: str, api_key: str, template_id: str) -> dict[str, Any]:
        """
        Analyze all automations for conflicts, redundancies, and optimization opportunities.

        Args:
            org_id: Organization ID
            api_key: Tallyfy API key for authentication
            template_id: Template ID

        Returns:
            Dictionary containing automation analysis with conflicts, redundancies, and optimization suggestions
        """
        try:
            with TallyfySDK(api_key=api_key) as sdk:
                result = sdk.analyze_template_automations(org_id, template_id)
                return result
        except TallyfyError as e:
            raise Exception(f"Failed to analyze template automations: {e}")
        except ValueError as e:
            raise Exception(f"Invalid input: {e}")

    @mcp.tool()
    def consolidate_automation_rules(org_id: str, api_key: str, template_id: str, preview: bool = True) -> dict[str, Any]:
        """
        Suggest and optionally implement automation consolidation.

        Args:
            org_id: Organization ID
            api_key: Tallyfy API key for authentication
            template_id: Template ID
            preview: If True, only suggest changes without implementing (default: True)

        Returns:
            Dictionary containing consolidation suggestions and results
        """
        try:
            with TallyfySDK(api_key=api_key) as sdk:
                result = sdk.consolidate_automation_rules(org_id, template_id, preview)
                return result
        except TallyfyError as e:
            raise Exception(f"Failed to consolidate automation rules: {e}")
        except ValueError as e:
            raise Exception(f"Invalid input: {e}")

    @mcp.tool()
    def get_step_visibility_conditions(org_id: str, api_key: str, template_id: str, step_id: str ) -> Dict[str, Any]:
        """
            Analyze when/how a step becomes visible based on all automations.

            Args:
                org_id: Organization ID
                api_key: Tallyfy API key for authentication
                template_id: Template ID
                step_id: Step ID to analyze

            Returns:
                Dictionary containing step visibility analysis with rules and logic
            """
        try:
            with TallyfySDK(api_key=api_key) as sdk:
                result = sdk.get_step_visibility_conditions(org_id, template_id, step_id)
                return result
        except TallyfyError as e:
            raise Exception(f"Failed to analyze step visibility conditions: {e}")
        except ValueError as e:
            raise Exception(f"Invalid input: {e}")

    @mcp.tool()
    def suggest_automation_consolidation(org_id: str, api_key: str, template_id: str) -> list[dict[str, Any]]:
        """
        AI analysis of automation rules with consolidation recommendations.

        Args:
            org_id: Organization ID
            api_key: Tallyfy API key for authentication
            template_id: Template ID

        Returns:
            List of consolidation recommendations with detailed analysis and priority levels
        """
        try:
            with TallyfySDK(api_key=api_key) as sdk:
                result = sdk.suggest_automation_consolidation(org_id, template_id)
                return result
        except TallyfyError as e:
            raise Exception(f"Failed to suggest automation consolidation: {e}")
        except ValueError as e:
            raise Exception(f"Invalid input: {e}")
