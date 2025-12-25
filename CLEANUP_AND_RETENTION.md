# Cleanup and Retention Policy

## Overview

The scan processor automatically manages temporary files and document retention to prevent disk space issues.

## Temporary Files

### Claude Code Prompt Files

**Location**: `/tmp/claude_prompt_*.txt`

**Lifecycle**:
1. Created when classifier calls Claude Code
2. Used once for processing
3. **Automatically deleted** immediately after use (via `finally` block)
4. Backup cleanup: Daily cron job removes files older than 1 hour

**Why temporary files?**
- Prompts are 3-4KB each
- Shell command length limits (~32KB on most systems)
- Using temp files avoids command length issues
- More reliable than `echo` for long prompts

### Cleanup Mechanism

```python
# In classifier.py
tmp_fd, tmp_path = tempfile.mkstemp(suffix='.txt', prefix='claude_prompt_')

try:
    # Use temp file...
    pass
finally:
    # ALWAYS clean up, even on error
    if os.path.exists(tmp_path):
        os.unlink(tmp_path)
```

## Document Retention

### Incoming Directory

**Location**: `/home/jodfie/scan-processor/incoming/`

**Retention**: Immediate (files moved to processing/)

**Purpose**: Drop zone for new documents

### Processing Directory

**Location**: `/home/jodfie/scan-processor/processing/`

**Retention**: Active only (moved when complete)

**Purpose**: Currently being processed

### Completed Directory

**Location**: `/home/jodfie/scan-processor/completed/`

**Retention**: **7 days**

**Purpose**: Successfully processed documents

**Auto-cleanup**: Daily cron job deletes files older than 7 days

**Why 7 days?**
- Gives you time to verify processing
- Can review via web UI history
- Original is in Paperless-NGX permanently
- BasicMemory notes are permanent

### Failed Directory

**Location**: `/home/jodfie/scan-processor/failed/`

**Retention**: **NEVER auto-deleted**

**Purpose**: Failed processing - needs manual review

**Manual cleanup**:
```bash
# Review failed documents in web UI first
# Then manually delete when resolved:
rm /home/jodfie/scan-processor/failed/old-file.pdf
```

**Why preserve forever?**
- Error information needed for debugging
- Web UI shows failed documents for review
- Manual intervention required anyway
- You decide when to delete

## Automated Cleanup

### Daily Cron Job

**Schedule**: 3:00 AM daily

**Script**: `/home/jodfie/scan-processor/scripts/cleanup_temp.sh`

**Actions**:
1. Remove temp files older than 1 hour (orphaned)
2. Remove completed documents older than 7 days
3. Report disk space usage
4. Log to `/home/jodfie/scan-processor/logs/cleanup.log`

### Install Cron Job

```bash
# Add to crontab
crontab -e

# Add this line:
0 3 * * * /home/jodfie/scan-processor/scripts/cleanup_temp.sh >> /home/jodfie/scan-processor/logs/cleanup.log 2>&1
```

### Manual Cleanup

```bash
# Run cleanup script manually
cd /home/jodfie/scan-processor
./scripts/cleanup_temp.sh
```

## Database Retention

### SQLite Database

**Location**: `/home/jodfie/scan-processor/queue/pending.db`

**Tables**:
- `pending_documents` - Documents awaiting clarification
- `processing_history` - All processed documents (forever)

**Retention**: Unlimited

**Why unlimited?**
- Database is small (few KB per document)
- History useful for analytics
- Web UI shows processing history
- Easy to query and filter

### Database Cleanup (if needed)

```bash
# If database grows too large, clean old history:
sqlite3 /home/jodfie/scan-processor/queue/pending.db <<EOF
DELETE FROM processing_history WHERE created_at < datetime('now', '-90 days');
VACUUM;
EOF
```

## Disk Space Monitoring

### Check Current Usage

```bash
# Quick check
./scripts/cleanup_temp.sh

# Detailed check
du -sh /home/jodfie/scan-processor/*/
```

### Expected Disk Usage

**Normal operation**:
- Temp files: ~0KB (cleaned immediately)
- Incoming: ~0-100MB (transient)
- Processing: ~0-50MB (active documents)
- Completed: ~0-500MB (7 days of docs)
- Failed: Varies (manual cleanup)
- Database: ~5-50MB (unlimited history)

**Total**: Usually < 1GB

### Alerts

Monitor via Uptime Kuma or add disk space check:

```bash
# Add to cron (alert if > 5GB)
USAGE=$(du -sm /home/jodfie/scan-processor | awk '{print $1}')
if [ $USAGE -gt 5000 ]; then
    echo "Warning: Scan processor using ${USAGE}MB" | mail -s "Disk Warning" you@example.com
fi
```

## Web UI Integration

### Failed Documents Display

The web UI shows failed documents with:
- Filename
- Error message (from processing_history table)
- Preview link
- Manual retry button
- Delete button (only in web UI)

### Completed Documents

7-day retention means:
- Documents visible in web UI for 7 days
- Links to Paperless-NGX work forever
- BasicMemory notes are permanent
- After 7 days: File deleted, history record remains

## File Recovery

### Recovering Deleted Files

Completed files deleted after 7 days can be recovered from:

1. **Paperless-NGX**: `https://paperless.redleif.dev`
   - Original document stored permanently
   - Download and re-process if needed

2. **BasicMemory**: For medical/expense documents
   - Notes stored in `/home/jodfie/Vault/jodys-brain/CoparentingSystem/`
   - Permanent storage

3. **Database**: Processing history
   - Query database for metadata
   - Even after file is deleted

## Best Practices

### 1. Regular Monitoring

```bash
# Weekly check
./scripts/cleanup_temp.sh

# Review failed documents
# Visit https://scanui.redleif.dev/history?status=failed
```

### 2. Verify Backups

Ensure backups include:
- `/home/jodfie/scan-processor/failed/` - Failed docs
- `/home/jodfie/scan-processor/queue/pending.db` - Database
- `/home/jodfie/Vault/jodys-brain/CoparentingSystem/` - Notes

### 3. Periodic Database Vacuum

```bash
# Monthly (or when database > 100MB)
sqlite3 /home/jodfie/scan-processor/queue/pending.db "VACUUM;"
```

### 4. Review Failed Documents

```bash
# List failed documents
ls -lh /home/jodfie/scan-processor/failed/

# Review errors in database
sqlite3 /home/jodfie/scan-processor/queue/pending.db \
  "SELECT filename, error_message FROM processing_history WHERE status='failed';"
```

## Cleanup Schedule Summary

| What | When | How | Why |
|------|------|-----|-----|
| Temp files | Immediately | Python `finally` block | Prevent buildup |
| Orphaned temps | Daily 3 AM | Cron job | Safety net |
| Completed docs | After 7 days | Cron job | Original in Paperless |
| Failed docs | Never | Manual only | Need review |
| Database | Never | Manual if needed | Small, useful |
| Logs | Rotate at 10MB | Built-in | Keep recent errors |

## Troubleshooting

### Temp files accumulating

```bash
# Check for orphaned temp files
ls -lh /tmp/claude_prompt_*.txt

# Clean up manually
rm /tmp/claude_prompt_*.txt

# Check classifier code has proper cleanup
grep -A5 "finally:" /home/jodfie/scan-processor/scripts/classifier.py
```

### Disk space full

```bash
# Find largest directories
du -sh /home/jodfie/scan-processor/*/ | sort -h

# Clean up completed files manually
find /home/jodfie/scan-processor/completed -name "*.pdf" -mtime +7 -delete

# Clean up old logs
find /home/jodfie/scan-processor/logs -name "*.log" -size +10M -delete
```

### Database too large

```bash
# Check database size
ls -lh /home/jodfie/scan-processor/queue/pending.db

# Clean old history (older than 90 days)
sqlite3 /home/jodfie/scan-processor/queue/pending.db <<EOF
DELETE FROM processing_history WHERE created_at < datetime('now', '-90 days');
VACUUM;
EOF
```

## Related Files

- `/home/jodfie/scan-processor/scripts/cleanup_temp.sh` - Cleanup script
- `/home/jodfie/scan-processor/scripts/classifier.py` - Temp file creation
- `/home/jodfie/scan-processor/config/config.yaml` - Retention settings
- `/tmp/scan-processor-cron.txt` - Cron job template
