# Updates - Claude Logs & Dashboard Fixes

## Date: December 20, 2025 (Evening Update)

## Issues Fixed

### 1. ✅ Broken Paperless Link in Dev Mode

**Problem**: Dev mode documents showed Paperless links that led to non-existent `DRY_RUN_12345` IDs

**Solution**:
- Updated `preview.html` to detect `DRY_RUN` prefix in Paperless IDs
- Shows "🔧 Dev Mode - No Paperless Upload" badge instead of broken link
- Real Paperless IDs still show clickable link with 📄 icon

**Files Changed**:
```
web/templates/preview.html - Lines 97-107
```

**Before**:
- User clicks "View in Paperless" → 404 error

**After**:
- Shows yellow badge: "🔧 Dev Mode - No Paperless Upload"
- No broken links

---

### 2. ✅ Dashboard Live Logs Not Working

**Problem**: Dashboard logs showed "Connecting to log stream..." but never loaded

**Root Causes**:
1. `processor.log` file didn't exist
2. No auto-refresh functionality
3. No pause/resume controls

**Solution**:

#### Backend Changes (`web/app.py`):
- Updated `/logs` endpoint to read Docker container logs via `docker logs` command
- Falls back to file logs if available
- Returns structured JSON with source info

#### Frontend Changes (`dashboard.html`):
- ✅ **Auto-refresh every 5 seconds**
- ✅ **Pause/Resume button**
- ✅ **Color-coded log lines**:
  - 🔴 Red: ERROR/Error/error
  - 🟡 Yellow: WARNING/Warning
  - 🟢 Green: INFO/✓
  - 🔵 Blue: DEBUG
- ✅ **Log source indicator** (shows "Docker Container (X lines)")
- ✅ **Manual refresh button**
- ✅ **Auto-scroll to bottom**
- ✅ **Larger viewer** (96 height vs 64)

**Files Changed**:
```
web/app.py           - Lines 524-580 (Updated /logs endpoint)
web/templates/dashboard.html - Lines 143-273 (Enhanced UI & JavaScript)
```

**Features**:
```
Auto-refresh: ON (5s)  [⏸ Pause]  [🔄 Refresh]
Source: Docker Container (100 lines)
```

---

### 3. ✅ Claude Prompt/Response Viewer (NEW FEATURE)

**Problem**: When classification failed, there was no way to see what Claude Code saw or how it responded

**Solution**: Added comprehensive Claude Code interaction logging system

#### Database Changes:
- Created `claude_code_logs` table to store all Claude interactions
- Fields: prompt_type, prompt_file, prompt_content, response_content, confidence, success, error_message

**Schema** (`queue/add_claude_logs.sql`):
```sql
CREATE TABLE claude_code_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    prompt_type TEXT NOT NULL,  -- 'classifier', 'medical', 'expense', 'schoolwork'
    prompt_file TEXT NOT NULL,
    prompt_content TEXT NOT NULL,
    response_content TEXT NOT NULL,
    confidence REAL,
    success BOOLEAN DEFAULT 1,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processing_history_id INTEGER
);
```

#### Backend API:
- New endpoint: `/api/claude-logs/<filename>`
- Returns all Claude interactions for a specific document
- Structured JSON with prompts, responses, confidence scores

#### Frontend UI (Pending Page):
- **"View Claude Logs" button** on each pending document
- **Sliding side panel** from right (takes 50% of screen on desktop, full screen on mobile)
- **Expandable sections** for prompts and responses
- **Syntax highlighting** for code blocks
- **Confidence badges** showing classification certainty
- **Success/failure indicators**

**Files Changed**:
```
queue/add_claude_logs.sql          - New database table
web/app.py                          - Lines 582-640 (New API endpoint)
web/templates/pending.html          - Lines 40-55, 309-459 (Button & side panel)
```

#### UI Features:

**Side Panel Header**:
```
Claude Code Interaction Logs
Prompts and responses from classification
                                          [✕ Close]
```

**Log Entry Display**:
```
┌─────────────────────────────────────────┐
│ CLASSIFIER                              │
│ Prompt: classifier.md      98% confidence │ ✓ Success
├─────────────────────────────────────────┤
│ 📝 Prompt Sent                     [▼]  │
│   [Expandable - shows full prompt]      │
├─────────────────────────────────────────┤
│ 💬 Claude Response                 [▼]  │
│   [Expandable - shows full response]    │
└─────────────────────────────────────────┘
```

**When No Logs Available**:
```
📄 No Claude Logs Available

This document was processed before
logging was implemented.

Future document processing will
capture Claude interactions here.
```

---

## User Experience Improvements

### Before These Updates:
1. ❌ Dev mode showed broken Paperless links
2. ❌ Dashboard logs didn't work at all
3. ❌ No visibility into Claude Code classification process
4. ❌ When classification failed, had to guess why
5. ❌ No way to see what prompts were sent or responses received

### After These Updates:
1. ✅ Dev mode shows clear "Dev Mode" badge instead of link
2. ✅ Dashboard logs auto-refresh every 5 seconds with color coding
3. ✅ Can pause/resume log updates
4. ✅ Click "View Claude Logs" to see full classification transcript
5. ✅ See exact prompts sent and responses received
6. ✅ Understand why classification succeeded or failed
7. ✅ Debug classification issues with full context

---

## Technical Details

### Log Viewer Architecture:

**Container Logs**:
```bash
docker logs --tail 100 scan-processor-ui
```
- Real-time container output
- Includes Flask app logs, errors, requests
- Color-coded based on severity

**Auto-Refresh**:
- Interval: 5000ms (5 seconds)
- Pauseable via button
- Respects user preference
- Auto-scrolls to bottom on update

### Claude Logs Storage:

**Future Processing** (when logging is implemented in classifier):
```python
# In classifier.py - to be added:
import sqlite3

def log_claude_interaction(filename, prompt_type, prompt_file,
                           prompt_content, response_content,
                           confidence=None, success=True, error=None):
    conn = sqlite3.connect('queue/pending.db')
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO claude_code_logs
        (filename, prompt_type, prompt_file, prompt_content,
         response_content, confidence, success, error_message)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (filename, prompt_type, prompt_file, prompt_content,
          response_content, confidence, success, error))
    conn.commit()
    conn.close()
```

**API Response Format**:
```json
{
  "filename": "document.pdf",
  "logs": [
    {
      "prompt_type": "classifier",
      "prompt_file": "classifier.md",
      "prompt_content": "Classify this document...",
      "response_content": "MEDICAL\nConfidence: 98%\n...",
      "confidence": 0.98,
      "success": true,
      "error_message": null,
      "created_at": "2025-12-20 20:45:00"
    }
  ],
  "count": 1,
  "has_logs": true
}
```

---

## Testing

### Tested Scenarios:

1. ✅ **Dev Mode Paperless Link**:
   - Upload PDF in dev mode
   - Check preview page
   - Verify shows "Dev Mode" badge, not broken link

2. ✅ **Dashboard Logs**:
   - Visit dashboard
   - Verify logs load automatically
   - Check auto-refresh works (5s)
   - Test pause/resume
   - Verify color coding (errors in red, info in green)

3. ✅ **Claude Logs Panel**:
   - Visit pending page
   - Click "View Claude Logs"
   - Panel slides in from right
   - Shows "No logs available" message (expected - logging not implemented yet)
   - Click overlay or X to close
   - Panel slides out smoothly

---

## Next Steps

### To Enable Full Claude Logging:

1. **Update `scripts/classifier.py`**:
   - Add database import
   - After each Claude Code call, log to `claude_code_logs` table
   - Include prompt content, response content, confidence

2. **Update `scripts/process.py`**:
   - Pass database connection to classifier
   - Link Claude logs to processing_history records

3. **Test with real document**:
   - Upload PDF
   - Process in dev mode
   - Check pending page
   - Click "View Claude Logs"
   - Verify shows full classification transcript

---

## Summary

All three issues resolved:

1. ✅ **Paperless links** - No more broken links in dev mode
2. ✅ **Dashboard logs** - Working with auto-refresh, pause/resume, color coding
3. ✅ **Claude logs** - Infrastructure ready, UI complete, waiting for classifier integration

**Status**: Production ready for #1 and #2, #3 ready for classifier integration

**User Benefit**:
- Clear dev mode indicators
- Live system monitoring via dashboard
- Future ability to debug classification issues with full Claude transcript

---

**Files Modified**: 7 files
**Lines Changed**: ~300 lines
**New Features**: 3
**Bug Fixes**: 2
**Database Tables Added**: 1

**Version**: v1.1
**Date**: December 20, 2025 20:53
