# Paperless iOS App → Scanner UI Workflow

**NEW**: Documents uploaded via Paperless iOS app are now automatically processed through Scanner UI's Claude Code workflow and updated with intelligent metadata.

## How It Works

```
Paperless iOS App → Paperless NGX
    ↓ (post-consume hook triggers)
Download PDF & POST to scanui.redleif.dev/api/upload
    ↓
Scanner UI Claude Code processing
    ↓ (Classification + Metadata Extraction)
UPDATE existing Paperless document (not create new)
    ↓
BasicMemory note created (if medical/expense)
    ↓
Pushover notification sent
```

## Key Features

✅ **No Duplicates** - Updates existing Paperless document instead of creating new one
✅ **Full Claude Processing** - Same classification & metadata extraction as scan-processor
✅ **Merged Tags** - New Claude-extracted tags are merged with existing tags
✅ **BasicMemory Integration** - Medical & expense documents still create notes
✅ **Automatic** - Happens in background after iOS app upload

## Architecture

### 1. Paperless Post-Consume Hook
**Location**: `/home/jodfie/docker/paperless-ngx/hooks/post-consume.d/20-scanner-ui.sh`

- Triggered automatically when Paperless finishes consuming a document
- Downloads the PDF from Paperless API
- POSTs to Scanner UI with `paperless_id` parameter
- Cleans up temporary file

### 2. Scanner UI Web Endpoint
**Endpoint**: `https://scanui.redleif.dev/api/upload`

**Parameters**:
- `file` - PDF file (multipart/form-data)
- `paperless_id` - Existing Paperless document ID (triggers UPDATE mode)
- `source` - Upload source (e.g., "paperless-app")

**Behavior**:
- When `paperless_id` is provided, processes immediately (doesn't wait for file watcher)
- Uses UPDATE mode instead of creating new document

### 3. DocumentProcessor UPDATE Mode
**Location**: `/home/jodfie/scan-processor/scripts/process.py`

**New Parameter**: `paperless_id`

**Changes**:
- When `paperless_id` provided, calls `paperless.update_document()` instead of `upload_document()`
- Updates existing document's tags, title, document type, and created date
- Merges new tags with existing tags (doesn't replace)
- Still creates BasicMemory notes for MEDICAL and CPS_EXPENSE
- Still sends notifications

### 4. PaperlessClient Update Method
**Location**: `/home/jodfie/scan-processor/scripts/paperless.py`

**New Method**: `update_document(document_id, ...)`

- Uses PATCH request to `/api/documents/{id}/`
- Fetches current document first
- Merges new tags with existing tags
- Updates only provided fields

## Usage

### Via Paperless iOS App (Automatic)

1. Open Paperless Mobile app
2. Scan/upload document
3. Wait 5-10 seconds for Paperless to consume
4. **Post-consume hook automatically triggers**
5. Document is downloaded and sent to Scanner UI
6. Claude processes and updates the document
7. You receive Pushover notification with results

### Via Command Line (Manual Testing)

```bash
# Test UPDATE mode with existing Paperless document
cd /home/jodfie/scan-processor

# Update document ID 123
python3 scripts/process.py completed/test.pdf --paperless-id 123

# Test in dev mode (no actual updates)
python3 scripts/process.py completed/test.pdf --paperless-id 123 --dev
```

### Via Web Upload (Manual)

```bash
# Upload with paperless_id to trigger UPDATE mode
curl -X POST https://scanui.redleif.dev/api/upload \
  -F "file=@document.pdf" \
  -F "paperless_id=123" \
  -F "source=manual"
```

## Comparison: Two Upload Paths

| Aspect | Scanner UI Direct | Paperless iOS App |
|--------|-------------------|-------------------|
| **Upload To** | scanui.redleif.dev | Paperless Mobile App |
| **Processing** | Automatic via file watcher | Automatic via post-consume hook |
| **Paperless** | New document created | Existing document updated |
| **Tags** | Claude tags only | Claude tags merged with existing |
| **BasicMemory** | ✅ Created | ✅ Created |
| **Notification** | ✅ Sent | ✅ Sent |
| **Best For** | Physical scanner → QNAP | iPhone/iPad scanning |

## Benefits of Paperless App Path

1. **Native iOS Experience** - Use Paperless Mobile app's great scanner interface
2. **No Duplicate Upload** - Document already in Paperless, just enhances metadata
3. **Tag Preservation** - Keeps any tags you manually added before processing
4. **OCR Already Done** - Paperless does OCR during consumption
5. **Offline Capable** - Can queue uploads in Paperless app when offline

## Environment Variables (Hook)

The post-consume hook uses these variables (configured in Docker `.env`):

```bash
PAPERLESS_URL=https://paperless.redleif.dev
PAPERLESS_API_TOKEN=8000e5da56b51a607233c901672538798531968a
SCANNER_UI_URL=https://scanui.redleif.dev
```

## Troubleshooting

### Hook Not Triggering

```bash
# Check post-consume hook is executable
ls -la /home/jodfie/docker/paperless-ngx/hooks/post-consume.d/20-scanner-ui.sh

# Should show: -rwxrwxr-x

# Check hook logs
docker exec paperless-ngx tail -f /tmp/post-consume.log

# Test hook manually
docker exec paperless-ngx sh -c "DOCUMENT_ID=123 /hooks/post-consume.d/20-scanner-ui.sh"
```

### Document Not Being Updated

```bash
# Check Scanner UI logs
docker logs -f scan-processor-ui

# Check processing history database
sqlite3 /home/jodfie/scan-processor/queue/pending.db \
  "SELECT filename, category, status, paperless_id FROM processing_history ORDER BY created_at DESC LIMIT 5"

# Test update manually
curl -H "Authorization: Token 8000e5da56b51a607233c901672538798531968a" \
  https://paperless.redleif.dev/api/documents/123/
```

### Missing BasicMemory Notes

Check that the document was classified as MEDICAL or CPS_EXPENSE:

```bash
# View last classification
sqlite3 /home/jodfie/scan-processor/queue/pending.db \
  "SELECT filename, category, classification_response FROM processing_history ORDER BY created_at DESC LIMIT 1"
```

## Database Changes

The `processing_history` table includes a new optional field:

- `paperless_id` - If provided during processing, indicates UPDATE mode was used

## Restart Required

After setting up the hook, restart Paperless to ensure it picks up the new script:

```bash
cd /home/jodfie/docker
docker-compose restart paperless-ngx
```

## Future Enhancements

- [ ] Webhook validation/authentication
- [ ] Rate limiting for hook endpoint
- [ ] Retry logic if Scanner UI is unavailable
- [ ] Web UI indicator showing "updated via iOS app"
- [ ] Statistics on iOS app vs scanner uploads

## Related Documentation

- **Main Workflow**: `README.md`
- **iOS Shortcuts**: `IOS_SHORTCUTS_INTEGRATION.md`
- **Upload Comparison**: `UPLOAD_WORKFLOW_COMPARISON.md`
- **TechKB**: `/home/jodfie/vault/jodys-brain/TechKB/10-projects/14-scan-processor/`
