# Scan Processor - Quick Reference

## Common Commands

### Development Mode (Safe Testing)

**Web UI (Recommended)**:
1. Visit https://scanui.redleif.dev/upload
2. Check the "🔧 Development Mode" checkbox
3. Upload your PDF
4. Results appear immediately with full dry run details

**Command Line**:
```bash
# Test without uploading to Paperless or creating notes
python3 scripts/process.py --dev /path/to/document.pdf

# Test with verbose errors
python3 scripts/process.py --dev incoming/test.pdf 2>&1 | tee logs/test.log
```

### Production Mode (Real Processing)
```bash
# Process a single document
python3 scripts/process.py /path/to/document.pdf

# Process with environment variables
source /home/jodfie/docker/.env
python3 scripts/process.py incoming/document.pdf
```

### Testing & Verification
```bash
# Test classifier only
./scripts/test_classifier.sh /path/to/document.pdf

# Verify Claude Code integration
./scripts/verify_claude_integration.sh

# Manual cleanup
./scripts/cleanup_temp.sh
```

### Docker Operations
```bash
# Restart web UI container
docker compose -f /home/jodfie/docker/docker-compose.yml restart scan-processor-ui

# View web UI logs
docker logs scan-processor-ui --tail 50 -f

# Check container status
docker ps --filter "name=scan-processor-ui"
```

### File Watcher Service
```bash
# Check watcher status
systemctl --user status scan-watcher

# Start watcher
systemctl --user start scan-watcher

# View watcher logs
tail -f /home/jodfie/scan-processor/logs/watcher.log
```

## Development Mode vs Production

| Action | Development Mode | Production Mode |
|--------|------------------|-----------------|
| **Run Command** | `--dev` flag | No flag |
| **Paperless Upload** | ✗ Simulated | ✓ Real |
| **BasicMemory Notes** | ✗ Simulated | ✓ Real |
| **Notifications** | ✗ Skipped | ✓ Sent |
| **Error Details** | ✓ Verbose | ⚠️ Basic |
| **Claude Classification** | ✓ Real | ✓ Real |

## File Locations

```
/home/jodfie/scan-processor/
├── incoming/          # Drop PDFs here
├── processing/        # Currently being processed
├── completed/         # Successfully processed (7-day retention)
├── failed/            # Failed processing (kept forever)
├── logs/              # Processing and cleanup logs
├── prompts/           # Claude Code prompts
│   ├── classifier.md
│   ├── medical.md
│   ├── expense.md
│   └── schoolwork.md
├── scripts/           # Processing scripts
│   ├── process.py     # Main processor (use with --dev)
│   ├── classifier.py  # Claude Code integration
│   ├── paperless.py   # Paperless API client
│   └── basicmemory.py # BasicMemory note creator
└── web/               # Web UI
    └── app.py         # Flask application
```

## Document Categories

| Category | Trigger | Paperless Tags | BasicMemory Note |
|----------|---------|----------------|------------------|
| **MEDICAL** | Doctor visits, prescriptions, medical bills | `medical`, `{child}` | ✓ Created in Medical/ |
| **CPS_EXPENSE** | Co-parenting expenses | `cps`, `expense`, `{child}` | ✓ Created in Expenses/ |
| **SCHOOLWORK** | School documents, report cards | `school`, `{child}` | ✗ Not created |
| **GENERAL** | Everything else | `general` | ✗ Not created |

## Web UI

- **URL**: https://scanui.redleif.dev
- **Pages**:
  - Dashboard - Recent activity and stats
  - Upload - Manual file upload
  - Pending - Documents needing clarification
  - Batch - Bulk processing
  - History - Processing history

## Quick Troubleshooting

### "Claude Code error: unknown option '--read'"
```bash
# Update command structure (already fixed in classifier.py)
# Uses: cat prompt.txt | claude --print --add-dir /path
```

### "attempt to write a readonly database"
```bash
cd /home/jodfie/scan-processor
rm queue/pending.db
python3 -c "
import sqlite3
with open('queue/schema.sql', 'r') as f:
    schema = f.read()
conn = sqlite3.connect('queue/pending.db')
conn.executescript(schema)
conn.close()
"
```

### "PAPERLESS_API_TOKEN not set"
```bash
# For dev mode: Not required
python3 scripts/process.py --dev document.pdf

# For production: Set in environment
source /home/jodfie/docker/.env
python3 scripts/process.py document.pdf
```

### Temp files accumulating
```bash
# Check for orphaned temp files
ls -lh /tmp/claude_prompt_*.txt

# Run cleanup
./scripts/cleanup_temp.sh
```

## Environment Variables

Required for **production mode** only:

```bash
PAPERLESS_URL=https://paperless.redleif.dev
PAPERLESS_API_TOKEN=<your-token>
PUSHOVER_USER=<your-user>
PUSHOVER_TOKEN=<your-token>
```

Not required for **development mode**.

## Testing Workflow

1. **Test in development mode first**:
   ```bash
   python3 scripts/process.py --dev incoming/test.pdf
   ```

2. **Verify the output**:
   - Check category classification
   - Verify metadata extraction
   - Review Paperless dry run output
   - Check BasicMemory note preview

3. **If looks good, run in production**:
   ```bash
   python3 scripts/process.py incoming/test.pdf
   ```

## Useful Logs

```bash
# Processing logs
tail -f logs/processor.log

# Classifier test logs
cat logs/classifier_test.log

# Dev mode test logs
cat logs/dev_mode_test.log

# Cleanup logs (after cron runs)
tail -f logs/cleanup.log

# Web UI logs
docker logs scan-processor-ui --tail 100 -f
```

## Cost Tracking

| Service | Cost |
|---------|------|
| Claude Code CLI | **$0** (uses Pro subscription) |
| Paperless-NGX | **$0** (self-hosted) |
| BasicMemory | **$0** (local files) |
| Cloudflare Tunnel | **$0** (free tier) |
| **Total** | **$0/month** |

## Support & Documentation

- Main README: `README.md`
- Claude Code Integration: `CLAUDE_CODE_INTEGRATION.md`
- Development Mode: `DEVELOPMENT_MODE.md`
- Cleanup & Retention: `CLEANUP_AND_RETENTION.md`
- Updates Log: `UPDATES.md`

## Example: Full Test Workflow

```bash
cd /home/jodfie/scan-processor

# 1. Verify Claude Code is working
./scripts/verify_claude_integration.sh

# 2. Test classifier on a document
./scripts/test_classifier.sh incoming/test-medical.pdf

# 3. Run in development mode
python3 scripts/process.py --dev incoming/test-medical.pdf

# 4. Review the output
cat logs/dev_mode_test.log

# 5. If everything looks good, run in production
source /home/jodfie/docker/.env
python3 scripts/process.py incoming/real-document.pdf

# 6. Check web UI
open https://scanui.redleif.dev/history
```

## Tips

💡 **Always test in dev mode first** - Prevents mistakes in production

💡 **Save dev mode logs** - Useful for debugging and reference

💡 **Check temp files** - Run cleanup script if `/tmp` fills up

💡 **Monitor disk space** - Failed docs are kept forever, review periodically

💡 **Use web UI** - Easier than command line for most operations

💡 **Database permissions** - If owned by root, recreate as jodfie user
