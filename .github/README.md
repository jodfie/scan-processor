# CI/CD Infrastructure

This directory contains GitHub Actions workflows for automated testing, building, and deployment.

## Workflows

### 1. `tests.yml` - Continuous Testing
**Triggers**: Push to main/develop, Pull Requests
**Purpose**: Run comprehensive test suite across multiple Python versions

**Jobs**:
- **test**: Runs pytest with coverage on Python 3.10, 3.11, 3.12
  - Enforces 80%+ code coverage
  - Uploads coverage reports to Codecov

- **validate-samples**: Validates all 48 sample documents (simulation mode)
  - Ensures sample infrastructure remains functional
  - Fast validation without real Claude Code calls

**Status Badge**:
```markdown
![Tests](https://github.com/YOUR_USERNAME/scan-processor/actions/workflows/tests.yml/badge.svg)
```

### 2. `docker-build-publish.yml` - Docker Image Build & Publish
**Triggers**: Push to main, Version tags (v*), Pull Requests
**Purpose**: Build and publish Docker images to GitHub Container Registry

**Jobs**:
- **test**: Runs test suite before building (gate check)
- **build-push**: Builds and publishes both containers
  - **Web UI**: `ghcr.io/YOUR_USERNAME/scan-processor/web-ui:latest`
  - **MCP Server**: `ghcr.io/YOUR_USERNAME/scan-processor/mcp-server:latest`

**Image Tags**:
- `latest` - Latest main branch build
- `v1.0.0` - Semantic version tags
- `pr-123` - Pull request builds (not pushed)

**Status Badge**:
```markdown
![Docker](https://github.com/YOUR_USERNAME/scan-processor/actions/workflows/docker-build-publish.yml/badge.svg)
```

## Setup Instructions

### 1. Enable GitHub Container Registry

The workflows publish to GitHub Container Registry (ghcr.io). No additional setup needed - `GITHUB_TOKEN` is automatically available.

### 2. Make Images Public (Optional)

After first push, images will be private. To make them public:

1. Go to https://github.com/YOUR_USERNAME?tab=packages
2. Click on your package (web-ui or mcp-server)
3. Click "Package settings"
4. Scroll to "Danger Zone"
5. Click "Change visibility" → "Public"

### 3. Add Codecov Token (Optional)

For enhanced coverage reporting:

1. Sign up at https://codecov.io
2. Add your repository
3. Copy the upload token
4. Add to repository secrets: `CODECOV_TOKEN`

## Using Published Images

### Pull Images

```bash
# Web UI
docker pull ghcr.io/YOUR_USERNAME/scan-processor/web-ui:latest

# MCP Server
docker pull ghcr.io/YOUR_USERNAME/scan-processor/mcp-server:latest
```

### Run with Docker Compose

The `docker-compose.yml` in the project root can use these images:

```yaml
services:
  web-ui:
    image: ghcr.io/YOUR_USERNAME/scan-processor/web-ui:latest
    # ... rest of config
```

Or build locally:

```bash
docker-compose up --build
```

## Local Development

### Run Tests Locally

```bash
# Install dependencies
pip install -r requirements-dev.txt

# Run tests
pytest --cov=scripts --cov-fail-under=80

# Validate samples
python3 scripts/validate_samples.py --verbose
```

### Build Docker Images Locally

```bash
# Web UI
docker build -t scan-processor-ui:local ./web

# MCP Server
docker build -t scan-processor-mcp:local ./mcp-server

# Run locally
docker-compose -f docker-compose.local.yml up
```

## Troubleshooting

### Workflow Fails on Coverage

If coverage drops below 80%, the workflow will fail. To fix:

1. Add more tests to increase coverage
2. Identify uncovered code: `pytest --cov=scripts --cov-report=html`
3. Open `htmlcov/index.html` to see what's missing

### Docker Build Fails

Common issues:

- **Missing dependencies**: Check `web/requirements.txt` or `mcp-server/requirements.txt`
- **Permission denied**: Ensure `GITHUB_TOKEN` has package write permissions
- **Platform issues**: Workflows build for linux/amd64 and linux/arm64

### Image Pull Fails

If you get "unauthorized" errors:

```bash
# Login to GHCR
echo $GITHUB_TOKEN | docker login ghcr.io -u YOUR_USERNAME --password-stdin

# Pull image
docker pull ghcr.io/YOUR_USERNAME/scan-processor/web-ui:latest
```

## Security

### Workflow Security

All workflows follow GitHub Actions security best practices:

- ✅ No untrusted input in shell commands
- ✅ Secrets properly scoped and protected
- ✅ Minimal permissions (principle of least privilege)
- ✅ Dependency pinning with version tags
- ✅ No hardcoded credentials

### Container Security

Both Dockerfiles follow security best practices:

- ✅ Use official Python base images
- ✅ Run as non-root user (where applicable)
- ✅ Minimal attack surface (slim images)
- ✅ No secrets baked into images
- ✅ Health checks included

## Maintenance

### Updating Workflows

When modifying workflows:

1. Test locally if possible
2. Create a PR to trigger workflow runs
3. Review workflow results before merging
4. Keep actions up to date (Dependabot recommended)

### Updating Dependencies

```bash
# Update Python dependencies
pip install --upgrade pip-tools
pip-compile requirements-dev.in

# Rebuild Docker images
docker-compose build --no-cache
```

## Additional Workflows (Optional)

Consider adding:

- **security.yml**: Dependency scanning (Safety, pip-audit, Trivy)
- **release.yml**: Automated release notes generation
- **deploy.yml**: Automated deployment to staging/production
- **dependabot.yml**: Automated dependency updates

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [Docker Build Push Action](https://github.com/docker/build-push-action)
- [Codecov](https://docs.codecov.com/docs)
