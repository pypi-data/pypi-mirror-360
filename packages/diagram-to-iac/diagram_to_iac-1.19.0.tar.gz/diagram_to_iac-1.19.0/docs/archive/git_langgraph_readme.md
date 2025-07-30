# Git LangGraph Agent

The Git LangGraph Agent is a specialized LangGraph-based agent designed for DevOps automation with a focus on Git operations and GitHub integration.

## Overview

This agent implements a hybrid-agent architecture featuring:
- **Light LLM "planner" node** that decides the next action via routing tokens
- **Specialized tool agents** (Shell, Git, GitHub) that execute real commands
- **LangGraph state machine** that orchestrates the control flow
- **Configuration-driven behavior** with robust error handling
- **Memory integration** for operation tracking

## Architecture

The agent follows a structured workflow:

1. **Planner LLM** analyzes user input and emits routing tokens:
   - `ROUTE_TO_CLONE` for git clone operations
   - `ROUTE_TO_ISSUE` for GitHub issue creation
   - `ROUTE_TO_SHELL` for shell command execution
   - `ROUTE_TO_END` when no action needed

2. **Router function** maps tokens to appropriate tool nodes

3. **Tool nodes** execute real operations using battle-tested tools

4. **State machine** handles error paths and success flows

## Key Features

### Git Operations
- **Repository Cloning**: Secure git clone operations with authentication handling
- **Branch Management**: Support for specific branch cloning
- **Depth Control**: Configurable clone depth for optimization
- **Workspace Management**: Organized workspace structure for repositories

### GitHub Integration
- **Issue Creation**: Automated GitHub issue creation
- **Label Management**: Support for issue labels and assignees
- **Authentication**: GitHub CLI integration with token-based auth
- **Repository Validation**: Smart repository URL validation and parsing

### Shell Integration
- **Safe Execution**: Whitelisted shell command execution
- **Workspace Context**: Commands executed within repository context
- **Error Handling**: Comprehensive error detection and reporting
- **Timeout Management**: Configurable command timeouts

## Tools

The agent integrates with the following tools (now located in `diagram_to_iac.tools.git`):

### GitExecutor
Core class that handles:
- Git clone operations with full configuration support
- GitHub CLI operations for issue management
- Authentication failure detection
- Repository path management
- Memory integration for operation tracking

### LangChain Tools
- `git_clone`: LangChain tool wrapper for git cloning
- `gh_open_issue`: LangChain tool wrapper for GitHub issue creation

## Configuration

The agent uses YAML-based configuration (`git_config.yaml`) with:

### Git Operations
```yaml
git_executor:
  default_workspace: "/workspace"
  default_clone_depth: 1
  default_timeout: 300
  auth_failure_patterns: [...]
  repo_path_template: "{workspace}/{repo_name}"
```

### GitHub CLI
```yaml
github_cli:
  default_timeout: 60
  require_auth_check: true
  auth_failure_patterns: [...]
```

### Error Messages and Status Codes
Structured error handling with predefined messages and status codes for consistent error reporting.

## State Management

The agent maintains state through:
- **Git operation history**: Tracking of all git operations
- **Repository context persistence**: Maintaining context across operations
- **Working directory management**: Proper workspace organization
- **Cross-tool state sharing**: Context flows between all tools

## Error Handling

Comprehensive error handling includes:
- **Authentication failures**: GitHub token and git credential issues
- **Network connectivity issues**: Timeout and connection problems
- **Repository access errors**: Permission and not-found scenarios
- **Tool-specific error propagation**: Detailed error context

## Tool Interactions

The tools work together in a coordinated manner:
- **Clone** → establishes repository context
- **Shell** → operates within repository directory
- **GitHub CLI** → uses repository identity
- **Context flows** between all tools seamlessly

## Testing Strategy

The agent includes comprehensive tests covering:
- **Mock git operations**: Safe testing without real git operations
- **Mock shell commands**: Isolated shell command testing
- **Mock GitHub API calls**: GitHub integration testing without API calls
- **State and context verification**: Memory and state management testing

## Usage

```python
from diagram_to_iac.agents.git_langgraph.agent import GitAgent

# Initialize the agent
agent = GitAgent(config_path="path/to/config.yaml", memory_type="persistent")

# Run git operations
result = agent.run({
    "user_input": "Clone the repository https://github.com/user/repo",
    "operation_id": "clone_001"
})
```

## File Structure

```
src/diagram_to_iac/
├── agents/git_langgraph/
│   ├── agent.py              # Main agent implementation
│   ├── config.yaml           # Agent configuration
│   └── tools/
│       └── __init__.py       # Tool imports (for backward compatibility)
└── tools/git/                # Relocated git tools
    ├── __init__.py           # Git tools package
    ├── git.py                # Core git tools implementation
    └── git_config.yaml       # Git tools configuration
```

## Migration Notes

The git tools have been moved from `agents/git_langgraph/tools/` to `tools/git/` for better organization:
- `git_tools.py` → `git.py`
- `git_tools_config.yaml` → `git_config.yaml`

All import paths have been updated, but backward compatibility is maintained through the tools package.

## Dependencies

- **LangGraph**: For workflow orchestration
- **LangChain**: For tool integration
- **Pydantic**: For schema validation
- **PyYAML**: For configuration management
- **Git CLI**: For git operations
- **GitHub CLI**: For GitHub integration