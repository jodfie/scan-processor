# Development Mode Guide

## Overview

Development mode allows you to test the scan processor **without actually uploading to Paperless or creating BasicMemory notes**. This is essential for:

- Testing document classification
- Verifying metadata extraction
- Debugging errors with verbose output
- Safe testing without affecting production systems

## Usage

### Web UI (Recommended)

1. Go to **https://scanui.redleif.dev/upload**
2. **Check the "🔧 Development Mode" checkbox**
3. Upload your PDF file
4. The file will be automatically processed in dev mode
5. **Results appear immediately** showing:
   - Classification category
   - Extracted metadata
   - What would be uploaded to Paperless (dry run)
   - What BasicMemory note would be created (dry run)
   - Processing time

**Benefits of Web UI**:
- ✅ Visual feedback in real-time
- ✅ No command line needed
- ✅ See results immediately
- ✅ Easy to compare multiple documents
- ✅ Works on mobile devices

### Command Line

```bash
python3 scripts/process.py --dev <file_path>
```

Or use the long form:

```bash
python3 scripts/process.py --dry-run <file_path>
```

### Example

```bash
cd /home/jodfie/scan-processor
python3 scripts/process.py --dev incoming/test-document.pdf
```

## What Development Mode Does

### ✅ Performs These Actions:

1. **Document Classification** - Uses Claude Code to classify the document
2. **Metadata Extraction** - Extracts detailed metadata based on category
3. **Workflow Simulation** - Shows exactly what would be uploaded
4. **Verbose Error Logging** - Displays full stack traces for debugging
5. **Database Logging** - Records processing history

### ❌ Skips These Actions:

1. **Paperless Upload** - Shows what would be uploaded, but doesn't send API request
2. **BasicMemory Note Creation** - Shows what note would be created, but doesn't write file
3. **Push Notifications** - Skips sending Pushover notifications

## Sample Output

```
============================================================
🔧 DEVELOPMENT MODE ENABLED
============================================================
⚠️  No actual uploads will be performed
⚠️  Paperless: DRY RUN
⚠️  BasicMemory: DRY RUN
⚠️  Verbose error logging enabled
============================================================

============================================================
Processing: test-medical-document.pdf
============================================================

[1/5] Classifying document...
✓ Category: MEDICAL (confidence: 95.00%)

[2/5] Extracting MEDICAL metadata...
✓ Metadata extracted
  Child: Jacob
  Provider: Pediatric Associates

[3/5] Uploading to Paperless...

============================================================
🔧 PAPERLESS DRY RUN - Would upload with:
============================================================
  File: test-medical-document.pdf
  Title: test-medical-document
  Tags: ['medical', 'jacob']
  Document Type: Medical
  Correspondent: None
  Created Date: 2025-01-09
  URL: https://paperless.redleif.dev/api/documents/post_document/
============================================================

✓ Uploaded to Paperless (ID: DRY_RUN_12345)

[4/5] Creating BasicMemory note...

============================================================
🔧 BASICMEMORY DRY RUN - Would create medical note:
============================================================
  Path: /home/jodfie/Vault/jodys-brain/CoparentingSystem/Medical/20250109_Jacob_Pediatric-Associates.md
  Filename: 20250109_Jacob_Pediatric-Associates.md

  Metadata:
    child: Jacob
    date: 2025-01-09
    provider: Pediatric Associates
    type: Well Child Visit

  Content preview (first 500 chars):
  ---
  date: 2025-01-09
  child: Jacob
  provider: Pediatric Associates
  type: Well Child Visit
  ...
============================================================

✓ BasicMemory note created: /path/to/note.md

[5/5] Sending notification...
🔇 Skipping failure notification (dev mode)

✓ Processing completed in 42.98s
```

## Verbose Error Logging

When an error occurs in development mode, you get detailed debugging information:

```
✗ ERROR: PAPERLESS_API_TOKEN environment variable not set

============================================================
📋 VERBOSE ERROR DETAILS (Development Mode)
============================================================
Error Type: ValueError
Error Message: PAPERLESS_API_TOKEN environment variable not set

Full Traceback:
Traceback (most recent call last):
  File "/home/jodfie/scan-processor/scripts/process.py", line 38, in __init__
    self.paperless = PaperlessClient()
  File "/home/jodfie/scan-processor/scripts/paperless.py", line 20, in __init__
    raise ValueError("PAPERLESS_API_TOKEN environment variable not set")
ValueError: PAPERLESS_API_TOKEN environment variable not set
============================================================
```

This makes it easy to:
- Identify the exact error type
- See the full stack trace
- Find the specific line causing the issue
- Reference the error when asking for help

## Common Use Cases

### 1. Testing New Document Types

```bash
# Test how the classifier handles a new type of document
python3 scripts/process.py --dev incoming/unknown-document.pdf
```

### 2. Verifying Metadata Extraction

```bash
# Check if Claude Code extracts the correct metadata
python3 scripts/process.py --dev incoming/medical-bill.pdf
```

Look for the "Metadata extracted" section to verify:
- Child name is correct
- Date is extracted properly
- Provider/vendor information is accurate

### 3. Debugging Errors

```bash
# Get full error details when something fails
python3 scripts/process.py --dev failing-document.pdf
```

The verbose error output will show:
- Exact error type
- Full stack trace
- File and line number
- All context needed to fix the issue

### 4. Testing Classifier Prompts

After modifying prompts in `prompts/`:

```bash
# Test updated classifier prompt
python3 scripts/process.py --dev test-document.pdf
```

Check the classification output to verify your prompt changes work correctly.

### 5. Validating Workflow Before Production

```bash
# Process a batch of test documents
for file in incoming/test-*.pdf; do
    python3 scripts/process.py --dev "$file"
done
```

## Differences from Production Mode

| Feature | Development Mode | Production Mode |
|---------|-----------------|----------------|
| Claude Code Classification | ✓ Real | ✓ Real |
| Metadata Extraction | ✓ Real | ✓ Real |
| Paperless Upload | ✗ Simulated | ✓ Real |
| BasicMemory Notes | ✗ Simulated | ✓ Real |
| Push Notifications | ✗ Skipped | ✓ Real |
| Error Details | ✓ Verbose | ⚠️ Basic |
| Database Logging | ✓ Logged | ✓ Logged |

## Environment Requirements

Development mode works **without** these environment variables:

- `PAPERLESS_API_TOKEN` - Optional (skipped in dry run)
- `PUSHOVER_USER` - Optional (notifications skipped)
- `PUSHOVER_TOKEN` - Optional (notifications skipped)

You **still need**:

- Claude Code CLI installed and authenticated
- Prompts directory with all prompt files
- Database directory (for history logging)

## Tips for Effective Testing

### 1. Save Dev Mode Logs

```bash
python3 scripts/process.py --dev test.pdf 2>&1 | tee logs/dev-test-$(date +%Y%m%d-%H%M%S).log
```

### 2. Test Edge Cases

- Documents with unclear categories
- PDFs with poor OCR quality
- Mixed-content documents
- Foreign language documents

### 3. Verify All Metadata Fields

Check the dry run output to ensure:
- Child names are detected correctly
- Dates are in YYYY-MM-DD format
- Provider/vendor names are clean
- Costs/amounts are extracted properly

### 4. Compare with Production

Run the same document in dev mode first:

```bash
# Development test
python3 scripts/process.py --dev test.pdf

# If it looks good, run in production
python3 scripts/process.py test.pdf
```

## Troubleshooting

### "attempt to write a readonly database"

**Problem**: Database file is owned by root (from Docker container)

**Solution**:
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

### "Medical template not found"

**Problem**: BasicMemory templates don't exist in the CPS directory

**Impact**: In dev mode, this only shows a warning and doesn't affect testing

**Solution** (if needed):
- Create templates in `/home/jodfie/Vault/jodys-brain/CoparentingSystem/Medical/`
- Or use the existing templates from the CPS project

### Claude Code Authentication Errors

**Problem**: `error: unknown option '--read'` or authentication failures

**Solution**:
```bash
# Check Claude Code version
claude --version

# Re-authenticate if needed
claude auth login
```

## Production Mode

To run in **production mode** (actually upload to Paperless and create notes):

```bash
# No --dev flag
python3 scripts/process.py <file_path>
```

Or use the file watcher service to automatically process new files.

## Best Practices

1. **Always test in dev mode first** when:
   - Testing new prompts
   - Processing unfamiliar document types
   - Debugging issues
   - Validating metadata extraction

2. **Check the dry run output** before production:
   - Verify tags are correct
   - Check document type assignment
   - Validate extracted dates and names
   - Review BasicMemory note content

3. **Save logs for reference**:
   - Keep successful dev runs for comparison
   - Save error logs for troubleshooting
   - Document edge cases and solutions

4. **Use production mode sparingly**:
   - Only after verifying in dev mode
   - When you're confident in the classification
   - For actual document processing workflows

## Related Files

- `scripts/process.py` - Main processor with --dev flag
- `scripts/paperless.py` - Paperless client with dry_run mode
- `scripts/basicmemory.py` - BasicMemory creator with dry_run mode
- `logs/dev_mode_test.log` - Example dev mode output

## Summary

Development mode is your **safe testing environment** that:

✅ Shows exactly what would happen
✅ Provides detailed error information
✅ Doesn't modify production systems
✅ Helps debug issues quickly
✅ Validates classification and metadata

Always test in development mode before running production workflows!
