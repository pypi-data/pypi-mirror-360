# DevOps-in-a-Box: Complete Project Knowledge Summary
*Session Handoff Document - Everything You Need to Know*

> **Note:** This document provides a comprehensive internal overview. Some sections, particularly regarding the primary container strategy and specific secret names for end-users, may be outdated. For the current user-facing setup and GHCR-primary strategy, please refer to `docs/R2D_USER_GUIDE.md` and `docs/DEVELOPER_GUIDE.md`.

---

## 🏗️ Project Overview

**DevOps-in-a-Box** is a containerized multi-agent system that automates the "Repo-to-Deployment" (R2D) workflow using AI-driven intelligence. It translates infrastructure diagrams into deployable Terraform code with zero human intervention for standard operations.

### Core Philosophy
- **LangGraph-based Multi-Agent System**: Each agent has specialized expertise (GitAgent, TerraformAgent, VisionAgent, etc.)
- **Container-Based GitHub Actions**: All operations happen within secure, isolated containers
- **Severance-Inspired Architecture**: Each AI agent maintains perfect "professional severance" - specialized domain knowledge without context switching

---

## 🏛️ Architecture Overview

### Multi-Agent System
```
SupervisorAgent (Orchestrator)
├── GitAgent (Repository Operations)
├── VisionAgent (Diagram Analysis) 
├── ShellAgent (System Operations)
├── TerraformAgent (Infrastructure Deployment)
└── Memory System (Shared State)
```

### Container Strategy
- **Development**: `docker/dev/Dockerfile` - Local development environment
- **Production**: `.github/actions/r2d/Dockerfile` - GitHub Actions container
- **Base**: Alpine-based Python 3.12 images for security and size

### Key Technologies
- **Core Language**: Python 3.12
- **Agent Framework**: LangGraph + LangChain
- **LLM Driver**: Multi-provider router (OpenAI/Gemini/Anthropic) in `src/diagram_to_iac/tools/llm_utils/router.py`
- **IaC Runtime**: Terraform 1.8+ via ShellTool
- **VCS Integration**: Git CLI + GitHub CLI (`gh`)

---

## 📁 Repository Structure Deep Dive

### Core Source Code
```
src/diagram_to_iac/
├── cli.py                    # Main CLI entry point
├── r2d.py                    # R2D workflow orchestrator
├── agents/                   # Multi-agent system
│   ├── supervisor.py         # Main orchestrator agent
│   ├── vision_agent.py       # Diagram analysis agent
│   ├── git_langgraph/        # Git operations agent
│   │   ├── agent.py          # GitAgent implementation
│   │   └── tools/            # Git-specific tools
│   └── hello_langgraph/      # Example/template agent
├── core/                     # Core infrastructure
│   ├── agent_base.py         # Base agent class
│   ├── config.py             # Configuration management
│   ├── memory.py             # Agent memory system
│   └── enhanced_memory.py    # Advanced memory features
└── tools/                    # Shared utilities
    ├── api_utils.py          # API helpers
    ├── sec_utils.py          # Security utilities
    └── llm_utils/            # LLM integration
        ├── router.py         # Multi-provider LLM router
        ├── openai_driver.py  # OpenAI integration
        ├── gemini_driver.py  # Google Gemini integration
        └── anthropic_driver.py # Anthropic Claude integration
```

### Configuration System
```
config/
├── logging.yaml             # Logging configuration
├── model_policy.yaml        # LLM model selection policy
├── secrets.yaml             # SOPS-encrypted secrets (production)
├── secrets_example.yaml     # Template for secrets
└── shell_tools_config.yaml  # Shell command allowlist
```

### Container Infrastructure
```
docker/
├── dev/                     # Development environment
│   ├── Dockerfile           # Dev container definition
│   ├── docker-compose.yml   # Local development stack
│   └── entrypoint.sh        # Dev container entry point
└── action/                  # GitHub Actions container (legacy)

.github/actions/r2d/
├── Dockerfile               # Production container
├── action.yml               # GitHub Action definition
└── entrypoint.sh            # Production entry point
```

### Testing & Debugging
```
tests/                       # Comprehensive test suite
├── agents/                  # Agent-specific tests
│   ├── git_langgraph/       # GitAgent tests
│   └── hello_langgraph/     # Example agent tests
├── core/                    # Core system tests
└── tools/                   # Tool-specific tests

debug/                       # Debugging and validation scripts
├── debug_copilot_assignment.py
├── debug_env_override.py
├── debug_github_auth.py
├── debug_secrets.py
├── test_workflow_validation.py
└── validate_task2_workflow.py
```

---

## 🔧 Development Workflow

### Local Development Setup
```bash
# 1. Environment Setup
./setup/setup_env.sh         # Initialize development environment
./setup/setup_tools.sh       # Install required tools (terraform, gh, etc.)

# 2. Development Container
cd docker/dev
docker-compose up -d         # Start development environment
docker-compose exec app bash # Enter development container

# 3. Build & Test
./scripts/build_wheel.sh     # Build Python package
pytest tests/               # Run test suite
```

### Container Development Strategy
- **Local Development**: Use `docker/dev/` for isolated development
- **GitHub Actions Testing**: Use `.github/actions/r2d/` for production testing
- **Hot Reload**: Development container supports code changes without rebuild

### Build Process
```bash
# Local Build
./scripts/build_wheel.sh

# Container Build (Development)
cd docker/dev && docker build -t diagram-to-iac:dev .

# Container Build (Production)
cd .github/actions/r2d && docker build -t diagram-to-iac:prod .
```

---

## 🧪 Testing Strategy

### Test Structure
- **Unit Tests**: `tests/tools/` - Individual tool testing
- **Agent Tests**: `tests/agents/` - Agent behavior validation
- **Integration Tests**: `tests/core/` - End-to-end workflows
- **Debugging Scripts**: `debug/` - Workflow validation and troubleshooting

### Key Test Commands
```bash
# Run all tests
pytest tests/

# Run specific agent tests
pytest tests/agents/git_langgraph/

# Run with coverage
pytest --cov=src/diagram_to_iac tests/

# Debug specific workflows
python debug/debug_secrets.py
python debug/validate_task2_workflow.py
```

### Test Requirements
- All new tools must have accompanying unit tests
- Mock external dependencies (subprocess calls, LLM responses)
- Fast, isolated tests without external dependencies

---

## 🚀 Deployment & GitHub Actions

### GitHub Actions Workflow
```
.github/workflows/
├── r2d-unified.yml          # Main deployment workflow
└── diagram-to-iac-build.yml # Container build workflow
```

### Container Action Architecture
- **Type**: Container-based GitHub Action
- **Registry**: DockerHub (`amartyamandal/diagram-to-iac-r2d:latest`)
- **Security**: Private repository requiring authentication
- **Isolation**: Runs in secure container environment

### Deployment Triggers
- **Issue Labels**: `r2d-request` label triggers deployment
- **PR Merges**: Automatic infrastructure updates
- **Manual Triggers**: `workflow_dispatch` for testing
- **Issue Comments**: `/r2d deploy` commands

---

## 🔐 Security & Configuration

### Security Model
- **Shell Command Allowlist**: Only approved binaries in `config/shell_allowlist.yaml`
- **Workspace Isolation**: All operations within `/workspace` container directory
- **Subprocess Timeouts**: 30-second default timeout for all shell operations
- **Secret Management**: SOPS encryption + GitHub Actions secrets

### Configuration Hierarchy
1. **App Config**: `src/diagram_to_iac/config.yaml` - Default application settings
2. **Environment Variables**: Runtime overrides
3. **GitHub Secrets**: Secure credential storage
4. **SOPS Secrets**: Development secret management

### Required Secrets
```yaml
# GitHub Secrets Required
OPENAI_API_KEY: "LLM vision processing"
TF_API_KEY: "Terraform Cloud authentication"
REPO_API_KEY: "GitHub repository access"
DOCKERHUB_USERNAME: "Container registry access"
DOCKERHUB_API_KEY: "Container registry authentication"
```

---

## 🤖 Agent System Details

### Agent Communication
- **State Management**: LangGraph TypedDict state objects
- **Memory System**: File-based persistent memory in `data/db/`
- **Routing**: LLM-driven routing tokens (`ROUTE_TO_*`)
- **Error Handling**: Automatic retry and escalation patterns

### Agent Personalities (Severance-Inspired)
- **SupervisorAgent**: "The Wellness Counselor" - Calm orchestrator
- **GitAgent**: "The Archivist" - Obsessive version control
- **VisionAgent**: "The Translator" - Diagram interpretation expert
- **ShellAgent**: "The Custodian" - Paranoid security enforcer
- **TerraformAgent**: "The Engineer" - Infrastructure purist

### Routing System
```python
# LLM-driven routing patterns
ROUTE_TO_CLONE = "Repository operations needed"
ROUTE_TO_VISION = "Diagram analysis required"
ROUTE_TO_TERRAFORM = "Infrastructure deployment"
ROUTE_TO_AUTO_FIX = "Self-healing activation"
ROUTE_TO_ISSUE = "Human escalation required"
```

---

## 🔧 Development Tools & Scripts

### Build Scripts
```bash
scripts/
├── build_wheel.sh           # Python package build
├── update_deps.py           # Dependency management
├── update_version.py        # Version bumping
└── smoke_run.sh            # Quick validation test
```

### Security Scripts
```bash
scripts/
├── encrypt_secrets.sh       # SOPS secret encryption
├── decrypt_secrets.sh       # SOPS secret decryption
├── sync_github_secrets.sh   # GitHub secret synchronization
└── generate_env_example.sh  # Environment template generation
```

### Setup Scripts
```bash
setup/
├── setup_env.sh            # Development environment initialization
├── setup_tools.sh          # Tool installation (terraform, gh, etc.)
├── setup_repo.sh           # Repository configuration
└── init_sops.sh           # SOPS encryption setup
```

---

## 📊 Key Achievements & Fixes

### Major Workflow Improvements
1. **Dynamic Issue Assignment**: Removed hardcoded bot usernames, now uses repo owner fallback
2. **Parameter Consistency**: Renamed `copilot_assignee` to `default_assignees` across all files
3. **Workflow Triggers**: Removed `closed` issue triggers, cleaned up routing logic
4. **DockerHub Authentication**: Implemented secure base64 secret handling for private containers

### Configuration Refactoring
- **Unified Parameter Names**: All assignment-related parameters now use `default_assignees`
- **Clear Override Hierarchy**: Config → Environment → Secrets with documented precedence
- **Backward Compatibility**: All changes maintain existing functionality

### Container Architecture
- **Multi-Stage Builds**: Optimized container size and security
- **Development/Production Split**: Separate containers for different environments
- **Security Hardening**: Non-root user, minimal base images, controlled access

---

## 🐛 Known Issues & Debugging

### Common Issues
1. **Container Authentication**: Private DockerHub repos require proper secret configuration
2. **Shell Tool Permissions**: Commands must be in allowlist for security
3. **Memory State**: Agent memory persists between runs - clear `data/db/` if needed
4. **LLM Rate Limits**: Router handles provider failover automatically

### Debug Commands
```bash
# Test container locally
docker run -it --rm diagram-to-iac:dev bash

# Validate GitHub workflow
python debug/validate_workflow_isolation.py

# Check secret configuration
python debug/debug_secrets.py

# Test agent routing
python debug/debug_routing_simple.py
```

### Environment Variables for Debugging
```bash
export DEBUG_MODE=true
export LOG_LEVEL=DEBUG
export DRY_RUN=true
export WORKSPACE_BASE=/workspace
```

---

## 📚 Documentation & Resources

### Key Documentation Files
- `README.md` - Project overview and quick start
- `docs/CONTAINER_ACTION_INTEGRATION.md` - GitHub Actions setup
- `docs/DOCKERHUB_AUTHENTICATION_FIX.md` - Container authentication
- `docs/R2D_WORKFLOW_IMPLEMENTATION_GUIDE.md` - Deployment guide
- `DEVOPS_IN_A_BOX_ARTICLE.md` - Severance-inspired blog post

### Code Examples
- `src/diagram_to_iac/agents/hello_langgraph/` - Template agent implementation
- `demo_multi_agent_models.py` - Multi-agent system demonstration
- `tests/` - Comprehensive test examples

---

## 🔄 Development Patterns

### Adding New Agents
1. Create agent directory in `src/diagram_to_iac/agents/`
2. Implement agent class extending `AgentBase`
3. Define agent-specific tools in `tools/` subdirectory
4. Add routing logic to `SupervisorAgent`
5. Create comprehensive tests in `tests/agents/`

### Adding New Tools
1. Create tool module in appropriate agent's `tools/` directory
2. Follow single responsibility principle (≤40 lines per function)
3. Use Pydantic models for all inputs/outputs
4. Add to shell allowlist if executing commands
5. Write unit tests with mocked dependencies

### Configuration Changes
1. Update `config/secrets_example.yaml` for new secrets
2. Update `src/diagram_to_iac/config.yaml` for app settings
3. Document configuration hierarchy and precedence
4. Test with environment variable overrides

---

## 🎯 Future Development Priorities

### Technical Debt
- Consolidate duplicate agent implementations
- Improve error handling consistency
- Standardize logging across all agents
- Optimize container build times

### Feature Roadmap
- Multi-cloud support (Azure, AWS, GCP)
- Kubernetes native deployment
- Policy as Code integration
- Natural language infrastructure requests

### Testing Improvements
- Integration test automation
- Performance benchmarking
- Security vulnerability scanning
- End-to-end workflow validation

---

## 🔧 Quick Reference Commands

### Development
```bash
# Start development environment
cd docker/dev && docker-compose up -d

# Run tests
pytest tests/

# Build package
./scripts/build_wheel.sh

# Debug workflow
python debug/debug_routing_simple.py
```

### Production
```bash
# Build production container
cd .github/actions/r2d && docker build -t diagram-to-iac:prod .

# Test GitHub Action locally
act workflow_dispatch

# Validate secrets
python debug/debug_secrets.py
```

### Maintenance
```bash
# Update dependencies
python scripts/update_deps.py

# Encrypt secrets
./scripts/encrypt_secrets.sh

# Sync GitHub secrets
./scripts/sync_github_secrets.sh
```

---

## 📝 Session Handoff Notes

### Current State
- All major refactoring completed and tested
- Workflow triggers cleaned up and optimized
- Container authentication documented and fixed
- Configuration hierarchy clearly defined
- Blog post rewritten with enhanced Severance theme

### Next Developer Should Focus On
1. **Performance Optimization**: Container build times and runtime efficiency
2. **Testing Coverage**: Add integration tests for complete workflows  
3. **Documentation**: Update developer onboarding guides
4. **Feature Development**: Multi-cloud support and Kubernetes integration

### Critical Files to Understand
- `src/diagram_to_iac/agents/supervisor.py` - Main orchestration logic
- `.github/workflows/r2d-unified.yml` - Production workflow
- `src/diagram_to_iac/config.yaml` - Application configuration
- `docker/dev/docker-compose.yml` - Development environment

This summary should provide everything needed for the next developer to pick up where we left off and continue building this amazing DevOps automation system! 🚀
