# Web UI Development Mode Toggle

## Quick Start

**Visit**: https://scanui.redleif.dev/upload

1. Check the **"🔧 Development Mode"** checkbox
2. Upload a PDF file
3. Watch real-time processing results appear immediately
4. See exactly what would be uploaded to Paperless and BasicMemory

![Dev Mode Toggle](web-ui-dev-mode-example.png)

## What You'll See

### Upload Interface

When you visit the upload page, you'll see:

```
📤 Scan Processor Upload

[Drag and drop area]

☐ 🔧 Development Mode
    Test without uploading to Paperless/BasicMemory
```

### Processing Results (Dev Mode Enabled)

After uploading with dev mode checked:

```
🔧 Processing Results (Development Mode)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ 20251220_Jacob_Medical.pdf                2:26 PM
    SUCCESS

    Category: MEDICAL
    Paperless ID: DRY_RUN_12345
    BasicMemory: /path/to/note.md
    Processing Time: 42.50s
```

## Features

### ✅ Automatic Processing

When dev mode is checked:
- File uploads immediately trigger processing
- No waiting for file watcher service
- Results appear in real-time

### ✅ Visual Feedback

The UI shows:
- **Upload progress** - Progress bar during upload
- **Processing status** - Real-time updates as document processes
- **Results panel** - Detailed results appear automatically
- **Category classification** - Shows MEDICAL, CPS_EXPENSE, SCHOOLWORK, or GENERAL
- **Dry run details** - Shows exactly what would be uploaded
- **Processing time** - See how long classification took

### ✅ Result Details

Each result shows:

**For Successful Processing**:
- ✅ Status icon
- 📋 Category with color-coded badge
- 🔢 Paperless document ID (DRY_RUN in dev mode)
- 📝 BasicMemory note path (if applicable)
- ⏱️ Processing time in seconds

**For Failed Processing**:
- ❌ Status icon
- 🚨 Error message
- 📋 Error details for debugging

### ✅ Multiple Documents

- Upload multiple files at once
- Results appear for each document
- Last 10 results are kept visible
- Easy to compare classification results

## Use Cases

### 1. Testing New Document Types

Upload a new type of document you haven't processed before:
- Check dev mode ✓
- Upload the PDF
- See how it's classified
- Verify metadata extraction
- Adjust prompts if needed

### 2. Validating Prompts

After modifying classification prompts:
- Check dev mode ✓
- Upload test documents
- Verify classification accuracy
- Compare results with previous versions

### 3. Debugging Issues

When a document isn't classifying correctly:
- Check dev mode ✓
- Upload the problematic document
- See detailed error messages
- Check extracted metadata
- Reference errors when fixing

### 4. Training Users

Show new users how the system works:
- Check dev mode ✓
- Upload sample documents
- Explain the classification process
- Show what metadata is extracted
- No risk of creating duplicate records

### 5. Batch Testing

Test multiple documents quickly:
- Check dev mode ✓
- Drag and drop multiple PDFs
- See all results in one view
- Verify batch processing logic

## Differences from Production Mode

| Feature | Dev Mode (Checkbox ✓) | Production Mode (Checkbox ☐) |
|---------|----------------------|----------------------------|
| **Processing** | Immediate | Via file watcher service |
| **Paperless Upload** | ✗ Simulated (DRY_RUN) | ✓ Real upload |
| **BasicMemory Notes** | ✗ Simulated (preview) | ✓ Real file creation |
| **Results Display** | ✓ Shown immediately | ⚠️ Background processing |
| **Notifications** | ✗ Skipped | ✓ Sent via Pushover |
| **Database Logging** | ✓ Logged | ✓ Logged |
| **Claude Classification** | ✓ Real | ✓ Real |
| **Metadata Extraction** | ✓ Real | ✓ Real |

## Example Workflow

### Testing a Medical Document

1. **Visit upload page**: https://scanui.redleif.dev/upload
2. **Check dev mode**: ☑️ Development Mode
3. **Upload**: `Jacob_Pediatrician_2025.pdf`
4. **Watch processing**:
   ```
   Upload complete - Processing in dev mode...
   ✓ Processing complete
   ```
5. **Review results**:
   ```
   ✅ Jacob_Pediatrician_2025.pdf
       Category: MEDICAL (98% confidence)
       Child: Jacob
       Provider: Pediatric Associates
       Date: 2025-01-09

       Would upload to Paperless:
       - Tags: medical, jacob
       - Document Type: Medical

       Would create BasicMemory note:
       - Path: Medical/20250109_Jacob_Pediatric-Associates.md
   ```
6. **If satisfied**: Uncheck dev mode and upload again for real

### Testing Multiple Document Types

1. Check dev mode ✓
2. Upload 5 different PDFs:
   - Medical bill
   - School report card
   - Co-parenting expense receipt
   - General correspondence
   - Another medical document
3. **See results for all 5**:
   ```
   ✅ Bill.pdf → MEDICAL
   ✅ Report.pdf → SCHOOLWORK
   ✅ Receipt.pdf → CPS_EXPENSE
   ✅ Letter.pdf → GENERAL
   ✅ Prescription.pdf → MEDICAL
   ```
4. Verify all classifications are correct
5. Process in production if happy with results

## Technical Implementation

### Frontend (upload.html + upload.js)

- Checkbox toggle for dev mode
- Automatic processing trigger after upload
- Results panel with expandable details
- Real-time status updates

### Backend (app.py)

- New `/api/process` endpoint
- Accepts `dev_mode` parameter
- Initializes `DocumentProcessor(dev_mode=True/False)`
- Returns processing results as JSON

### Integration

- Uses existing `DocumentProcessor` class
- Respects dev mode flag throughout pipeline
- Returns detailed results for display
- WebSocket events for real-time updates

## Benefits

✅ **User-Friendly** - No command line needed
✅ **Visual** - See results immediately
✅ **Safe** - Test without affecting production
✅ **Fast** - Immediate processing, no waiting
✅ **Informative** - Detailed dry run output
✅ **Mobile-Friendly** - Works on phones and tablets
✅ **Batch-Ready** - Test multiple documents at once

## Production Mode

To process documents for real (actually upload to Paperless):

1. **Uncheck** the Development Mode checkbox
2. Upload your PDF
3. File is saved to incoming directory
4. File watcher service processes it automatically
5. Check History page for results

Or use the command line:
```bash
python3 scripts/process.py /path/to/document.pdf
```

## Troubleshooting

### "DocumentProcessor not available"

**Problem**: Import error in Docker container

**Solution**: Container needs to be restarted
```bash
docker compose restart scan-processor-ui
```

### Results not appearing

**Problem**: Processing took longer than timeout

**Solution**: Check Docker logs
```bash
docker logs scan-processor-ui --tail 50
```

### Classification errors

**Problem**: Claude Code integration issue

**Solution**:
1. Check dev mode results for error details
2. Verify Claude Code is authenticated
3. Check prompts are correctly formatted

## Related Documentation

- `DEVELOPMENT_MODE.md` - Complete dev mode guide
- `QUICK_REFERENCE.md` - Command quick reference
- `README.md` - Main system documentation

## Summary

The **Web UI Development Mode Toggle** makes testing easy:

1. ✓ **Check the checkbox**
2. 📤 **Upload your PDF**
3. 👁️ **See results immediately**
4. 🎯 **No production impact**

Perfect for testing, debugging, and validating document processing without affecting your production Paperless and BasicMemory systems!
