# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **MCP (Model Context Protocol) WebSocket Server** that provides multi-user access to Tallyfy workflow automation. The repository implements a sophisticated solution to MCP's fundamental limitation of not supporting multi-user scenarios by default, creating a session-based proxy layer that enables secure, isolated access for multiple concurrent users.

### Core Architecture

The system consists of three interconnected components:

- **MCP Server** (`/server`): FastMCP 2.9.0-based server exposing 40+ Tallyfy SDK functions as MCP tools
- **WebSocket Host** (`/host`): Multi-user WebSocket server managing client connections and session isolation
- **Tallyfy SDK** (`/tallyfy`): Comprehensive Python SDK (v1.0.2) for Tallyfy API integration

### Repository Context

This repository is part of Tallyfy's broader ecosystem, working alongside:
- `api-v2/`: Laravel-based main API (443.198.69.152)
- `client/`: Angular frontend application  
- `documentation/`: User documentation
- `cloudflare-workers/`: Distributed edge computing services
- `systems/`: Infrastructure automation tools

### Problem Statement

The repository specifically addresses the multi-user challenge described in GitHub issue regarding MCP's single-client limitation (referenced from MCP TypeScript SDK issues #204, #243). The solution implements session-based authentication and credential isolation to enable multi-tenant MCP access.

## Common Development Commands

### Running the System

```bash
# Install dependencies
pip install -r requirements.txt

# Start the MCP server (runs on port 9000)
python -m server.server

# Start the WebSocket server (runs on port 9001)
python run_websocket_server.py

# For development with debug logging
python run_websocket_server.py --debug
```

### Code Quality

```bash
# Format code with Black
black . --line-length 88

# Type checking with mypy
mypy . --python-version 3.7

# Linting with flake8
flake8 .

# Run tests (when available)
pytest tests/
```

### Docker Commands

```bash
# Build and run MCP server
cd server && docker-compose up --build

# Build and run WebSocket host
cd host && docker-compose up --build
```

## Architecture & Key Components

### MCP Server Tools (`/server/tools/`)

The server provides 40+ tools organized by domain:

1. **User Management**: Organization members/guests, invitations
2. **Task Management**: Create, retrieve, and manage tasks with NLP date extraction
3. **Process Management**: Manage workflow processes (runs)
4. **Template Management**: Create/edit templates, steps, and health analysis
5. **Form Fields**: Add/manage form fields on steps
6. **Search**: Find tasks, processes, and templates
7. **Automation**: Create/manage if-then rules and analyze automations

### WebSocket Architecture

```
Web Clients → WebSocket Server → Session Manager → MCP Client → Tallyfy API
```

Key features:
- Per-session authentication with user's Tallyfy credentials
- Isolated credential storage (memory only, no persistence)
- 60-minute session timeout
- Real-time bidirectional communication

### Authentication Flow

1. Client connects to WebSocket
2. Client sends auth message with Tallyfy API key and org ID
3. Server creates isolated session with credentials
4. All subsequent queries use session's credentials
5. Credentials cleared on disconnect/timeout

## Important Patterns

### Tool Parameter Pattern

All MCP tools follow this pattern:
```python
@mcp.tool()
async def tool_name(api_key: str, org_id: str, other_params...):
    """Tool description"""
    client = Tallyfy(api_key=api_key, org_id=org_id)
    # Implementation
```

### Error Handling

- Tools raise `TallyfyError` for API errors
- WebSocket server catches and forwards errors to clients
- Comprehensive logging throughout

### Date Extraction

The `DateExtractor` class in `tools/date_utils.py` handles natural language dates:
- Multiple parsing strategies (dateparser, manual patterns)
- Common time expressions (noon, midnight, morning)
- Task info extraction from text

## Deployment

Automated deployment via GitHub Actions:
- `.github/workflows/deploy-server.yml` - Deploys MCP server
- `.github/workflows/deploy-host.yml` - Deploys WebSocket host
- Target: DigitalOcean droplet (143.198.69.152)

## Environment Variables

Required:
- `ANTHROPIC_API_KEY` - For Claude API access
- `TALLYFY_API_KEY` - Fallback Tallyfy API key (users provide their own)
- `TALLYFY_ORG_ID` - Fallback organization ID

Optional:
- `MCP_SERVER_URL` - MCP server endpoint (default: http://127.0.0.1:9000/mcp/)

## Security Considerations

- Per-session authentication required
- No credential persistence (memory only)
- Environment variables for server config only
- Input validation on all messages
- Session isolation for multi-tenancy

## AI-Driven Automation Approach

This codebase supports automated Claude Code workflows for breaking down large tasks into manageable units. Use this approach for complex operations like bulk documentation, refactoring, or systematic updates.

### Non-Interactive Execution Pattern

Execute Claude tasks without human intervention:
```bash
claude -p "YOUR_PROMPT_HERE" --dangerously-skip-permissions
```

### File-Based Task Queue

For large projects, break work into atomic tasks using a file-based queue:

1. **Create task queue directory**:
```bash
mkdir automation_queue
```

2. **Generate prompt files** (numbered for ordering):
```
automation_queue/
├── 001_analyze_tools.prompt
├── 002_document_user_tools.prompt
├── 003_document_task_tools.prompt
└── 004_validate_docs.prompt
```

3. **Process queue with automatic cleanup**:
```python
#!/usr/bin/env python3
import subprocess
from pathlib import Path

queue_dir = Path("automation_queue")
for prompt_file in sorted(queue_dir.glob("*.prompt")):
    prompt = prompt_file.read_text().strip()
    cmd = ["claude", "-p", prompt, "--dangerously-skip-permissions"]
    
    if subprocess.run(cmd).returncode == 0:
        prompt_file.unlink()  # Delete completed task
        print(f"✓ Completed: {prompt_file.name}")
    else:
        print(f"✗ Failed: {prompt_file.name}")
        break
```

### Example Automation Patterns

**Bulk Documentation**:
```bash
# Generate documentation for all server tools
for tool in server/tools/*.py; do
    claude -p "Add comprehensive docstrings to all functions in $tool following NumPy style" --dangerously-skip-permissions
done
```

**Systematic Refactoring**:
```bash
# Refactor to async patterns
claude -p "Convert synchronous Tallyfy SDK calls in server/tools/user_management.py to async patterns" --dangerously-skip-permissions
```

**Test Generation**:
```bash
# Create test files for each tool module
claude -p "Generate comprehensive pytest tests for server/tools/task_management.py covering all edge cases" --dangerously-skip-permissions
```

### Best Practices for Automation

1. **Atomic Tasks**: Each prompt should complete one specific objective
2. **Clear File References**: Always use absolute paths in prompts
3. **Validation Steps**: Include verification after generation tasks
4. **Sequential Dependencies**: Number files to control execution order
5. **State Isolation**: Each task runs independently without shared state

### When to Use Automation

- Bulk updates across multiple files
- Systematic documentation efforts
- Large-scale refactoring projects
- Test suite generation
- Code migration tasks

This approach enables handling projects that would take days manually in hours through automated, methodical execution.

## Technical Deep Dive

### FastMCP Framework Integration

This repository implements FastMCP 2.0, the actively maintained framework for MCP development:

#### Tool Registration Pattern
```python
@mcp.tool()
async def tool_name(api_key: str, org_id: str, other_params...):
    """Tool description following NumPy docstring convention"""
    client = Tallyfy(api_key=api_key, org_id=org_id)
    # Implementation with proper error handling
    return result
```

#### Resource Management
The server exposes data through MCP Resources for LLM context injection, following the pattern:
```python
@mcp.resource("tallyfy://resource-name")
def get_resource() -> str:
    """Resource description"""
    return structured_data
```

### Multi-User Session Architecture

#### Session Isolation Model
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Clients   │    │  WebSocket      │    │   MCP Client    │
│   (Multiple)    │◄──►│     Server      │◄──►│   (Shared)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │ Session Manager │
                       │ (Per-user conv) │
                       └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │ Credential Store│
                       │ (Memory Only)   │
                       └─────────────────┘
```

#### Critical Session Management Patterns

**Session Creation**:
- UUID-based session IDs
- JWT token parsing for user identification 
- Credential verification via Tallyfy API before storage
- 60-minute automatic timeout

**Security Features**:
- Per-session credential isolation
- No persistent credential storage (memory only)
- Real-time credential validation
- Session-scoped conversation history

### Dependencies & Frameworks

#### Core Dependencies
- `fastmcp==2.9.0`: MCP server framework (production-ready with extensive features)
- `mcp[cli]==1.9.4`: Official MCP client libraries
- `anthropic==0.52.2`: Claude API integration for LLM operations
- `websockets==11.0.3`: Real-time bidirectional communication
- `tallyfy==1.0.2`: Workflow automation SDK

#### Supporting Libraries
- `dateparser==1.2.1`: Natural language date extraction
- `PyJWT>=2.8.0`: JWT token parsing and validation
- `fastapi==0.115.12`: HTTP API framework (for admin tools)
- `uvicorn==0.23.2`: ASGI server
- `python-dotenv==1.1.0`: Environment configuration
- `markdown>=3.4.0`: Response formatting for web clients

### Tool Categories & Implementation

#### 1. User Management Tools (`/server/tools/user_management.py`)
- Organization member/guest management
- User invitation and role assignment
- Profile data retrieval and updates
- Permission validation

#### 2. Task Management Tools (`/server/tools/task_management.py`)
- Task creation with NLP date extraction
- Assignment and ownership management
- Status tracking and updates
- Search and filtering capabilities

#### 3. Process Management Tools (`/server/tools/process_management.py`)
- Workflow instance (run) management
- Process status monitoring
- Execution control and automation

#### 4. Template Management Tools (`/server/tools/template_management.py`)
- Blueprint creation and modification
- Step management and dependencies
- Health assessment and optimization
- Version control and duplication

#### 5. Form Field Tools (`/server/tools/form_fields.py`)
- Dynamic form field creation
- Validation rule management
- Dropdown option updates
- Field positioning and layout

#### 6. Search Tools (`/server/tools/search.py`)
- Universal search across tasks, processes, templates
- Advanced filtering and sorting
- Performance-optimized queries

#### 7. Automation Tools (`/server/tools/automation.py`)
- Conditional rule creation (if-then logic)
- Automation analysis and optimization
- Rule consolidation and conflict detection

### Error Handling Patterns

#### Tallyfy API Error Handling
```python
try:
    with TallyfySDK(api_key=api_key) as sdk:
        result = sdk.api_method(org_id, params)
        return result
except TallyfyError as e:
    logger.error(f"Tallyfy API error: {e}")
    raise TallyfyError(f"Operation failed: {e}")
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise Exception(f"Unexpected error: {e}")
```

#### WebSocket Error Handling
- Graceful connection cleanup
- Session state preservation
- Automatic reconnection support
- Comprehensive error logging

### Security Considerations & Vulnerabilities

#### MCP Security Landscape (2025)
Based on security research findings, this implementation addresses critical vulnerabilities:

**Prompt Injection Mitigation**:
- User approval required for all tool invocations (SHOULD treated as MUST)
- Input validation on all WebSocket messages
- Session-based credential verification

**Authentication Security**:
- JWT token validation without relying solely on signature verification
- Credential verification against Tallyfy API for each session
- Memory-only credential storage (no persistence)

**Session Security**:
- UUID-based session identifiers (not exposed in URLs)
- Session isolation preventing cross-user data access
- Automatic session cleanup after 60 minutes

#### Known MCP Vulnerabilities to Monitor
- Tool poisoning and "rug pull" attacks (tool definitions changing post-approval)
- Indirect prompt injection through external content
- Command injection in tool implementations (43% of open-source MCP servers affected)
- Cross-session data leakage

### Performance & Scaling Patterns

#### Connection Management
- Ping/pong heartbeat for connection health (30s interval, 10s timeout)
- Automatic cleanup of inactive sessions (5-minute intervals)
- Resource pooling for Tallyfy SDK instances

#### Memory Management
- Session-scoped conversation history
- Periodic cleanup of abandoned sessions
- Efficient JSON parsing and response caching

### Integration with Tallyfy Ecosystem

#### API Integration Patterns
```python
# Idempotent request pattern
headers = {
    "Authorization": f"Bearer {api_key}",
    "X-Tallyfy-Client": "APIClient",  # Required header
    "Content-Type": "application/json"
}

# Retry logic with exponential backoff
@retry_with_backoff(max_retries=3)
def make_tallyfy_request(endpoint, data):
    response = requests.post(f"{BASE_URL}/{endpoint}", headers=headers, json=data)
    if response.status_code == 429:  # Rate limiting
        retry_after = int(response.headers.get("Retry-After", 60))
        time.sleep(retry_after)
    return response
```

#### Webhook Integration Support
- Event-driven automation triggers
- Idempotency key management
- Batch operation handling

### Deployment Architecture

#### Production Environment
- **Target**: DigitalOcean droplet (143.198.69.152)
- **MCP Server**: Port 9000 (HTTP transport)
- **WebSocket Server**: Port 8765 (WebSocket transport)
- **Transport Support**: Both stdio and HTTP-SSE for maximum compatibility

#### GitHub Actions Deployment
- `.github/workflows/deploy-server.yml`: MCP server deployment
- `.github/workflows/deploy-host.yml`: WebSocket host deployment
- Automated testing and deployment pipeline

#### Environment Configuration
```bash
# Required for operation
ANTHROPIC_API_KEY="sk-ant-api03-..."  # Claude API access
TALLYFY_API_KEY="fallback-key"        # Fallback (users provide own)
TALLYFY_ORG_ID="fallback-org"         # Fallback organization

# Optional configuration
MCP_SERVER_URL="http://127.0.0.1:9000/mcp/"  # Internal MCP endpoint
```

### Testing & Quality Assurance

#### Code Quality Tools
```bash
# Formatting
black . --line-length 88

# Type checking (Python 3.7+ compatibility)
mypy . --python-version 3.7

# Linting
flake8 .

# Testing (when available)
pytest tests/
```

#### Integration Testing Patterns
- WebSocket connection testing
- Session management validation
- Tallyfy API integration verification
- Error handling scenario testing

### Version Control & Branching

#### Current Repository State
- **Main Branch**: `main` (default)
- **Recent Activity**: Recent commits include logging improvements, MCP server enhancements
- **Deployment**: Direct deployment from main branch

#### Development Patterns
- Single-branch development model
- Direct commits to main with immediate deployment
- Issue-driven development (3 open issues tracked)

### Monitoring & Observability

#### Logging Configuration
```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Suppress noisy logs
logging.getLogger('mcp.server.lowlevel.server').setLevel(logging.WARNING)
logging.getLogger('FastMCP.fastmcp.tools.tool_manager').setLevel(logging.FATAL)
```

#### Health Monitoring
- Connection status tracking
- Session statistics and cleanup reporting
- Tool invocation logging and error tracking
- Performance metrics for session management

### Development Best Practices

#### Tool Development Patterns
1. **Parameter Validation**: Always validate `api_key` and `org_id` before processing
2. **Error Handling**: Use `TallyfyError` for API-related errors, generic `Exception` for others
3. **Documentation**: Follow NumPy docstring conventions for all tools
4. **Resource Management**: Use context managers for Tallyfy SDK instances
5. **Testing**: Verify tool functionality against actual Tallyfy API

#### Session Management Guidelines
1. **Credential Isolation**: Never share credentials between sessions
2. **Validation**: Verify credentials with Tallyfy API before storage
3. **Cleanup**: Implement proper session cleanup and timeout handling
4. **Logging**: Log session events for debugging and monitoring

#### Security Implementation
1. **Input Validation**: Sanitize all user inputs before processing
2. **Authentication**: Verify user credentials for every session
3. **Authorization**: Implement proper role-based access control
4. **Audit Trail**: Log all significant operations for security monitoring