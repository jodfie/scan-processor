# Scan Processor System

Comprehensive document processing system with web UI for co-parenting document management.

## Architecture

```
Scanner/Upload → incoming/ → File Watcher → Claude Code Classifier → Category-Specific Processor
                                                                              ↓
                                                                    Paperless-NGX + BasicMemory
                                                                              ↓
                                                                     Pushover Notification
```

## Components

### Web UI (Flask + Socket.IO)
- **URL**: https://scanui.redleif.dev
- **Features**:
  - Real-time processing dashboard
  - Manual upload interface (drag-and-drop)
  - Document preview (PDF.js)
  - Pending clarifications queue
  - Batch operations
  - Processing history

### File Watcher (systemd service)
- Monitors `incoming/` directory for new PDFs
- Triggers processing automatically
- Runs as background service

### Processing Pipeline
1. **Classifier** - Claude Code analyzes document and determines category
2. **Metadata Extractor** - Extracts detailed metadata based on category
3. **Paperless Upload** - Uploads to Paperless-NGX with tags
4. **BasicMemory Notes** - Creates notes for medical/expense documents
5. **Notifications** - Sends Pushover alerts

## Document Categories

- **MEDICAL** - Medical records, bills, EOBs → Creates BasicMemory note
- **CPS_EXPENSE** - Co-parenting expenses → Creates BasicMemory note
- **SCHOOLWORK** - Children's schoolwork → Paperless only
- **GENERAL** - Other documents → Paperless only

## Directory Structure

```
/home/jodfie/scan-processor/
├── incoming/              # Files arrive here
├── processing/            # Currently being processed
├── completed/             # Successfully processed (7-day retention)
├── failed/                # Failed processing
├── prompts/               # Claude Code prompts
│   ├── classifier.md
│   ├── medical.md
│   ├── expense.md
│   └── schoolwork.md
├── config/
│   └── config.yaml        # Main configuration
├── queue/
│   └── pending.db         # SQLite database
├── logs/
│   ├── processor.log
│   ├── watcher.log
│   └── web.log
├── web/                   # Flask application
├── scripts/               # Python processing scripts
└── README.md
```

## Deployment

### Docker Container
```bash
cd /home/jodfie/docker
docker compose up -d scan-processor-ui
docker compose restart swag  # Load new tunnel config
```

### File Watcher Service
```bash
# Copy systemd service file
sudo cp /tmp/scan-watcher.service /etc/systemd/system/

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable scan-watcher
sudo systemctl start scan-watcher

# Check status
sudo systemctl status scan-watcher
```

## Usage

### Manual Upload
1. Visit https://scanui.redleif.dev/upload
2. Drag-and-drop PDF files
3. Monitor processing in real-time

### iOS Shortcuts Integration
Upload documents directly from your iPhone:

1. **API Endpoint**: `https://scanui.redleif.dev/api/upload`
2. **Method**: POST with PDF file
3. **Use Cases**:
   - Scan with iPhone camera and auto-upload
   - Upload PDFs from Files app
   - Share from other apps via Share Sheet

**See**:
- [IOS_SHORTCUTS_QUICK_START.md](IOS_SHORTCUTS_QUICK_START.md) - 5-minute setup
- [IOS_SHORTCUTS_INTEGRATION.md](IOS_SHORTCUTS_INTEGRATION.md) - Complete guide
- [UPLOAD_WORKFLOW_COMPARISON.md](UPLOAD_WORKFLOW_COMPARISON.md) - Scan Processor vs Paperless App

> **Note**: This method provides intelligent processing (Claude Code classification, BasicMemory notes, notifications) vs direct Paperless app upload. See workflow comparison for details.

### Scanner Integration
Configure scanner to save to `/home/jodfie/scan-processor/incoming/`

### Responding to Clarifications
1. Visit https://scanui.redleif.dev/pending
2. Review documents needing clarification
3. Provide required information
4. Processing continues automatically

## Monitoring

- **Web UI**: https://scanui.redleif.dev
- **Uptime Kuma**: Monitors container health
- **Logs**: `/home/jodfie/scan-processor/logs/`

## Configuration

Edit `/home/jodfie/scan-processor/config/config.yaml`:

- Paperless API settings
- BasicMemory paths
- Pushover credentials
- Processing parameters
- Retention policies

## Environment Variables

Located in `/home/jodfie/docker/.env`:

- `SCAN_UI_SECRET_KEY` - Flask secret key
- `PAPERLESS_API_TOKEN` - Paperless authentication
- `PUSHOVER_USER` - Pushover user key
- `PUSHOVER_TOKEN` - Pushover app token

## Troubleshooting

### Container won't start
```bash
docker logs scan-processor-ui
```

### File watcher not triggering
```bash
sudo systemctl status scan-watcher
tail -f /home/jodfie/scan-processor/logs/watcher.log
```

### Processing failures
Check `/home/jodfie/scan-processor/failed/` and review error logs

### Database issues
```bash
# Reset database
rm /home/jodfie/scan-processor/queue/pending.db
docker compose restart scan-processor-ui
```

## Integration Notes

### Claude Code
- **Uses Claude Code CLI with your Pro subscription** (no API costs!)
- Prompts located in `/home/jodfie/scan-processor/prompts/`
- Command: `echo "prompt" | claude --read file.pdf`
- Classifier extracts JSON responses automatically
- Test with: `./scripts/test_classifier.sh <test.pdf>`

### Paperless-NGX
- Auto-creates tags and document types
- Links available in processing history

### BasicMemory
- Uses templates from CPS project
- Notes created in `Medical/` and `Expenses/` folders

## Future Enhancements

See `/home/jodfie/Vault/jodys-brain/TechKB/10-projects/14-scan-processor/Scan-Processor-n8n-Migration.md` for migration path to n8n orchestration.

## Support

- GitHub Issues: https://github.com/anthropics/claude-code/issues
- System logs: `/home/jodfie/scan-processor/logs/`
- Docker logs: `docker logs scan-processor-ui`
