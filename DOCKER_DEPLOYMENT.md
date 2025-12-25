# Docker Deployment Guide

**Production deployment using Docker Compose with SWAG reverse proxy, DIUN updates, and Uptime Kuma monitoring.**

---

## Architecture

The scan-processor is deployed as part of a modular Docker Compose stack:

```
/home/jodfie/docker/compose/
├── docker-compose.yml          # Main compose file with includes
├── apps/
│   └── scan-processor.yml      # Scan Processor service definition
└── .env                        # Environment variables

/home/jodfie/docker/scan-processor/
├── incoming/                   # QNAP syncs files here
├── processing/                 # Active processing
├── completed/                  # Successful documents
├── failed/                     # Failed documents
├── logs/                       # Processing logs
├── queue/                      # SQLite database
├── scripts/                    # Python scripts (synced from repo)
├── prompts/                    # Claude Code prompts (synced from repo)
└── deploy.sh                   # Deployment script
```

---

## Initial Setup

### 1. Configure Environment Variables

Add to `/home/jodfie/docker/compose/.env`:

```bash
# Scan Processor - Paperless API Token
SCAN_PROCESSOR_PAPERLESS_TOKEN=<your-paperless-api-token>
```

Get your Paperless API token from: https://paperless.redleif.dev/admin/authtoken/token/

### 2. Create Directory Structure

The directory structure should already exist at `/home/jodfie/docker/scan-processor/`. If not:

```bash
mkdir -p /home/jodfie/docker/scan-processor/{incoming,processing,completed,failed,logs,queue,scripts,prompts}
```

### 3. Sync Scripts and Prompts

Initial sync from repo:

```bash
rsync -av /home/jodfie/scan-processor/scripts/ /home/jodfie/docker/scan-processor/scripts/
rsync -av /home/jodfie/scan-processor/prompts/ /home/jodfie/docker/scan-processor/prompts/
```

### 4. Start the Service

```bash
cd /home/jodfie/docker/compose
docker-compose up -d scan-processor-ui
```

### 5. Enable File Watcher (Optional)

The file watcher systemd service monitors the `incoming/` directory and triggers processing:

```bash
# Reload systemd
systemctl --user daemon-reload

# Start service
systemctl --user start scan-processor-watcher

# Enable on boot
systemctl --user enable scan-processor-watcher

# Check status
systemctl --user status scan-processor-watcher
```

---

## Service Configuration

**File**: `/home/jodfie/docker/compose/apps/scan-processor.yml`

Key features:
- **Image**: `ghcr.io/jodfie/scan-processor/web-ui:latest` (auto-built by CI/CD)
- **Port**: 5555 (internal, exposed via SWAG reverse proxy)
- **URL**: https://scanui.redleif.dev
- **Networks**: `reverse_proxy` (SWAG integration)
- **Health Check**: HTTP check on `/health` endpoint every 60s
- **Restart Policy**: `unless-stopped`

### Labels

- **DIUN**: Automatic image update notifications
- **SWAG**: Reverse proxy configuration
  - Host: `scanui.redleif.dev`
  - Port: 5555
- **Uptime Kuma**: HTTP monitoring
  - Interval: 60s
  - Tag: Automation

---

## Deployment Workflow

### Using the Deploy Script (Recommended)

```bash
/home/jodfie/docker/scan-processor/deploy.sh
```

This script:
1. Pulls latest image from GitHub Container Registry
2. Syncs scripts and prompts from repo
3. Restarts the container
4. Checks health status
5. Shows recent logs

### Manual Deployment

```bash
# Pull latest image
cd /home/jodfie/docker/compose
docker-compose pull scan-processor-ui

# Update scripts/prompts
rsync -av /home/jodfie/scan-processor/scripts/ /home/jodfie/docker/scan-processor/scripts/
rsync -av /home/jodfie/scan-processor/prompts/ /home/jodfie/docker/scan-processor/prompts/

# Restart container
docker-compose up -d scan-processor-ui

# View logs
docker logs -f scan-processor-ui
```

---

## CI/CD Integration

The GitHub Actions workflow automatically builds and publishes Docker images to GitHub Container Registry on every push to `main`:

**Workflow**: `.github/workflows/docker-build-publish.yml`

**Images**:
- `ghcr.io/jodfie/scan-processor/web-ui:latest`
- `ghcr.io/jodfie/scan-processor/mcp-server:latest` (optional)

### Automatic Deployment

With DIUN enabled, you'll receive notifications when new images are available. To deploy:

```bash
/home/jodfie/docker/scan-processor/deploy.sh
```

---

## Monitoring

### Health Checks

- **Endpoint**: http://scan-processor-ui:5555/health
- **Interval**: 60s
- **Docker Health**: `docker inspect --format='{{.State.Health.Status}}' scan-processor-ui`

### Uptime Kuma

Automatic monitoring via AutoKuma labels:
- **Name**: Scan Processor UI
- **URL**: http://scan-processor-ui:5555
- **Tag**: Automation
- **Interval**: 60s

### Logs

```bash
# Follow logs
docker logs -f scan-processor-ui

# Last 100 lines
docker logs --tail 100 scan-processor-ui

# Logs since 1 hour ago
docker logs --since 1h scan-processor-ui
```

---

## Volume Management

All volumes are persistent and mounted from `/home/jodfie/docker/scan-processor/`:

| Volume Path | Purpose | Mount Type |
|-------------|---------|------------|
| `incoming/` | Files from QNAP | Read/Write |
| `processing/` | Active processing | Read/Write |
| `completed/` | Successful docs | Read/Write |
| `failed/` | Failed docs | Read/Write |
| `logs/` | Application logs | Read/Write |
| `queue/` | SQLite database | Read/Write |
| `scripts/` | Python scripts | Read-Only |
| `prompts/` | Claude prompts | Read-Only |
| `/home/jodfie/vault/jodys-brain` | BasicMemory vault | Read-Only |

---

## Networking

The scan-processor connects to the `reverse_proxy` network for SWAG integration:

```
Internet → Cloudflare Tunnel → SWAG (reverse_proxy network) → scan-processor-ui:5555
```

**URL**: https://scanui.redleif.dev

SWAG automatically configures the reverse proxy based on labels:
- `swag=enable`
- `swag_port=5555`
- `swag_host=scanui.redleif.dev`

---

## Troubleshooting

### Container Won't Start

1. Check environment variables:
   ```bash
   cat /home/jodfie/docker/compose/.env | grep SCAN_PROCESSOR
   ```

2. Verify volumes exist:
   ```bash
   ls -la /home/jodfie/docker/scan-processor/
   ```

3. Check Docker logs:
   ```bash
   docker logs scan-processor-ui
   ```

### Files Not Processing

1. Check file watcher:
   ```bash
   systemctl --user status scan-processor-watcher
   journalctl --user -u scan-processor-watcher -f
   ```

2. Verify incoming directory:
   ```bash
   ls -la /home/jodfie/docker/scan-processor/incoming/
   ```

3. Test manual processing:
   ```bash
   docker exec -it scan-processor-ui python /app/scripts/process.py /app/incoming/test.pdf --dev
   ```

### Web UI Not Accessible

1. Check container health:
   ```bash
   docker inspect scan-processor-ui | grep -A 10 Health
   ```

2. Verify SWAG configuration:
   ```bash
   docker logs swag | grep scanui
   ```

3. Test internal connectivity:
   ```bash
   docker exec -it swag curl http://scan-processor-ui:5555/health
   ```

### Update Not Deploying

1. Verify image was built:
   - Check GitHub Actions: https://github.com/jodfie/scan-processor/actions

2. Pull image manually:
   ```bash
   docker pull ghcr.io/jodfie/scan-processor/web-ui:latest
   ```

3. Force recreate container:
   ```bash
   cd /home/jodfie/docker/compose
   docker-compose up -d --force-recreate scan-processor-ui
   ```

---

## Backup & Restore

### Backup

Critical data to backup:
- `/home/jodfie/docker/scan-processor/queue/pending.db` - Processing history
- `/home/jodfie/docker/scan-processor/completed/` - Processed documents (if needed)
- `/home/jodfie/docker/scan-processor/logs/` - Application logs

```bash
# Backup database
cp /home/jodfie/docker/scan-processor/queue/pending.db ~/backups/scan-processor-$(date +%Y%m%d).db

# Backup entire directory (excluding incoming/processing)
tar -czf ~/backups/scan-processor-$(date +%Y%m%d).tar.gz \
    --exclude='incoming' \
    --exclude='processing' \
    /home/jodfie/docker/scan-processor/
```

### Restore

```bash
# Restore database
cp ~/backups/scan-processor-20251225.db /home/jodfie/docker/scan-processor/queue/pending.db

# Restore entire directory
tar -xzf ~/backups/scan-processor-20251225.tar.gz -C /
```

---

## Security Considerations

1. **API Tokens**: Stored in `.env` file (not in repo)
2. **Vault Access**: Read-only mount to BasicMemory vault
3. **Container User**: Runs as PUID/PGID from .env
4. **Network Isolation**: Only exposed via reverse_proxy network
5. **HTTPS**: All traffic encrypted via Cloudflare Tunnel → SWAG

---

## Maintenance

### Regular Tasks

**Weekly**:
- Check DIUN notifications for updates
- Review processing errors at https://scanui.redleif.dev/history
- Clean up failed directory if needed

**Monthly**:
- Backup queue database
- Review disk usage in completed/logs directories
- Update Docker image if new version available

**As Needed**:
- Update scripts/prompts from repo
- Add new document categories (update prompts/)
- Adjust classification thresholds

---

## Additional Resources

- **Web UI**: https://scanui.redleif.dev
- **GitHub Repo**: https://github.com/jodfie/scan-processor
- **GitHub Actions**: https://github.com/jodfie/scan-processor/actions
- **Docker Images**: https://github.com/jodfie/scan-processor/pkgs
- **CLAUDE.md**: Project documentation in repo
