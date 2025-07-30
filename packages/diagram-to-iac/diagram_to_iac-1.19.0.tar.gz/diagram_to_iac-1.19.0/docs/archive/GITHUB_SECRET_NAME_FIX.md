# GitHub Secret Name Restriction Fix ✅

## 🔍 **Issue Identified**

GitHub has restrictions on secret names and **does not allow secrets containing "GITHUB"** in the name. This means users cannot create a secret named `GITHUB_TOKEN` in their repository settings.

## ✅ **Solution Implemented**

### **Secret Name Mapping**

Based on your [`config.yaml`](config.yaml) secret mapping configuration:

```yaml
secret_mappings:
    REPO_API_KEY: "GITHUB_TOKEN"
    TF_API_KEY: "TFE_TOKEN"
```

### **Corrected Workflow**

Updated [`.github/workflows/r2d-unified.yml`](.github/workflows/r2d-unified.yml) line 236:

**Before (❌ Invalid):**
```yaml
env:
  GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}  # ❌ GitHub doesn't allow this secret name
```

**After (✅ Correct):**
```yaml
env:
  # GitHub repository access (mapped from REPO_API_KEY to GITHUB_TOKEN inside container)
  GITHUB_TOKEN: ${{ secrets.REPO_API_KEY }}  # ✅ Uses allowed secret name
```

## 🔄 **How the Mapping Works**

1. **User creates GitHub secret**: `REPO_API_KEY` (GitHub accepts this name)
2. **Workflow references**: `${{ secrets.REPO_API_KEY }}`
3. **Container receives**: Environment variable `GITHUB_TOKEN`
4. **Python app uses**: `os.environ.get("GITHUB_TOKEN")` works correctly

### **Complete Secret Mapping Chain**

| User's GitHub Secret | Workflow Env Var | Container Env Var | Python Code Uses |
|---------------------|------------------|------------------|-----------------|
| `REPO_API_KEY` | `GITHUB_TOKEN: ${{ secrets.REPO_API_KEY }}` | `GITHUB_TOKEN` | `os.environ.get("GITHUB_TOKEN")` |
| `TF_API_KEY` | `TFE_TOKEN: ${{ secrets.TF_API_KEY }}` | `TFE_TOKEN` | `os.environ.get("TFE_TOKEN")` |
| `DOCKERHUB_USERNAME` | `DOCKERHUB_USERNAME: ${{ secrets.DOCKERHUB_USERNAME }}` | `DOCKERHUB_USERNAME` | `os.environ.get("DOCKERHUB_USERNAME")` |
| `DOCKERHUB_API_KEY` | `DOCKERHUB_API_KEY: ${{ secrets.DOCKERHUB_API_KEY }}` | `DOCKERHUB_API_KEY` | `os.environ.get("DOCKERHUB_API_KEY")` |

## 📋 **Required User GitHub Secrets**

Users need to add these **base64-encoded secrets** to their GitHub repository:

### **Required Secrets:**
- ✅ **`REPO_API_KEY`** - GitHub Personal Access Token (not "GITHUB_TOKEN")
- ✅ **`DOCKERHUB_USERNAME`** - Docker Hub username
- ✅ **`DOCKERHUB_API_KEY`** - Docker Hub personal access token
- ✅ **`TF_API_KEY`** - Terraform Cloud API token

### **Optional AI Secrets:**
- 🤖 **`OPENAI_API_KEY`** - OpenAI API key
- 🤖 **`ANTHROPIC_API_KEY`** - Anthropic API key
- 🤖 **`GOOGLE_API_KEY`** - Google API key

## 🔧 **GitHub Personal Access Token Setup**

For the `REPO_API_KEY` secret, users need:

1. **Create GitHub PAT**: Go to https://github.com/settings/tokens
2. **Permissions needed**:
   - `repo` (Full repository access)
   - `workflow` (Update GitHub Action workflows)
   - `write:packages` (if using GitHub Packages)
3. **Base64 encode**: `echo -n "ghp_your_token_here" | base64`
4. **Add as `REPO_API_KEY`** (not "GITHUB_TOKEN")

## 🎯 **Validation**

The workflow now correctly:
- ✅ **Uses allowed secret names** (`REPO_API_KEY` instead of `GITHUB_TOKEN`)
- ✅ **Maps to correct env vars** inside the container
- ✅ **Works with Python code** that expects `GITHUB_TOKEN` environment variable
- ✅ **Follows GitHub naming restrictions**

## 🚀 **Result**

Users can now successfully:
1. Create the required secrets with valid names
2. Run the R2D workflow without secret naming conflicts  
3. Access GitHub repositories through the `REPO_API_KEY` → `GITHUB_TOKEN` mapping

---

**Status**: ✅ **FIXED** - Workflow now uses GitHub-compliant secret names
