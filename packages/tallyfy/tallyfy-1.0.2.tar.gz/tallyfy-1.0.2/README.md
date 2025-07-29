# MCP WebSocket Server

A production-ready WebSocket server that enables multi-user access to the Model Context Protocol (MCP) for Tallyfy workflow automation. This repository solves a fundamental limitation of MCP by implementing secure, session-based multi-tenancy that allows multiple users to simultaneously access Tallyfy's workflow automation tools through AI assistants.

## About Tallyfy

[Tallyfy](https://tallyfy.com/) is an AI-powered workflow management platform that helps organizations automate and streamline their business processes. The company's mission is to "Run AI-powered operations and save 2 hours per person every day" by eliminating manual work and improving operational efficiency.

### Why This MCP Server Matters

The Model Context Protocol (MCP), introduced by Anthropic in 2024, standardizes how AI systems connect to external tools and data sources. However, MCP servers typically support only single-user scenarios. This repository addresses that limitation by providing a sophisticated proxy layer that enables:

- **Multi-tenant access**: Multiple users can simultaneously access Tallyfy through their AI assistants
- **Secure credential isolation**: Each user authenticates with their own Tallyfy credentials
- **Session management**: Isolated conversation contexts and automatic cleanup
- **Real-time communication**: WebSocket-based architecture for instant responses

## Features

### Core Capabilities
- **Multi-user Support**: Multiple clients can connect simultaneously with isolated sessions
- **40+ Workflow Tools**: Comprehensive access to Tallyfy's workflow automation features
- **Session Management**: Each connection gets its own conversation history and credentials
- **Real-time Communication**: WebSocket-based for instant responses with markdown formatting
- **Secure Authentication**: Per-session credential validation with Tallyfy API
- **Automatic Cleanup**: Inactive sessions are automatically cleaned up after 60 minutes

### Available Workflow Tools

#### 📋 Task Management
- Create tasks from natural language with automatic date extraction
- Assign tasks to users and manage ownership
- Search and filter tasks across your organization
- Track task status and progress

#### 🔄 Process Management  
- Launch and manage workflow processes (runs)
- Monitor process status and execution
- Access process data and metadata
- Control workflow automation

#### 📝 Template Management
- Create and edit workflow templates (blueprints)
- Manage template steps and dependencies
- Perform health assessments and optimization
- Duplicate and version control templates

#### 👥 User Management
- Manage organization members and guests
- Send user invitations with role assignments
- Retrieve user profiles and permissions
- Handle user authentication and access control

#### 📊 Form Fields & Data
- Add dynamic form fields to workflow steps
- Configure validation rules and dropdown options
- Manage field positioning and layout
- Update field properties and options

#### 🔍 Search & Discovery
- Universal search across tasks, processes, and templates
- Advanced filtering and sorting capabilities
- Performance-optimized search queries
- Cross-organizational data discovery

#### ⚡ Automation & Rules
- Create conditional automation rules (if-then logic)
- Analyze existing automations for conflicts and optimization
- Consolidate and optimize automation rules
- Monitor automation health and performance

## Architecture

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
```

![tallyfy-mcp-architecture-v1](https://github.com/user-attachments/assets/79047d20-5ddd-479d-baa6-92e1113a18e0)


## Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up server environment variables**:
   ```bash
   export ANTHROPIC_API_KEY="your-anthropic-api-key"
   # Optional: Set default values (users will provide their own)
   export TALLYFY_API_KEY="fallback-api-key"  
   export TALLYFY_ORG_ID="fallback-org-id"
   ```

3. **Start the MCP server** (in separate terminal):
   ```bash
   python -m server.server
   ```

4. **Start the WebSocket server**:
   ```bash
   python run_websocket_server.py
   ```

5. **Connect and authenticate clients**:
   - Open `test_client.html` in a web browser
   - Connect to the WebSocket server
   - **Authenticate with your Tallyfy credentials** (API key + org ID)
   - Start sending queries

## Usage

### Web Interface

Open `test_client.html` in your browser for a ready-to-use chat interface.

### WebSocket API

Connect to `ws://localhost:9001` and send messages in JSON format:

```json
{
  "type": "query",
  "content": "Your message here"
}
```

#### Authentication

Before sending queries, users must authenticate with their Tallyfy credentials:

```json
{
  "type": "auth",
  "api_key": "your-tallyfy-api-key",
  "org_id": "your-organization-id"
}
```

#### Message Types

**Client to Server**:
- `auth`: Authenticate with API key and org ID
- `query`: Send a query to the MCP client
- `ping`: Ping the server

**Server to Client**:
- `connection_established`: Connection successful with session ID
- `auth_success`: Authentication successful
- `auth_error`: Authentication failed
- `response`: Response from the MCP client
- `processing`: Indicates query is being processed
- `info`: Informational messages
- `error`: Error messages
- `pong`: Response to ping

#### Special Commands

- `"clear"`: Clear conversation history
- `"quit"`: Disconnect from server

### Command Line Options

```bash
python run_websocket_server.py --help
```

Options:
- `--host`: Host to bind to (default: localhost)
- `--port`: Port to bind to (default: 9001)
- `--debug`: Enable debug logging

## Session Management

Each WebSocket connection gets:
- Unique session ID
- Separate conversation history  
- **Per-user authentication** with Tallyfy API credentials
- **Isolated credential storage** for secure multi-tenancy
- Automatic cleanup after 60 minutes of inactivity

## File Structure

```
client/
├── __init__.py              # Package initialization
├── config.py               # Configuration management
├── conversation.py         # Conversation history management
├── exceptions.py           # Custom exceptions
├── mcp_client.py          # Core MCP client logic
├── prompts.py             # System prompts
├── session_manager.py     # Multi-user session management
└── websocket_server.py    # WebSocket server implementation

websocket_server.py        # Server entry point
test_client.html          # Web-based test client
README.md                 # This file
```

## Development

### Running Tests

```bash
# Start the MCP server
python -m server.server

# Start the WebSocket server
python run_websocket_server.py --debug

# Open index.html in browser
```

### Adding Features

1. **New Message Types**: Add handlers in `websocket_server.py`
2. **Session Features**: Extend `session_manager.py`
3. **MCP Extensions**: Modify `mcp_client.py`

## Configuration

Environment variables:
- `ANTHROPIC_API_KEY`: Required for Claude API access
- `TALLYFY_API_KEY`: Required for Tallyfy API access
- `TALLYFY_ORG_ID`: Optional, auto-injected if provided
- `MCP_SERVER_URL`: Optional, defaults to `http://127.0.0.1:9000/mcp/`

## Monitoring

The server provides:
- Connection logging
- Session statistics
- Automatic cleanup of inactive sessions
- Health monitoring via ping/pong

## Error Handling

- Graceful handling of client disconnections
- Automatic session cleanup
- Comprehensive error logging
- Fallback responses for failed operations

## Security Considerations

This server implements comprehensive security measures following 2025 MCP security best practices:

### Authentication & Authorization
- **Per-session authentication** with user-provided Tallyfy API credentials
- **Credential verification** against Tallyfy API before session creation
- **JWT token parsing** for user identification and validation
- **Session-based access control** - all queries authenticated with user's own credentials

### Data Protection
- **Credential isolation** - each session stores its own API keys securely in memory
- **No credential persistence** - API keys are only stored in memory during active sessions
- **Memory-only session storage** - no sensitive data written to disk
- **Automatic credential cleanup** when sessions expire or disconnect

### Security Hardening
- **Input validation** on all WebSocket messages and API calls
- **Session timeout** - automatic cleanup of inactive sessions after 60 minutes
- **UUID-based session identifiers** (not exposed in URLs)
- **Environment variable protection** for server configuration
- **Prompt injection mitigation** through input validation

### MCP Security Compliance
- **User approval required** for all tool invocations (following MCP specification)
- **Tool poisoning protection** through validation
- **Cross-session isolation** preventing data leakage between users
- **Secure transport** with WebSocket and HTTP-SSE support

## Deployment

### Production Environment
- **Target**: DigitalOcean droplet (143.198.69.152)
- **Ports**: 9000 (MCP Server), 8765 (WebSocket Server)
- **Deployment**: Automated via GitHub Actions
- **Monitoring**: Built-in health checks and session statistics

### Technology Stack
- **Framework**: FastMCP 2.9.0 with Python 3.7+ support
- **WebSocket**: websockets 11.0.3 for real-time communication
- **AI Integration**: Anthropic Claude API 0.52.2
- **Workflow SDK**: Tallyfy SDK 1.0.2

## Related Resources

### Tallyfy Products
- [Tallyfy Pro](https://tallyfy.com/products/pro/): Core workflow automation platform
- [API Documentation](https://go.tallyfy.com/api): Tallyfy REST API reference
- [Product Overview](https://tallyfy.com/products/): Complete product suite

### MCP Resources
- [Model Context Protocol](https://modelcontextprotocol.io/): Official MCP specification
- [FastMCP Framework](https://gofastmcp.com/): Python framework for MCP development
- [Anthropic MCP Guide](https://www.anthropic.com/news/model-context-protocol): Introduction to MCP

### Development Resources
- **Issues & Support**: [GitHub Issues](https://github.com/tallyfy/mcp-server/issues)
- **API Support**: [Tallyfy API Support](https://github.com/tallyfy/api-support)
- **Developer Documentation**: See `CLAUDE.md` for comprehensive development guidance

## AI-Driven Development

This codebase supports AI-assisted automation for large-scale development tasks. Complex operations can be broken down into atomic prompt files and executed methodically using Claude's non-interactive mode. 

For detailed automation patterns, development guidelines, and technical implementation details, see `CLAUDE.md`.
