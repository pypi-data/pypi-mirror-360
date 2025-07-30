# Container Build Fix Strategy for Configuration Issues

## Problem Summary
The production containers use PyPI packages that don't include our recent configuration fixes:
- LogBus workspace-aware paths
- Centralized configuration loading for all agents
- Model policy file inclusion
- Unified config structure

## Current Build Process Issues
1. **Container uses PyPI package**: `pip install "diagram-to-iac==$VERSION"`
2. **Our fixes are in source**: Not yet published to PyPI
3. **Permission errors**: Old package tries to write to `/usr/local/lib/python3.11/logs`

## Solution Options

### Option 1: Immediate Dev Container Fix (Recommended)
Create a development Dockerfile that uses source code instead of PyPI package.

**Pros**: 
- ✅ Immediate fix for development/testing
- ✅ No need to wait for PyPI release
- ✅ Can test all our fixes in container environment

**Cons**: 
- ❌ Only fixes dev environment, not production

### Option 2: Trigger New Release
Tag a new version to trigger the build pipeline with our fixes.

**Pros**: 
- ✅ Fixes production containers
- ✅ Permanent solution

**Cons**: 
- ❌ Requires version bump and proper release process
- ❌ Takes time to propagate through PyPI

### Option 3: Hybrid Dockerfile (Best Long-term)
Modify Dockerfile to use source code when `PACKAGE_VERSION=dev` or similar.

**Pros**: 
- ✅ Supports both dev and production builds
- ✅ Flexible for testing
- ✅ Maintains production stability

**Cons**: 
- ❌ More complex Dockerfile logic

## Recommended Implementation Plan

1. **Phase 1**: Create dev container with source code installation
2. **Phase 2**: Test all configuration fixes in container environment  
3. **Phase 3**: Tag new version for production release
4. **Phase 4**: Update Dockerfile to support both modes

## Files to Modify

### 1. Create `docker/dev/Dockerfile.source` 
- Copy from current Dockerfile
- Replace PyPI installation with source code installation
- Ensure all config files are copied correctly

### 2. Update `.github/actions/r2d/Dockerfile`
- Add logic to detect development vs production mode
- Support both PyPI and source installation

### 3. Add container test script
- Verify all configuration fixes work in container
- Test workspace-aware paths
- Validate centralized config loading

## Expected Outcomes

After implementation:
- ✅ No more `/usr/local/lib/python3.11/logs` permission errors
- ✅ All agents load config from centralized system
- ✅ Model policy files found correctly
- ✅ GitExecutor, TerraformExecutor, DemonstratorAgent use proper config
- ✅ LogBus uses workspace-aware paths

## Next Steps

1. Implement dev container with source code
2. Run comprehensive container tests
3. Validate all configuration warnings are resolved
4. Prepare for production release
