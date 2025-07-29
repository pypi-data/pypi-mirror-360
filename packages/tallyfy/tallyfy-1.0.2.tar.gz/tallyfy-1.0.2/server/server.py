"""
Tallyfy MCP Server
Exposes Tallyfy SDK functions as MCP tools for use with LLM applications
"""

import logging
from fastmcp import FastMCP

# Configure logging with timestamps for HTTP requests
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Suppress noisy logs
logging.getLogger('mcp.server.lowlevel.server').setLevel(logging.WARNING)
logging.getLogger('FastMCP.fastmcp.tools.tool_manager').setLevel(logging.FATAL)

from tools.user_management import register_user_management_tools
from tools.task_management import register_task_management_tools
from tools.process_management import register_process_management_tools
from tools.search import register_search_tools
from tools.template_management import register_template_management_tools
from tools.form_fields import register_form_field_tools
from tools.automation import register_automation_tools


# load_dotenv()  # load environment variables from .env

# def get_api_key() -> str:
#     """Get API key from environment"""
#     api_key = os.getenv('TALLYFY_API_KEY')
#     if not api_key:
#         raise TallyfyError("TALLYFY_API_KEY environment variable is required")
#     return api_key

# Resource for getting server status
# @mcp.resource("tallyfy://status")
# def get_server_status() -> str:
#     """Get the current status of the Tallyfy MCP server"""
#     try:
#         api_key = os.getenv('TALLYFY_API_KEY')
#         if not api_key:
#             return "❌ No API key configured. Set TALLYFY_API_KEY environment variable."
#
#         # Test SDK connection
#         with TallyfySDK(api_key=api_key) as sdk:
#             return "✅ Tallyfy MCP Server is running and API key is configured."
#     except Exception as e:
#         return f"❌ Server error: {e}"

mcp = FastMCP("Tallyfy MCP Server")


# Register all tool categories
register_user_management_tools(mcp)
register_task_management_tools(mcp)
register_process_management_tools(mcp)
register_search_tools(mcp)
register_template_management_tools(mcp)
register_form_field_tools(mcp)
register_automation_tools(mcp)



# Resource for listing available tools
@mcp.resource("tallyfy://tools")
def get_available_tools() -> str:
    """Get a list of all available Tallyfy tools"""
    tools = [
        "get_organization_users - Get all organization members with full profile data",
        "get_organization_users_list - Get organization members with minimal data",
        "get_organization_guests - Get organization guests with full profile data",
        "get_organization_guests_list - Get organization guests with minimal data",
        "invite_user_to_organization - Invite a member to your organization",
        "get_my_tasks - Get tasks assigned to the current user",
        "get_user_tasks - Get tasks assigned to a given user",
        "get_tasks_for_process - Get all tasks for a given process (run)",
        "get_organization_runs - Get all processes (runs) in the organization",
        "create_task_from_text - Create a standalone task in the organization from natural language with automatic date extraction",
        "search_for_tasks - Search for tasks in the organization",
        "search_for_processes - Search for processes in the organization",
        "search_for_templates - Search for templates in the organization",
        "get_template - Get a template (checklist) by its ID or name with full details including prerun fields, automated actions, linked tasks, and metadata",
        "get_step_dependencies - Analyze which automations affect when this step appears",
        "suggest_step_deadline - Suggest reasonable deadline based on step type and complexity",
        "add_form_field_to_step - Add form fields (text, dropdown, date, etc.) to a step",
        "move_form_field - Move form field between steps",
        "delete_form_field - Delete a form field from a step",
        "get_dropdown_options - Get current dropdown options for analysis",
        "update_dropdown_options - Update dropdown options (for external data integration)",
        "suggest_form_fields_for_step - AI-powered suggestions for relevant form fields based on step content",
        "create_automation_rule - Create conditional automation (if-then rules)",
        "delete_automation_rule - Remove an automation rule",
        "analyze_template_automations - Analyze all automations for conflicts, redundancies, and optimization opportunities",
        "consolidate_automation_rules - Suggest and optionally implement automation consolidation",
        "get_step_visibility_conditions - Analyze when/how a step becomes visible based on all automations",
        "suggest_automation_consolidation - AI analysis of automation rules with consolidation recommendations",
        "suggest_kickoff_fields - Suggest relevant kickoff fields based on template analysis",
        "assess_template_health - Comprehensive template health check analyzing multiple aspects",
        "add_assignees_to_step - Add assignees to a specific step in a template",
        "edit_description_on_step - Edit the description/summary of a specific step in a template",
        "add_step_to_template - Add a new step to a template",
        # "update_automation_rule - Modify automation conditions and actions", #TODO Fix kwargs issue
        # "update_form_field - Update form field properties, validation, options", #TODO Fix kwargs issue
        # "update_kickoff_field - Update kickoff field properties.", #TODO
        # "add_kickoff_field - Add kickoff/prerun fields to template.", #TODO
    ]
    return "\n".join(f"• {tool}" for tool in tools)


if __name__ == "__main__":
    # Run the MCP server
    mcp.run(transport="streamable-http", host="127.0.0.1", port=9000)