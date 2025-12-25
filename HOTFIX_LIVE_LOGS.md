# Hotfix - Live Logs Docker Error

## Issue
Dashboard live logs showed error: `Error: [Errno 2] No such file or directory: 'docker'`

## Root Cause
The `/logs` endpoint was trying to execute `docker logs` command from **inside** the container to read its own logs. However, Docker CLI is not installed inside the `scan-processor-ui` container, causing the error.

## Problem Code
```python
# WRONG - This doesn't work inside container
import subprocess
result = subprocess.run(
    ['docker', 'logs', '--tail', str(lines), 'scan-processor-ui'],
    capture_output=True,
    text=True,
    timeout=5
)
```

## Solution
Updated `/logs` endpoint to use **available data sources** instead of Docker CLI:

### New Multi-Source Approach:

1. **Try log files first** (in order of preference):
   - `dev_mode_test.log` - Development mode tests
   - `classifier_test.log` - Classifier tests
   - `manual_test.log` - Manual tests

2. **Fall back to database** if no log files:
   - Query `processing_history` table
   - Format as log lines with timestamps, status, category
   - Show last N processing events

3. **Show helpful message** if no data available:
   - Tells user what logs will appear when
   - Suggests uploading a document

## Fixed Code
```python
@app.route('/logs')
def logs():
    """Live log viewer - shows recent processing activity"""
    lines = int(request.args.get('lines', 100))

    # Try log files first
    log_sources = [
        ('dev_mode_test.log', 'Development Mode Tests'),
        ('classifier_test.log', 'Classifier Tests'),
        ('manual_test.log', 'Manual Tests')
    ]

    for log_file, source_name in log_sources:
        log_path = LOGS_DIR / log_file
        if log_path.exists():
            # Read and return log lines
            ...
            return jsonify({
                'logs': log_lines,
                'source': source_name,
                'count': len(log_lines)
            })

    # Fall back to database processing history
    if not log_lines:
        cursor.execute("""
            SELECT created_at, filename, category, status,
                   processing_time_ms, error_message
            FROM processing_history
            ORDER BY created_at DESC
            LIMIT ?
        """, (lines,))

        # Format as log lines
        for row in cursor.fetchall():
            log_line = f"[{timestamp}] {status_icon} {filename} - {category} ({time})"
            ...

    # Show helpful message if nothing available
    return jsonify({
        'logs': ['No logs available yet', 'Upload a document to get started!'],
        'source': 'System Message'
    })
```

## Benefits

### Before (Broken):
- ❌ Required Docker CLI inside container
- ❌ Failed with "No such file or directory: 'docker'"
- ❌ No fallback if Docker not available
- ❌ Only tried one source (Docker logs)

### After (Fixed):
- ✅ Works with available data sources
- ✅ No external dependencies (Docker CLI)
- ✅ Multi-source fallback chain
- ✅ Shows processing history from database
- ✅ Helpful messages when no logs available
- ✅ Color-coded output on dashboard
- ✅ Auto-refresh every 5 seconds

## Tested Behavior

### Example Log Output:
```json
{
  "count": 20,
  "logs": [
    "✓ Moved to failed directory",
    "🔇 Skipping failure notification (dev mode)",
    "Traceback (most recent call last):",
    "  File \"/home/jodfie/scan-processor/scripts/process.py\", line 139",
    "sqlite3.OperationalError: attempt to write a readonly database"
  ],
  "source": "Development Mode Tests"
}
```

### When Processing History is Used:
```
Source: Processing History (Database)

[2025-12-20 20:45:00] ✓ Morgan_CarePlan.pdf - MEDICAL (44.4s)
[2025-12-20 20:30:15] ✓ Jacob_Referral.pdf - MEDICAL (38.2s)
[2025-12-20 20:15:30] ✗ Unknown_Doc.pdf - GENERAL (2.1s)
    ERROR: Classification confidence too low
```

### When No Logs Available:
```
Source: System Message

============================================================
No logs available yet

Logs will appear here when:
  • Documents are processed
  • Development mode tests are run
  • Classification tests are performed

Upload a document to get started!
============================================================
```

## Files Modified
- `web/app.py` - Lines 524-625 (Updated `/logs` endpoint)

## Testing
```bash
# Test logs endpoint
curl -s https://scanui.redleif.dev/logs?lines=20 | python3 -m json.tool

# Check dashboard
https://scanui.redleif.dev

# Verify auto-refresh works
# Wait 5 seconds, logs should update automatically
```

## Status
✅ **FIXED** - Dashboard live logs now working properly

- No more Docker CLI dependency
- Multi-source log reading
- Graceful fallbacks
- Auto-refresh working
- Color-coded output

## Related Issues
- This was discovered after implementing the dashboard live logs feature
- Original implementation assumed Docker CLI would be available
- Solution is more robust and doesn't require Docker-in-Docker

## Future Improvements
- Add real-time log streaming via WebSocket
- Add log filtering by severity (ERROR, WARNING, INFO)
- Add log search functionality
- Store Flask app logs to dedicated file for live monitoring

---

**Fixed**: December 20, 2025 22:09
**Version**: v1.1.1
**Priority**: High (Dashboard feature was broken)
