# GitHub Copilot Workflow Setup

## Overview

The `.github/workflows/copilot-setup-steps.yml` workflow is designed to preconfigure GitHub Copilot's ephemeral development environment with all the necessary dependencies and tools for the diagram-to-iac project.

## Purpose

This workflow ensures that when GitHub Copilot starts working on this repository, it has:
- Python 3.12 environment properly configured
- All project dependencies installed
- Required directories created
- Core modules validated and working
- Testing framework available

## Workflow Specification

The workflow follows GitHub's copilot-setup-steps specification:

### Required Elements
- **Job Name**: Must be named `copilot-setup-steps`
- **Permissions**: Minimal `contents: read` permission
- **Timeout**: Set to 15 minutes (max 59 allowed)
- **Platform**: Runs on `ubuntu-latest`

### Customizable Elements
- `runs-on`: Currently set to `ubuntu-latest`
- `permissions`: Set to `contents: read` only
- `timeout-minutes`: Set to 15 minutes for efficiency
- `steps`: Customized for Python development environment

## Workflow Steps

### 1. Repository Checkout
```yaml
- name: Checkout repository
  uses: actions/checkout@v4
  with:
    fetch-depth: 1
```

### 2. Python Environment Setup
```yaml
- name: Set up Python 3.12
  uses: actions/setup-python@v5
  with:
    python-version: '3.12'
    cache: 'pip'
```

### 3. Directory Creation
Creates required project directories:
- `data/db`, `data/state`, `data/tmp`
- `logs`

### 4. Build Dependencies Installation
Installs essential build tools:
- `setuptools`
- `wheel`

### 5. Project Dependencies Installation
Attempts to install project dependencies with fallback:
- Primary: Install via `pip install -e .`
- Fallback: Install core dependencies manually

### 6. Copilot Setup Script Execution
Runs the existing `setup/build_copilot.sh` script with:
- `COPILOT_ENVIRONMENT=true`
- `SKIP_INSTALL=true` (dependencies already installed)

### 7. Environment Validation
Validates that all core modules can be imported:
- `diagram_to_iac` main package
- `diagram_to_iac.cli` module
- `diagram_to_iac.core.config_loader` module
- `diagram_to_iac.tools.sec_utils` module

### 8. Setup Summary
Generates a comprehensive summary in GitHub Actions including:
- Python and pip versions
- Environment variables
- Installed packages
- Setup status

## Triggers

The workflow is triggered by:

1. **Manual Dispatch**: Can be run manually from GitHub Actions tab
2. **File Changes**: Automatically runs when the workflow file is modified
3. **Pull Requests**: Runs on PRs that modify the workflow file

## Environment Variables

The workflow sets these environment variables:
- `COPILOT_ENVIRONMENT=true`: Enables Copilot-specific behavior
- `SKIP_INSTALL=true`: Skips redundant installations in setup script

## Testing

### Local Testing
Run the workflow validation test:
```bash
python tests/test_copilot_workflow.py
```

This test validates:
- Workflow file existence and syntax
- Required job configuration
- Module imports
- Directory structure
- GitHub Actions specification compliance

### Manual Testing
Test the setup process manually:
```bash
# Set environment variables
export COPILOT_ENVIRONMENT=true
export SKIP_INSTALL=true

# Run setup script
./setup/build_copilot.sh --help

# Validate imports
python -c "import sys; sys.path.insert(0, './src'); import diagram_to_iac; print('✅ Ready')"
```

## Integration with Existing Tools

The workflow leverages existing project infrastructure:

### Build Script Integration
- Uses `setup/build_copilot.sh` designed specifically for Copilot environments
- Respects existing environment detection logic
- Maintains compatibility with local development workflow

### Project Configuration
- Follows `pyproject.toml` dependencies
- Uses existing directory structure
- Respects existing test configuration (`pytest.ini`)

## Maintenance

### Updating Dependencies
When project dependencies change:
1. The workflow will automatically pick up changes from `pyproject.toml`
2. The fallback dependency list may need manual updates
3. Test the workflow with `python tests/test_copilot_workflow.py`

### Modifying Workflow
When changing the workflow:
1. Ensure the job remains named `copilot-setup-steps`
2. Keep `timeout-minutes` ≤ 59
3. Test locally before committing
4. The workflow will auto-run on file changes

## Troubleshooting

### Common Issues

**Module Import Errors**: 
- Check that `PYTHONPATH` includes `./src`
- Verify all dependencies are installed
- Run validation tests individually

**Timeout Issues**:
- Current timeout is 15 minutes
- Network issues may require increasing timeout
- Consider adding retry logic for network operations

**Permission Issues**:
- Workflow uses minimal `contents: read` permission
- Copilot gets separate token for its operations
- No additional permissions should be needed

### Debug Commands

```bash
# Check Python environment
python --version
python -m pip --version
python -c "import sys; print(sys.path)"

# Test module imports
python -c "import sys; sys.path.insert(0, './src'); import diagram_to_iac"

# Validate workflow syntax
python -c "import yaml; yaml.safe_load(open('.github/workflows/copilot-setup-steps.yml'))"

# Run comprehensive test
python tests/test_copilot_workflow.py
```

## Security Considerations

### Minimal Permissions
- Only `contents: read` permission granted
- No access to secrets or sensitive data
- Copilot gets separate, more privileged token

### Safe Dependencies
- Only installs dependencies from `pyproject.toml`
- Uses official GitHub Actions (`actions/checkout`, `actions/setup-python`)
- No custom or third-party actions

## Future Improvements

Potential enhancements:
- Add caching for Python dependencies
- Implement retry logic for network operations
- Add parallel testing of multiple Python versions
- Integrate with existing CI/CD pipeline health checks