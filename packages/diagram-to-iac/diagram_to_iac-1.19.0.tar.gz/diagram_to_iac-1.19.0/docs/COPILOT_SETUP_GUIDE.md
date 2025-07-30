# 🤖 GitHub Copilot Setup Guide for diagram-to-iac

## Overview

The `setup/build_copilot.sh` script is specifically designed for GitHub Copilot AI paired programming environments. It provides a robust setup, build, and test environment that works even with limited network access and missing API keys.

## Quick Start

```bash
# Navigate to the project root
cd /path/to/diagram-to-iac

# Make the script executable
chmod +x setup/build_copilot.sh

# Run the setup script
./setup/build_copilot.sh --help
```

## Environment Variables

The script automatically detects and adapts to different environments:

### Automatic Detection
- `CI=true` - Detected CI environment
- `COPILOT_ENVIRONMENT=true` - Explicitly set Copilot environment
- `SKIP_INSTALL=true` - Skip network-dependent package installations

### Secret Configuration (Optional)
- `REPO_API_KEY_ENCODED` - Base64 encoded GitHub token
- `TFE_TOKEN_ENCODED` - Base64 encoded Terraform Cloud token  
- `OPENAI_API_KEY_ENCODED` - Base64 encoded OpenAI API key

## Usage Examples

### Basic Setup and Help
```bash
# Get help information
./setup/build_copilot.sh --help

# Run with explicit Copilot environment
COPILOT_ENVIRONMENT=true ./setup/build_copilot.sh --help
```

### Skip Network Dependencies
```bash
# Skip package installation (useful in constrained environments)
SKIP_INSTALL=true ./setup/build_copilot.sh --help

# Force package installation
SKIP_INSTALL=false ./setup/build_copilot.sh --help
```

### With API Keys (Optional)
```bash
# Encode your API keys first
export OPENAI_API_KEY_ENCODED=$(echo -n "sk-your-key-here" | base64)
export TFE_TOKEN_ENCODED=$(echo -n "your-tfe-token" | base64)

# Run with encoded secrets
./setup/build_copilot.sh --help
```

## Script Features

### 🛡️ Robust Network Handling
- Automatic retry logic for network operations
- Graceful fallback when dependencies can't be installed
- Timeout protection to prevent hanging

### 🔍 Environment Detection  
- Automatically detects CI/Copilot environments
- Skips heavy installations in constrained environments
- Provides clear feedback about environment decisions

### 🔐 Secure Secret Management
- Base64 decoding for environment-provided secrets
- Graceful handling of missing API keys
- No secret exposure in logs or output

### ✅ Comprehensive Testing
- Tests all major functionality without network dependencies
- Validates package imports and CLI functionality
- Provides clear success/failure feedback

## Testing the Setup

### Run Comprehensive Tests
```bash
# Run the full test suite
python tests/test_build_copilot.py

# Run the helper test script
./setup/test_copilot.sh
```

### Manual Testing
```bash
# Test basic functionality
SKIP_INSTALL=true ./setup/build_copilot.sh --help

# Test with package installation
SKIP_INSTALL=false ./setup/build_copilot.sh --help
```

## Troubleshooting

### Network Timeouts
```
🔄 Installing project dependencies...
❌ Could not install project at all
```
**Solution**: Use `SKIP_INSTALL=true` to bypass network dependencies

### Missing API Dependencies
```
⚠️ Could not import API utils: No module named 'openai'
🔍 Skipping API tests - this is normal during initial setup
```
**Solution**: This is expected and normal. The script continues gracefully.

### CLI Not Found
```
⚠️ diagram-to-iac command not found in PATH
🔍 Trying to run via python module...
```
**Solution**: The script automatically tries alternative execution methods.

### Package Import Issues
```
❌ Package import failed
```
**Solution**: Ensure you're running from the project root and PYTHONPATH is set correctly.

## Project Structure Requirements

The script expects the following project structure:
```
diagram-to-iac/
├── pyproject.toml          # Required for project detection
├── setup/
│   └── build_copilot.sh    # This script
├── src/
│   └── diagram_to_iac/     # Main package
└── scripts/
    └── update_deps.py      # Dependency management
```

## Integration with GitHub Copilot

### In Copilot Chat
```
@workspace How do I set up the diagram-to-iac project?

Run: ./setup/build_copilot.sh --help
```

### In VS Code with Copilot
1. Open terminal in VS Code
2. Navigate to project root
3. Run: `./setup/build_copilot.sh --help`
4. Copilot will understand the project structure from the successful setup

### Environment Configuration
For consistent Copilot integration, add to your shell profile:
```bash
export COPILOT_ENVIRONMENT=true
export SKIP_INSTALL=true  # For faster Copilot interactions
```

## Advanced Usage

### Custom Environment Setup
```bash
# Create a custom setup for development
cat > .copilot-env << 'EOF'
export COPILOT_ENVIRONMENT=true
export SKIP_INSTALL=true
export PYTHONPATH="$(pwd)/src"
EOF

# Source it before running
source .copilot-env
./setup/build_copilot.sh --help
```

### Integration with Development Workflow
```bash
# Add to your project's .bashrc or .zshrc
alias copilot-setup='cd /path/to/diagram-to-iac && SKIP_INSTALL=true ./setup/build_copilot.sh'
```

## Security Considerations

### Safe Defaults
- Script never logs or exposes secrets
- Base64 encoding prevents accidental exposure
- Graceful handling of missing credentials

### API Key Management
- Always base64 encode API keys before setting environment variables
- Use repository secrets in GitHub environments
- Never commit raw API keys to version control

## Support

If you encounter issues with the script:

1. **Check Prerequisites**: Ensure Python 3.12+ and bash are available
2. **Run Tests**: Execute `python tests/test_build_copilot.py`
3. **Use Helper Script**: Run `./setup/test_copilot.sh` for diagnostics
4. **Check Environment**: Verify you're in the correct project directory
5. **Network Issues**: Use `SKIP_INSTALL=true` to bypass network dependencies

## Success Indicators

When the script works correctly, you should see:
```
🏗️ Setting up diagram-to-iac build environment...
📁 Project root: /path/to/diagram-to-iac
🐍 Python version: Python 3.12.3
✅ API connectivity tests completed
┌─ Running diagram-to-iac CLI ───────────────────
✅ diagram-to-iac CLI is up and running!
└─ CLI finished ─────────────────────────────────
```

---

**Ready to code with Copilot!** 🚀 The script ensures a consistent, reliable setup experience for AI-assisted development.