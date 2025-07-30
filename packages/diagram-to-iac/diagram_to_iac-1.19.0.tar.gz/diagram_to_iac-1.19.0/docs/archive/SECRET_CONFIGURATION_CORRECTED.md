# 🔐 Secret Configuration Guide - CORRECTED

## **Two Different Secret Naming Patterns**

### **1. Build Workflow Secrets** (`.github/workflows/diagram-to-iac-build.yml`)
Uses `*_ENCODED` suffix secrets:

```yaml
# Required secrets in GitHub repository settings:
ANTHROPIC_API_KEY_ENCODED     # Base64 encoded Anthropic API key
DOCKERHUB_API_KEY_ENCODED     # Base64 encoded Docker Hub token  
DOCKERHUB_USERNAME_ENCODED    # Base64 encoded Docker Hub username
GOOGLE_API_KEY_ENCODED        # Base64 encoded Google AI API key
GROK_API_KEY_ENCODED          # Base64 encoded Grok API key
OPENAI_API_KEY_ENCODED        # Base64 encoded OpenAI API key
PYPI_API_KEY_ENCODED          # Base64 encoded PyPI token
REPO_API_KEY_ENCODED          # Base64 encoded GitHub PAT
TF_API_KEY_ENCODED            # Base64 encoded Terraform Cloud token
```

### **2. R2D Workflow Secrets** (`.github/workflows/r2d-unified*.yml`)
Uses regular secret names (without `_ENCODED`):

```yaml
# Required secrets in GitHub repository settings:
REPO_API_KEY          # Base64 encoded GitHub Personal Access Token
TF_API_KEY            # Base64 encoded Terraform Cloud API token

# Optional AI API keys (at least one recommended):
OPENAI_API_KEY        # Base64 encoded OpenAI API key
ANTHROPIC_API_KEY     # Base64 encoded Anthropic API key  
GOOGLE_API_KEY        # Base64 encoded Google AI API key

# Optional Docker Hub credentials (if using private registries):
DOCKERHUB_USERNAME    # Base64 encoded Docker Hub username
DOCKERHUB_API_KEY     # Base64 encoded Docker Hub token
```

## **How Base64 Encoding Works**

### **Container Processing** (`src/diagram_to_iac/tools/sec_utils.py`):
1. **Environment Variables**: Secrets are passed as base64 encoded environment variables
2. **Automatic Decoding**: `sec_utils.py` automatically detects and decodes base64 values
3. **Smart Detection**: If a value looks already decoded (e.g., starts with `sk-`, `ghp_`, etc.), it's used as-is
4. **Environment Setting**: Decoded values are set as standard environment variables

### **API Integration** (`src/diagram_to_iac/tools/api_utils.py`):
- Uses the decoded environment variables for API calls
- Handles timeout configuration from `config.yaml`
- Provides fallback handling for missing credentials

## **Secret Creation Example**

### **Encoding Secrets:**
```bash
# GitHub Personal Access Token
echo -n "ghp_your_actual_token_here" | base64

# OpenAI API Key  
echo -n "sk-your_openai_key_here" | base64

# Terraform Cloud Token
echo -n "your_tfe_token_here.atlasv1.something" | base64

# Docker Hub Username
echo -n "your_dockerhub_username" | base64
```

### **Adding to GitHub Secrets:**
1. Go to `Settings` → `Secrets and variables` → `Actions`
2. Click `New repository secret`
3. Use the correct name pattern (with or without `_ENCODED` suffix)
4. Paste the base64 encoded value

## **Secret Mapping Flow**

### **Build Workflow:**
```
GitHub Secret: REPO_API_KEY_ENCODED (base64)
        ↓
Container Env: REPO_API_KEY_ENCODED (base64)
        ↓  
sec_utils.py: Decodes to REPO_API_KEY (plain)
        ↓
config.yaml: Maps to GITHUB_TOKEN (plain)
        ↓
Application: Uses GITHUB_TOKEN environment variable
```

### **R2D Workflow:**
```
GitHub Secret: REPO_API_KEY (base64)
        ↓
Container Env: GITHUB_TOKEN (base64) 
        ↓
sec_utils.py: Decodes to GITHUB_TOKEN (plain)
        ↓
Application: Uses GITHUB_TOKEN environment variable
```

## **Required vs Optional Secrets**

### **Always Required:**
- `REPO_API_KEY` - GitHub repository operations
- `TF_API_KEY` - Terraform Cloud workspace operations

### **AI Keys (at least one recommended):**
- `OPENAI_API_KEY` - Best performance/cost ratio
- `ANTHROPIC_API_KEY` - Good for reasoning tasks  
- `GOOGLE_API_KEY` - Good for multimodal tasks

### **Optional for Special Cases:**
- `DOCKERHUB_USERNAME` + `DOCKERHUB_API_KEY` - Only if using private Docker registries
- `PYPI_API_KEY` - Only for build workflow (package publishing)

## **Validation Process**

The container validates secrets on startup:
1. **Environment Check**: Looks for expected environment variables
2. **Decoding**: Attempts base64 decoding if needed
3. **Validation**: Checks format (e.g., GitHub tokens start with `ghp_`)
4. **Early Exit**: Fails fast if required secrets missing
5. **Logging**: Reports which secrets are available/missing

## **Error Messages**

### **Missing Required Secret:**
```
❌ Error: Required secret REPO_API_KEY not found or empty
📋 Please add base64 encoded GitHub Personal Access Token as repository secret
```

### **Invalid Base64:**
```
❌ Error: Secret OPENAI_API_KEY contains invalid base64 encoding
💡 Use: echo -n "your-key" | base64
```

### **Wrong Format:**
```
⚠️ Warning: REPO_API_KEY doesn't look like a GitHub token (should start with ghp_)
🔍 Please verify your token format
```

## **Summary**

- **Build workflows**: Use `*_ENCODED` secret names
- **R2D workflows**: Use regular secret names  
- **All values**: Must be base64 encoded
- **Container**: Automatically decodes and validates
- **Configuration**: Uses `src/diagram_to_iac/config.yaml` mapping

This two-tier approach allows:
1. **Separation of concerns** - Build vs runtime secrets
2. **Security** - All secrets base64 encoded in transit
3. **Flexibility** - Different access patterns for different workflows
4. **Validation** - Early detection of missing/invalid secrets
