# 🐳 Dual-Registry Container Strategy

## Overview

The DevOps-in-a-Box project uses a **dual-registry approach** to maximize reliability, availability, and user convenience. This document explains the strategy, implementation, and maintenance considerations.

## Registry Roles

### Primary Registry: GitHub Container Registry (GHCR)
- **Purpose**: Primary source for container pulls in workflows
- **URL**: `ghcr.io/amartyamandal/diagram-to-iac-r2d:latest`
- **Benefits**:
  - Native GitHub Actions integration
  - Automatic authentication via GitHub PATs
  - Fast pulls within GitHub ecosystem
  - No external service dependencies

### Backup Registry: Docker Hub
- **Purpose**: Redundancy, public visibility, cross-platform compatibility
- **URL**: `amartyamandal/diagram-to-iac-r2d:latest`
- **Benefits**:
  - Public discoverability
  - Cross-platform container pulls
  - Fallback if GHCR has issues
  - Industry-standard registry

## Implementation Details

### Build Pipeline Strategy

The build pipeline (`diagram-to-iac-build.yml`) pushes to **both registries** simultaneously:

```yaml
# Push to Docker Hub
- name: "📦 Push to Docker Hub"
  run: |
    echo "${{ secrets.DOCKERHUB_API_KEY_ENCODED }}" | base64 -d | docker login -u "$(echo "${{ secrets.DOCKERHUB_USERNAME_ENCODED }}" | base64 -d)" --password-stdin
    docker push amartyamandal/diagram-to-iac-r2d:$VERSION
    docker push amartyamandal/diagram-to-iac-r2d:latest

# Push to GHCR
- name: "📦 Push to GHCR"
  run: |
    echo "${{ secrets.REPO_API_KEY }}" | base64 -d | docker login ghcr.io -u amartyamandal --password-stdin
    docker tag amartyamandal/diagram-to-iac-r2d:$VERSION ghcr.io/amartyamandal/diagram-to-iac-r2d:$VERSION
    docker tag amartyamandal/diagram-to-iac-r2d:latest ghcr.io/amartyamandal/diagram-to-iac-r2d:latest
    docker push ghcr.io/amartyamandal/diagram-to-iac-r2d:$VERSION
    docker push ghcr.io/amartyamandal/diagram-to-iac-r2d:latest
```

### Workflow Usage Strategy

R2D workflows (`r2d-unified.yml`) pull **only from GHCR**:

```yaml
# GHCR login for private container access
- name: "🔐 Login to GHCR"
  run: |
    echo "${{ secrets.REPO_API_KEY }}" | base64 -d | docker login ghcr.io -u ${{ github.actor }} --password-stdin

# Action uses GHCR image
- name: "🤖 Execute R2D Container Action"
  uses: ./.github/actions/r2d
  # action.yml internally references: ghcr.io/amartyamandal/diagram-to-iac-r2d:latest
```

### Action Definition Strategy

The action definition (`action.yml`) references **GHCR as primary**:

```yaml
runs:
  using: 'docker'
  image: 'ghcr.io/amartyamandal/diagram-to-iac-r2d:latest'  # GHCR primary
```

## Secret Management

### Required Secrets for Build (Project Maintainers)

| Secret | Purpose | Registry |
|--------|---------|----------|
| `REPO_API_KEY` | GitHub PAT for GHCR | GHCR |
| `DOCKERHUB_USERNAME_ENCODED` | Docker Hub username | Docker Hub |
| `DOCKERHUB_API_KEY_ENCODED` | Docker Hub API token | Docker Hub |

### Required Secrets for Usage (End Users)

| Secret | Purpose | Required |
|--------|---------|----------|
| `REPO_API_KEY` | GitHub PAT for GHCR + repo access | ✅ Yes |
| `TF_API_KEY` | Terraform Cloud API | ✅ Yes |
| `OPENAI_API_KEY` | LLM API access | ✅ Yes |
| Docker Hub secrets | Not needed for pulls | ❌ No |

## Benefits of This Strategy

### For End Users
1. **Simplified Setup**: Only need GitHub PAT, no Docker Hub account required
2. **Fast Performance**: GHCR optimized for GitHub Actions
3. **Reliable Access**: GitHub authentication already configured
4. **No External Dependencies**: Everything within GitHub ecosystem

### For Project Maintainers
1. **High Availability**: Dual registry redundancy
2. **Public Visibility**: Docker Hub provides discoverability
3. **Migration Safety**: Gradual transition with fallback options
4. **Cross-Platform Support**: Docker Hub accessible from any environment

### For DevOps Teams
1. **Vendor Independence**: Not locked into single registry
2. **Disaster Recovery**: Multiple container sources
3. **Performance Options**: Choose optimal registry per environment
4. **Compliance Flexibility**: Different registries for different security requirements

## Migration Path from Docker Hub Only

### Phase 1: Dual Push (✅ Complete)
- Build pipeline pushes to both registries
- Action still uses Docker Hub
- Zero user impact

### Phase 2: Primary GHCR (✅ Complete)
- Action updated to use GHCR
- Workflows use GHCR for pulls
- Docker Hub maintained for redundancy

### Phase 3: Full GHCR (Future)
- Docker Hub becomes backup only
- All documentation emphasizes GHCR
- Legacy Docker Hub support maintained

## Troubleshooting

### GHCR Pull Issues
```bash
# Check GHCR authentication
echo "$REPO_API_KEY" | base64 -d | docker login ghcr.io -u username --password-stdin

# Verify image exists
docker pull ghcr.io/amartyamandal/diagram-to-iac-r2d:latest
```

### Docker Hub Fallback
```yaml
# Emergency fallback to Docker Hub (if needed)
runs:
  using: 'docker'
  image: 'docker://amartyamandal/diagram-to-iac-r2d:latest'
```

### Registry Status Check
```bash
# Check both registries
curl -s https://ghcr.io/v2/amartyamandal/diagram-to-iac-r2d/tags/list
curl -s https://registry.hub.docker.com/v2/repositories/amartyamandal/diagram-to-iac-r2d/tags/
```

## Future Considerations

### Performance Monitoring
- Track pull times from both registries
- Monitor error rates and availability
- User feedback on registry preference

### Cost Analysis
- GHCR bandwidth usage (GitHub Actions)
- Docker Hub bandwidth usage (external pulls)
- Storage costs across registries

### Security Updates
- Vulnerability scanning on both registries
- Security policy enforcement
- Access control consistency

## Maintenance Tasks

### Weekly
- [ ] Verify both registries have latest images
- [ ] Check build pipeline success rates
- [ ] Monitor user feedback/issues

### Monthly
- [ ] Review registry performance metrics
- [ ] Update documentation if needed
- [ ] Assess migration phase progress

### Quarterly
- [ ] Registry cost analysis
- [ ] Security audit of both registries
- [ ] Strategy refinement based on usage data

## Conclusion

The dual-registry strategy provides the best of both worlds: the convenience and performance of GHCR for GitHub Actions users, with the reliability and public visibility of Docker Hub as a backup. This approach ensures high availability while simplifying the user experience and maintaining backwards compatibility.
